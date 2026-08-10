"""Sběr zpráv z RSS, slučování duplicit do událostí, skórování.

Tohle je "nudná" část, která stojí 0 Kč a nepotřebuje žádnou AI.
Běží na GitHub Actions každé 3 hodiny.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from collections import defaultdict

import feedparser

from . import config

STOP = set("""a an the and or of in on at to for from by with is are was were be been
this that these those it its as has have had will would can could may might not no new
after before over under about into than then them they he she his her you your we our us
says said report reports live latest breaking update updates video watch""".split())

# klíčová slova -> rubrika (jednoduché, ale překvapivě funkční)
SECTION_HINTS = {
    "world": "election government president minister parliament summit border refugee protest court "
             "war strike missile ceasefire troops invasion attack military conflict hostage airstrike",
    "business": "inflation economy market stocks shares gdp bank tariff trade jobs unemployment budget "
                "currency debt investors earnings revenue profit merger crypto bitcoin interest rates",
    "tech": "artificial intelligence chip robot software startup openai google apple microsoft data "
            "model quantum algorithm app smartphone cloud cyber hacking semiconductor",
    "science": "study research scientists discovery physics species nasa telescope genome climate "
               "fossil astronomy particle experiment orbit galaxy evolution",
    "health": "cancer vaccine patients doctors hospital disease virus mental therapy diet sleep "
              "brain trial medicine treatment diagnosis obesity",
    "culture": "film movie music album artist novel book museum exhibition theatre festival design "
               "photography actor director gallery",
    "travel": "destination hotel flight airline tourism island beach hiking city guide passport visa "
              "railway trek village landscape",
    "motoring": "car electric vehicle battery driver engine tesla motorway charging automotive suv",
    "sport": "match final league champion goal tournament olympic player coach season score cup",
    "food": "recipe cooking chef restaurant kitchen ingredient bread cheese wine coffee dish flavour",
    "goodnews": "rescue saved recovery breakthrough restored donated reunited kindness conservation "
                "survived recovering volunteers thriving reforestation",
    "history": "archaeology excavation ancient artifact tomb ruins inscription bronze iron century "
               "empire dynasty manuscript scroll temple archaeologist",
    "questions": "philosophy ethics meaning morality consciousness free will existence belief religion "
                 "truth justice why argument debate",
    "relationships": "relationship couple marriage partner dating divorce love intimacy trust "
                     "conflict communication breakup friendship attachment jealousy apology",
    "parenting": "children child parents parenting toddler teenager baby school homework "
                 "discipline screen time family mother father siblings adolescence upbringing",
    "ai": "artificial intelligence machine learning neural model llm chatbot openai anthropic "
          "deepmind gemini claude gpt robot robotics humanoid autonomous agent training inference "
          "chip gpu nvidia dataset benchmark alignment automation copilot",
    "safety": "scam phishing fraud breach hacked ransomware malware password stolen leaked "
              "cyberattack identity spyware surveillance vishing extortion victim warning "
              "emergency evacuation blackout preparedness safety alert protect",
    "wonder": "species discovered animal ocean deep insect bird whale fossil galaxy universe "
              "telescope nebula cells neurons immune body organ evolution symbiosis migration "
              "extraordinary remarkable astonishing rare unique phenomenon",
    "meaning": "psychology loneliness happiness gratitude burnout anxiety resilience purpose habits "
               "attention mindfulness relationships forgiveness compassion",
}

# Slova, která signalizují, že za zprávou je lidská otázka — tedy že se hodí
# k závěrečné vrstvě "The deeper story". Nejde o náboženský filtr.
DEPTH_SIGNALS = set("""hope fear grief loss death dying survival rescue forgiveness justice injustice
dignity meaning purpose loneliness identity trust betrayal courage sacrifice mercy shame guilt
addiction suicide poverty famine refugee orphan family marriage children elderly disability
ethics moral conscience freedom persecution faith belief community belonging kindness""".split())


def _tokens(title: str) -> set:
    """Významová slova z titulku. Vlastní jména (velké písmeno) váží dvakrát."""
    words = re.findall(r"[A-Za-zÁ-Žá-ž][A-Za-zÁ-Žá-ž'-]{2,}", title)
    out = set()
    for w in words:
        lw = w.lower()
        if lw in STOP or len(lw) < 4:
            continue
        out.add(lw)
        if w[0].isupper():
            out.add("^" + lw)  # vlastní jméno = druhý token = dvojnásobná váha
    return out


def _fetch_all() -> list:
    items = []
    for src in config.sources():
        try:
            feed = feedparser.parse(src["url"])
            n = 0
            for e in feed.entries[:40]:
                link = getattr(e, "link", "")
                title = getattr(e, "title", "").strip()
                if not link or not title:
                    continue
                summary = re.sub(r"<[^>]+>", " ", getattr(e, "summary", ""))[:600]
                items.append(
                    {
                        "title": title,
                        "url": link,
                        "summary": " ".join(summary.split()),
                        "source": src["name"],
                        "weight": src.get("weight", 5),
                        "src_section": src.get("section"),
                        "seen_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                    }
                )
                n += 1
            config.log(f"  {src['name']}: {n} položek")
        except Exception as e:  # noqa: BLE001
            config.log(f"  ! {src['name']} selhal: {str(e)[:120]}")
    return items


def _similar(a: set, b: set) -> bool:
    inter = a & b
    if not inter:
        return False
    named = {t for t in inter if t.startswith("^")}
    plain = inter - named
    # dvě shodná vlastní jména + jedno obecné slovo = skoro jistě táž událost
    if len(named) >= 2 and len(plain) >= 1:
        return True
    containment = len(inter) / max(1, min(len(a), len(b)))
    return containment >= 0.5 and len(plain) >= 2


def _cluster(items: list) -> list:
    """Sloučí články o téže události napříč zdroji."""
    clusters: list = []
    for it in items:
        toks = _tokens(it["title"])
        if len(toks) < 3:
            continue
        placed = False
        for c in clusters:
            if _similar(toks, c["tokens"]):
                c["items"].append(it)
                c["tokens"] |= toks
                placed = True
                break
        if not placed:
            clusters.append({"tokens": toks, "items": [it]})
    return clusters


def _section_for(cluster: dict) -> str:
    """Rubrika podle zdrojů (kde je uvedená) a podle klíčových slov."""
    items = cluster["items"]
    text = " ".join(i["title"] + " " + i["summary"][:200] for i in items).lower()

    votes: dict = {}
    for i in items:
        hint = i.get("src_section")
        if hint:
            votes[hint] = votes.get(hint, 0) + i.get("weight", 5)

    scores = {sec: sum(2 for w in kws.split() if w in text) for sec, kws in SECTION_HINTS.items()}
    for sec, v in votes.items():
        scores[sec] = scores.get(sec, 0) + v

    valid = {s["id"] for s in config.site()["sections"]}
    scores = {k: v for k, v in scores.items() if k in valid}
    if not scores:
        return "world"
    sec, val = max(scores.items(), key=lambda kv: kv[1])
    return sec if val > 0 else "world"


def _score(cluster: dict) -> dict:
    items = cluster["items"]
    outlets = {i["source"] for i in items}
    text = " ".join(i["title"] + " " + i["summary"][:200] for i in items).lower()

    n_sources = min(len(outlets), 5) / 5 * 30          # 0-30 kolik nezávislých zdrojů
    credibility = max(i["weight"] for i in items) / 10 * 20   # 0-20 důvěryhodnost
    volume = min(len(items), 8) / 8 * 15             # 0-15 kolik článků celkem
    depth = min(sum(1 for w in DEPTH_SIGNALS if w in text), 6) / 6 * 15  # 0-15 lidský rozměr
    breadth = min(len(cluster["tokens"]), 30) / 30 * 20  # 0-20 šíře tématu
    total = round(n_sources + credibility + volume + depth + breadth)

    lead = sorted(items, key=lambda i: -i["weight"])[0]
    return {
        "id": hashlib.sha1(lead["url"].encode()).hexdigest()[:12],
        "headline": lead["title"],
        "section": _section_for(cluster),
        "score": total,
        "sources_count": len(outlets),
        "depth_signal": round(depth),
        "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "items": [
            {"title": i["title"], "url": i["url"], "source": i["source"], "summary": i["summary"][:400]}
            for i in sorted(items, key=lambda i: -i["weight"])[:10]
        ],
    }


def run() -> list:
    config.log("Sbírám zprávy…")
    items = _fetch_all()
    state = config.load_state()
    seen = set(state.get("seen_urls", []))

    fresh = [i for i in items if i["url"] not in seen]
    config.log(f"Celkem {len(items)} položek, z toho {len(fresh)} nových.")

    clusters = _cluster(fresh)
    events = [_score(c) for c in clusters]
    events = [e for e in events if e["sources_count"] >= 1]
    events.sort(key=lambda e: -e["score"])

    state["seen_urls"] = list(seen | {i["url"] for i in items})
    state.setdefault("last_run", {})["collect"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    config.save_state(state)

    out = config.DATA / "events.json"
    old = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    # necháme události 3 dny, ať se dají porovnávat a nezmizí přes noc
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)).isoformat()
    keep = [e for e in old if e.get("created", "") > cutoff]
    known = {e["id"] for e in keep}
    merged = keep + [e for e in events if e["id"] not in known]
    merged.sort(key=lambda e: -e["score"])
    out.write_text(json.dumps(merged[:300], ensure_ascii=False, indent=1), encoding="utf-8")

    config.log(f"Uloženo {len(merged[:300])} událostí. Nejsilnější: "
               f"{merged[0]['headline'][:70] if merged else '—'} ({merged[0]['score'] if merged else 0})")
    return merged


if __name__ == "__main__":
    run()
