"""Vytvoří 'objednávku práce' (brief) pro AI redakci.

Tohle je propojka mezi zdarma-částí (GitHub Actions) a AI-částí
(naplánované úlohy ChatGPT Work nebo volitelné API). GitHub Actions připraví brief,
AI si ho přečte a napíše podle něj články do content/inbox/.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json

from . import config, daily, memory


def depth_for(section: str, key: str) -> str:
    """Rozhodne, jestli má mít článek biblickou závěrečnou vrstvu.

    Rozhodnutí je odvozené z identifikátoru článku, takže je stabilní —
    stejný článek dostane při každém běhu stejný režim.
    """
    ed = config.site()["editorial"]
    if section in ed.get("depth_never", []):
        return "open"
    if section in ed.get("depth_always", []):
        return "scripture"
    ratio = float(ed.get("depth_ratio", 0.3))
    h = int(hashlib.sha1(key.encode()).hexdigest()[:6], 16) / 0xFFFFFF
    return "scripture" if h < ratio else "open"


def _reserve_count() -> int:
    """Kolik hotových článků čeká 'v šuplíku' na vydání."""
    n = 0
    for p in (config.CONTENT / "en").glob("*.md"):
        head = p.read_text(encoding="utf-8")[:800]
        if "status: reserve" in head or "status: scheduled" in head:
            n += 1
    return n


def _next_series(state: dict, count: int) -> list:
    done = set(state.get("done_series", []))
    pending = [s for s in config.series() if s["id"] not in done]
    if not pending:  # kalendář došel – začneme znovu s hlubšími variantami
        pending = config.series()
    return pending[:count]


def build() -> dict:
    site = config.site()
    ed = site["editorial"]
    state = config.load_state()
    autonomous = config.is_autonomous()

    events_path = config.DATA / "events.json"
    events = json.loads(events_path.read_text(encoding="utf-8")) if events_path.exists() else []

    picked = [
        e for e in events
        if e["score"] >= ed["min_score"]
        and e["sources_count"] >= ed["min_sources"]
        and e["id"] not in set(state.get("used_events", []))
    ][: ed["news_per_day"]]

    for e in picked:
        e["depth"] = depth_for(e["section"], e["id"])

    reserve = _reserve_count()
    bible_needed = 1 if reserve < ed["reserve_target"] else 0
    if reserve < ed["reserve_emergency"]:
        bible_needed = 3

    # analýzy z dlouhodobé paměti — obsah, který bez záznamu napsat nejde
    analyses = []
    for t in memory.active(days=14, min_entries=3)[:2]:
        analyses.append({
            "id": t["id"],
            "title_hint": f"What has actually changed: {t['title'][:80]}",
            "section": t["section"],
            "depth": depth_for(t["section"], t["id"]),
            "timeline": memory.describe(t, max_entries=20),
            "thread_days": len(t["timeline"]),
        })

    # témata, po kterých je doložená poptávka
    demand = []
    tp = config.DATA / "topics.json"
    if tp.exists():
        try:
            data = json.loads(tp.read_text(encoding="utf-8"))
            used = set(state.get("used_topics", []))
            per_day = int(config.site().get("topics", {}).get("per_day", 1))
            for t in data.get("topics", []):
                if t["term"].lower() in used:
                    continue
                t["depth"] = depth_for(t.get("section") or "meaning", t["term"])
                demand.append(t)
                if len(demand) >= per_day:
                    break
        except Exception:  # noqa: BLE001
            pass

    # článek dne — jeden pořádně propracovaný text z rotující rubriky
    try:
        daily_item = daily.build()
    except Exception as e:  # noqa: BLE001
        config.log(f"Článek dne se nepodařilo připravit: {str(e)[:120]}")
        daily_item = None

    features = _next_series(state, max(bible_needed, 1))
    for f in features:
        f["depth"] = depth_for(f.get("section", "history"), f["id"])

    brief = {
        "date": config.today(),
        "mode": "autonomous" if autonomous else "normal",
        "days_since_human": config.days_since_human_activity(),
        "confidence_threshold": config.confidence_threshold(),
        "reserve_articles": reserve,
        "news_assignments": picked,
        "feature_assignments": features,
        "analysis_assignments": analyses,
        "demand_assignments": demand,
        "daily_assignment": daily_item,
        "master_language": site["languages"]["master"],
    }

    (config.DATA / "brief.json").write_text(
        json.dumps(brief, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (config.DATA / "brief.md").write_text(_as_markdown(brief), encoding="utf-8")
    config.log(
        f"Brief hotov: {len(picked)} zpráv, {len(features)} delších článků, "
        f"{len(analyses)} analýz, {len(demand)} na poptávku, "
        f"{'článek dne ano' if daily_item else 'článek dne ne'}, "
        f"režim {brief['mode']}, zásoba {reserve} článků."
    )
    return brief


def _as_markdown(b: dict) -> str:
    L = []
    A = L.append
    A(f"# ZADÁNÍ PRO REDAKCI — {b['date']}")
    A("")
    A(f"- Režim: **{b['mode']}**" + ("  ⚠️ nikdo se o projekt {} dní nestaral – buď opatrnější".format(b["days_since_human"]) if b["mode"] == "autonomous" else ""))
    A(f"- Práh jistoty pro automatické vydání: **{b['confidence_threshold']}/100**")
    A(f"- Článků v zásobě: **{b['reserve_articles']}**")
    A(f"- Jazyk, ve kterém se píše: **{b['master_language']}**")
    A("")
    A("---")
    A("")
    A("## A) ZPRAVODAJSKÉ ROZBORY")
    if not b["news_assignments"]:
        A("")
        A("_Dnes žádná událost nepřekročila práh důležitosti. Nic nepiš._")
    for i, e in enumerate(b["news_assignments"], 1):
        A("")
        A(f"### {i}. {e['headline']}")
        A(f"- id události: `{e['id']}`  ·  rubrika: `{e['section']}`  ·  "
          f"skóre: {e['score']}  ·  nezávislých zdrojů: {e['sources_count']}")
        A(f"- **depth: `{e['depth']}`** — "
          + ("závěrečná vrstva pracuje s biblickým textem"
             if e["depth"] == "scripture"
             else "závěrečná vrstva je obecně myšlenková, Bibli nezmiňuj"))
        A("- Zdroje:")
        for it in e["items"]:
            A(f"  - **{it['source']}** — {it['title']}")
            A(f"    <{it['url']}>")
            if it["summary"]:
                A(f"    > {it['summary'][:280]}")
    A("")
    A("---")
    A("")
    d = b.get("daily_assignment")
    A("## A2) ČLÁNEK DNE — hlavní text, na kterém záleží nejvíc")
    if not d:
        A("")
        A("_Dnes se nenašlo téma. Doplň `topics.evergreen_seeds` v data/site.yml._")
    else:
        A("")
        A(f"### {d['term']}")
        A(f"- rubrika: `{d['section']}`  ·  **depth: `{d['depth']}`**  ·  "
          f"rozsah {d['min_words']}–{d['max_words']} slov")
        if d.get("questions"):
            A("- otázky, které k tomu lidé píší do vyhledávače:")
            for q in d["questions"]:
                A(f"  - „{q}“")
        A(f"- PODKLADY ({len(d.get('sources', []))} stránek) jsou v `data/brief.json` "
          "pod `daily_assignment.sources`. **Piš z nich, ne z hlavy** — každé číslo "
          "a jméno v článku bude porovnáno s tímhle podkladem.")
        for src in d.get("sources", []):
            A(f"  - {src['title']} — <{src['url']}>")
    A("")
    A("---")
    A("")
    A("## B) TÉMATA, PO KTERÝCH JE POPTÁVKA")
    if not b.get("demand_assignments"):
        A("")
        A("_Dnes nic. Spusť `python -m engine.trends`._")
    for i, t in enumerate(b.get("demand_assignments", []), 1):
        A("")
        A(f"### {i}. {t['term']}")
        A(f"- rubrika: `{t.get('section')}`  ·  signál: {t.get('source')}  ·  "
          f"síla: {t.get('score')}  ·  **depth: `{t.get('depth')}`**")
        A("- OTÁZKY, KTERÉ LIDÉ SKUTEČNĚ PÍŠÍ (odpověz na ně, ne na to, co si myslíš, že chtějí):")
        for q in t.get("questions", []):
            A(f"  - „{q}“")
    A("")
    A("---")
    A("")
    A("## C) ANALÝZY Z DLOUHODOBÉ PAMĚTI")
    if not b.get("analysis_assignments"):
        A("")
        A("_Zatím není dost historie. Analýzy začnou vznikat, až systém poběží "
          "pár týdnů a nasbírá časové osy témat._")
    for i, a in enumerate(b.get("analysis_assignments", []), 1):
        A("")
        A(f"### {i}. {a['title_hint']}")
        A(f"- id: `{a['id']}`  ·  rubrika: `{a['section']}`  ·  "
          f"záznamů v ose: {a['thread_days']}  ·  **depth: `{a['depth']}`**")
        A("- ČASOVÁ OSA (tohle je ten materiál, který nikdo jiný nemá):")
        A("")
        A("```")
        A(a["timeline"])
        A("```")
    A("")
    A("---")
    A("")
    A("## D) DELŠÍ ČLÁNKY (do zásoby)")
    for i, s in enumerate(b["feature_assignments"], 1):
        A("")
        A(f"### {i}. {s['title_hint']}")
        A(f"- id: `{s['id']}`  ·  rubrika: `{s.get('section', 'history')}`  ·  série: {s['series']}")
        if s.get("passage"):
            A(f"- Výchozí text: {s['passage']}")
        A(f"- **depth: `{s['depth']}`**")
        A(f"- Úhel pohledu: {s['angle']}")
    A("")
    return "\n".join(L)


if __name__ == "__main__":
    build()
