"""Analytik — původní články, které umí napsat jen ten, kdo má paměť.

Dělá tři věci:

1) ANALYTICKÉ ZADÁNÍ
   Z dlouhodobé paměti vytáhne, co se v běžících tématech změnilo,
   co se opakuje, kde si zdroje odporují a o čem se přestalo mluvit.
   Z toho vzniká zadání pro původní analýzy — obsah, který nikdo jiný
   napsat nemůže, protože nemá záznam.

2) VEŘEJNÝ ZÁZNAM PŘEDPOVĚDÍ
   Místo mlhavých "experti očekávají" vydáváme konkrétní tvrzení
   s pravděpodobností a datem, do kdy se to rozhodne. Po termínu si
   sami spočítáme, jak jsme dopadli, a necháme to na webu i když to
   dopadlo špatně. Tohle nedělá skoro nikdo a je to největší možný
   doklad, že to s poctivostí myslíme vážně.

3) VYHODNOCENÍ
   Splatné předpovědi se porovnají se skutečností a spočítá se
   Brierovo skóre (0 = dokonalé, 0,25 = jako hod mincí, 1 = úplně mimo).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys

from . import ai, config, memory

FORECASTS = config.DATA / "forecasts.json"
BRIEF = config.DATA / "memory" / "analyst-brief.md"


# ------------------------------------------------------- analytické zadání
def _contradictions(thread: dict) -> list:
    """Hrubé hledání míst, kde se vyprávění obrací."""
    flips, prev = [], None
    signals = [("deny", "denies denied rejects rejected dismissed"),
               ("confirm", "confirms confirmed admits admitted acknowledged"),
               ("halt", "halts halted suspended cancelled paused withdraw"),
               ("resume", "resumes resumed restarts restored reopened agreed")]
    for e in thread["timeline"]:
        low = e["headline"].lower()
        tag = next((name for name, words in signals if any(w in low for w in words.split())), None)
        if tag and prev and tag != prev[0]:
            flips.append(f"{prev[1]} → {e['date']}: „{e['headline'][:90]}“")
        if tag:
            prev = (tag, e["date"])
    return flips[-3:]


def build_brief() -> dict:
    mem = memory.load()
    act = memory.active(days=14, min_entries=2)
    dorm = memory.dormant()
    today = config.today()

    L = [f"# ANALYTICKÉ ZADÁNÍ — {today}", "",
         f"Paměť obsahuje **{len(mem['threads'])} vláken**. "
         f"Aktivních za posledních 14 dní: **{len(act)}**.", "",
         "---", "", "## A) BĚŽÍCÍ TÉMATA (materiál pro analýzy)", ""]

    picks = []
    for t in act[:6]:
        span = (dt.date.fromisoformat(t["last_seen"]) - dt.date.fromisoformat(t["first_seen"])).days
        L += [f"### {t['title']}",
              f"- rubrika `{t['section']}` · sledováno {span} dní · {len(t['timeline'])} záznamů",
              "- časová osa:"]
        for e in t["timeline"][-10:]:
            L.append(f"  - **{e['date']}** ({e['sources']} zdrojů) {e['headline']}")
        flips = _contradictions(t)
        if flips:
            L.append("- ⚠️ vyprávění se v čase obrátilo:")
            L += [f"  - {f}" for f in flips]
        L.append("")
        picks.append(t)

    if dorm:
        L += ["---", "", "## B) TÉMATA, O KTERÝCH SE PŘESTALO MLUVIT", "",
              "_Často zajímavější než ta hlasitá. Co se s tím stalo? Vyřešilo se to, "
              "nebo jen zmizelo z pozornosti?_", ""]
        for t in dorm[:6]:
            L.append(f"- **{t['title']}** — naposledy {t['last_seen']}, "
                     f"celkem {len(t['timeline'])} záznamů")
        L.append("")

    fc = load_forecasts()
    open_fc = [f for f in fc["forecasts"] if f["status"] == "open"]
    due = [f for f in open_fc if f["resolve_by"] <= today]
    if open_fc:
        L += ["---", "", "## C) OTEVŘENÉ PŘEDPOVĚDI", ""]
        for f in open_fc[:12]:
            mark = " ⏰ **SPLATNÁ, ROZHODNI**" if f in due else ""
            L.append(f"- `{f['id']}` **{int(f['probability'] * 100)} %** — {f['question']} "
                     f"(do {f['resolve_by']}){mark}")
        L.append("")

    score = scoreboard()
    if score["resolved"]:
        L += [f"_Dosavadní úspěšnost: {score['resolved']} vyhodnocených předpovědí, "
              f"Brierovo skóre {score['brier']:.3f} "
              f"({score['verdict_cs']})._", ""]

    BRIEF.parent.mkdir(parents=True, exist_ok=True)
    BRIEF.write_text("\n".join(L), encoding="utf-8")
    config.log(f"Analytické zadání hotovo: {len(picks)} běžících témat, "
               f"{len(dorm)} utichlých, {len(due)} splatných předpovědí.")
    return {"threads": picks, "dormant": dorm[:6], "due": due}


# --------------------------------------------------------------- předpovědi
def load_forecasts() -> dict:
    if not FORECASTS.exists():
        return {"forecasts": []}
    return json.loads(FORECASTS.read_text(encoding="utf-8"))


def save_forecasts(data: dict) -> None:
    FORECASTS.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def scoreboard() -> dict:
    data = load_forecasts()
    done = [f for f in data["forecasts"] if f["status"] == "resolved" and f.get("brier") is not None]
    if not done:
        return {"resolved": 0, "brier": 0.0, "verdict": "none", "verdict_cs": "zatím nevyhodnoceno"}
    brier = sum(f["brier"] for f in done) / len(done)
    key = ("strong" if brier < 0.15 else "good" if brier < 0.25
           else "chance" if brier < 0.30 else "poor")
    cs = {"strong": "výrazně lepší než náhoda", "good": "lepší než hod mincí",
          "chance": "na úrovni náhody", "poor": "horší než náhoda"}[key]
    return {"resolved": len(done), "brier": brier, "verdict": key, "verdict_cs": cs}


PROPOSE = """Jsi analytik The Deeper Story. Dostaneš časové osy běžících témat.

Navrhni 2 až 3 KONKRÉTNÍ, OVĚŘITELNÉ předpovědi. Každá musí splňovat:
- dá se po termínu jednoznačně rozhodnout ANO/NE z veřejných zpráv
- termín je 14 až 120 dní od dneška
- není triviální (ne "bude se dál jednat") ani nemožná
- není o smrti, nemoci ani soukromí konkrétních osob
- není o výsledcích voleb v zemi, kde by to mohlo být bráno jako ovlivňování

Ke každé uveď poctivou pravděpodobnost. Nezaokrouhluj na 50 %, to je alibismus.
Když si myslíš 70, napiš 70. Budeme z toho počítat skóre a bude to veřejné.

Vrať JSON:
{"forecasts": [{"question": "...", "probability": 0.0-1.0,
  "resolve_by": "RRRR-MM-DD", "resolution_criteria": "podle čeho se to pozná",
  "reasoning": "dvě až tři věty, proč právě tahle pravděpodobnost"}]}"""

RESOLVE = """Jsi analytik The Deeper Story. Dostaneš předpověď, jejíž termín uplynul,
a záznam událostí k danému tématu.

Rozhodni poctivě, jestli se to stalo. Když z podkladů nejde rozhodnout,
napiš "unclear" — raději předpověď zrušíme, než abychom si ji přibarvili.

Vrať JSON:
{"outcome": "yes" | "no" | "unclear", "explanation": "jedna až dvě věty"}"""


def propose(limit: int = 3) -> int:
    act = memory.active(days=14, min_entries=2)[:5]
    if not act:
        config.log("Málo materiálu na předpovědi.")
        return 0
    payload = "\n\n".join(memory.describe(t) for t in act)
    payload += f"\n\nDNEŠNÍ DATUM: {config.today()}"
    try:
        out = ai.ask_json(PROPOSE, payload, max_tokens=2500, temperature=0.3)
    except Exception as e:  # noqa: BLE001
        config.log(f"Předpovědi se nepodařilo vytvořit: {str(e)[:140]}")
        return 0

    data = load_forecasts()
    existing = {f["question"].lower() for f in data["forecasts"]}
    added = 0
    for f in out.get("forecasts", [])[:limit]:
        q = str(f.get("question", "")).strip()
        if not q or q.lower() in existing:
            continue
        try:
            p = max(0.02, min(0.98, float(f["probability"])))
            dt.date.fromisoformat(f["resolve_by"])
        except Exception:  # noqa: BLE001
            continue
        data["forecasts"].append({
            "id": hashlib.sha1(q.encode()).hexdigest()[:8],
            "question": q,
            "probability": round(p, 2),
            "created": config.today(),
            "resolve_by": f["resolve_by"],
            "resolution_criteria": f.get("resolution_criteria", ""),
            "reasoning": f.get("reasoning", ""),
            "status": "open",
            "outcome": None,
            "brier": None,
        })
        added += 1
        config.log(f"  + {int(p * 100)} % — {q[:80]}")
    save_forecasts(data)
    return added


def resolve() -> int:
    data = load_forecasts()
    today = config.today()
    due = [f for f in data["forecasts"] if f["status"] == "open" and f["resolve_by"] <= today]
    if not due:
        config.log("Žádná předpověď není splatná.")
        return 0

    threads = memory.load()["threads"]
    done = 0
    for f in due:
        context = "\n\n".join(
            memory.describe(t, max_entries=20) for t in threads[:12]
        )[:12000]
        try:
            out = ai.ask_json(
                RESOLVE,
                f"PŘEDPOVĚĎ: {f['question']}\nKRITÉRIUM: {f.get('resolution_criteria', '')}\n"
                f"TERMÍN: {f['resolve_by']}\n\nZÁZNAM UDÁLOSTÍ:\n{context}",
                max_tokens=800, temperature=0.1,
            )
        except Exception as e:  # noqa: BLE001
            config.log(f"  ! nelze rozhodnout: {str(e)[:120]}")
            continue

        res = str(out.get("outcome", "unclear")).lower()
        if res == "unclear":
            f["status"] = "void"
            f["explanation"] = out.get("explanation", "")
            config.log(f"  ~ zrušeno (nelze rozhodnout): {f['question'][:70]}")
        else:
            hit = 1.0 if res == "yes" else 0.0
            f["status"] = "resolved"
            f["outcome"] = res == "yes"
            f["resolved_on"] = today
            f["explanation"] = out.get("explanation", "")
            f["brier"] = round((f["probability"] - hit) ** 2, 4)
            mark = "✓" if (f["probability"] > 0.5) == f["outcome"] else "✗"
            config.log(f"  {mark} {int(f['probability'] * 100)} % → {res.upper()} "
                       f"(Brier {f['brier']}) {f['question'][:60]}")
        done += 1
    save_forecasts(data)
    s = scoreboard()
    config.log(f"Vyhodnoceno {done}. Celkem {s['resolved']} předpovědí, "
               f"Brier {s['brier']:.3f} — {s['verdict_cs']}.")
    return done


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "brief"
    if cmd == "brief":
        build_brief()
    elif cmd == "propose":
        propose()
    elif cmd == "resolve":
        resolve()
    elif cmd == "all":
        build_brief()
        resolve()
        propose()
