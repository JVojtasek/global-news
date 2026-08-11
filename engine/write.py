"""Napsání článků podle briefu — cesta přes API.

Pipeline pro každý článek:
  1) draft      – napiš článek
  2) guardian   – teologická kontrola
  3) sceptic    – kontrola očima nevěřícího čtenáře
  4) revise     – přepiš podle připomínek
  5) rozhodni   – publikovat / do zásoby / k ruční kontrole

Když AI nefunguje nebo je vyčerpaný denní strop, skript prostě skončí
bez chyby a systém jede dál z existující zásoby článků.
"""
from __future__ import annotations

import json
import sys

from . import ai, article, config, safety

P = config.ROOT / "engine" / "prompts"


def _prompt(name: str) -> str:
    return (P / name).read_text(encoding="utf-8")


FORMAT = _prompt("FORMAT.md")


def _fix_section(meta: dict, defaults: dict) -> dict:
    """Model si občas splete rubriku. Typ článku rozhoduje, ne model."""
    if meta.get("section") not in {s["id"] for s in config.site()["sections"]}:
        meta["section"] = defaults.get("section", "world")
    meta["depth"] = defaults.get("depth", meta.get("depth", "open"))
    meta["type"] = defaults.get("type", meta.get("type", "news"))
    return meta


def _pipeline(system: str, task: str, defaults: dict, sensitive: bool) -> dict | None:
    config.log(f"  → píšu: {defaults.get('_label', '')}")
    raw = ai.ask(system + "\n\n" + FORMAT, task, max_tokens=9000, temperature=0.6)
    meta, body = article.parse(raw)
    if not meta:
        config.log("  ! model nevrátil platnou hlavičku, přeskakuji")
        return None
    meta, body = article.normalise(meta, body, defaults=defaults)
    meta = _fix_section(meta, defaults)

    config.log("  → teologická kontrola")
    g = ai.ask_json(_prompt("guardian.md"), article.dump(meta, body), max_tokens=3000, temperature=0.1)

    config.log("  → skeptická kontrola")
    s = ai.ask_json(_prompt("sceptic.md"), article.dump(meta, body), max_tokens=3000, temperature=0.3)

    blockers = [i for i in g.get("issues", []) if i.get("severity") == "blocker"]
    needs_revision = blockers or g.get("verdict") in ("revise", "block") or s.get("manipulation_score", 0) > 35

    if needs_revision:
        config.log(f"  → přepisuji ({len(blockers)} blokujících připomínek)")
        notes = json.dumps({"theology": g, "sceptic": s}, ensure_ascii=False)[:6000]
        raw2 = ai.ask(
            _prompt("revise.md"),
            f"ČLÁNEK:\n{article.dump(meta, body)}\n\nPŘIPOMÍNKY:\n{notes}",
            max_tokens=9000,
            temperature=0.4,
        )
        m2, b2 = article.parse(raw2)
        if m2:
            meta, body = article.normalise(m2, b2, defaults=defaults)
            meta = _fix_section(meta, defaults)

    # výsledná jistota = kombinace obou kontrol
    conf = min(
        int(g.get("confidence", 60)),
        int(s.get("credibility_score", 60)),
        100 - int(s.get("manipulation_score", 20)),
        int(s.get("deeper_layer_quality", 80)) + 15,
    )
    if s.get("detected_agenda"):
        conf = min(conf, 70)   # skeptik prokoukl záměr → článek jde k ruční kontrole
    meta["confidence"] = conf
    meta["review"] = {
        "theology_verdict": g.get("verdict", "?"),
        "sceptic_verdict": s.get("one_sentence_verdict", "")[:200],
        "manipulation_score": s.get("manipulation_score"),
        "open_issues": len(g.get("issues", [])) + len(s.get("issues", [])),
    }

    problems = article.validate(meta, body)
    if problems:
        config.log("  ! formální problémy: " + "; ".join(problems[:3]))
        meta["status"] = "review"
        meta["problems"] = problems
    else:
        threshold = config.confidence_threshold()
        if sensitive:
            meta["status"] = "review"
        elif conf >= threshold:
            meta["status"] = "published" if defaults.get("type") == "news" else "reserve"
        else:
            meta["status"] = "review"

    p = article.save(meta, body)
    config.log(f"  ✓ {p.name}  jistota {conf}/100  stav {meta['status']}")
    return meta


def _is_sensitive(text: str) -> bool:
    always = set(config.site()["editorial"]["always_review"])
    return safety.is_sensitive(text, always)


def _deep_pipeline(task: str, defaults: dict, grounding: str) -> dict | None:
    """Delší postup pro článek dne: draft → fakta → teologie → skeptik → přepis."""
    config.log(f"  → článek dne: {defaults.get('_label', '')}")
    raw = ai.ask(_prompt("deep_article.md") + "\n\n" + FORMAT,
                 task, max_tokens=12000, temperature=0.65)
    meta, body = article.parse(raw)
    if not meta:
        config.log("  ! model nevrátil platnou hlavičku")
        return None
    meta, body = article.normalise(meta, body, defaults=defaults)
    meta = _fix_section(meta, defaults)

    config.log("  → kontrola faktů proti podkladům")
    fc = ai.ask_json(_prompt("factcheck.md"),
                     f"ČLÁNEK:\n{article.dump(meta, body)}\n\nPODKLADY:\n{grounding[:40000]}",
                     max_tokens=4000, temperature=0.0)
    bad = [c for c in fc.get("claims", []) if c.get("verdict") in ("unsupported", "wrong", "vague")]
    config.log(f"     tvrzení bez opory: {len(bad)}"
               + (f" — nejhorší: {str(fc.get('worst', ''))[:70]}" if bad else ""))

    config.log("  → teologická kontrola")
    g = ai.ask_json(_prompt("guardian.md"), article.dump(meta, body), max_tokens=3000, temperature=0.1)
    config.log("  → skeptická kontrola")
    sc = ai.ask_json(_prompt("sceptic.md"), article.dump(meta, body), max_tokens=3000, temperature=0.3)

    if bad or g.get("verdict") in ("revise", "block") or sc.get("manipulation_score", 0) > 35:
        config.log(f"  → přepisuji ({len(bad)} faktických nálezů)")
        notes = json.dumps({"facts": fc, "theology": g, "sceptic": sc}, ensure_ascii=False)[:9000]
        raw2 = ai.ask(_prompt("revise.md") +
                      "\n\nFAKTICKÉ NÁLEZY MAJÍ PŘEDNOST PŘED VŠÍM OSTATNÍM. "
                      "Každé tvrzení označené unsupported, wrong nebo vague buď oprav "
                      "podle podkladů, nebo z textu úplně vyhoď. Nic si nedomýšlej.",
                      f"ČLÁNEK:\n{article.dump(meta, body)}\n\nPŘIPOMÍNKY:\n{notes}"
                      f"\n\nPODKLADY:\n{grounding[:30000]}",
                      max_tokens=12000, temperature=0.4)
        m2, b2 = article.parse(raw2)
        if m2:
            meta, body = article.normalise(m2, b2, defaults=defaults)
            meta = _fix_section(meta, defaults)

    conf = min(int(g.get("confidence", 60)),
               int(sc.get("credibility_score", 60)),
               100 - int(sc.get("manipulation_score", 20)),
               100 - min(len(bad) * 8, 60))
    if not fc.get("safe_to_publish", True):
        conf = min(conf, 65)
    meta["confidence"] = conf
    meta["review"] = {
        "theology_verdict": g.get("verdict", "?"),
        "sceptic_verdict": sc.get("one_sentence_verdict", "")[:200],
        "unsupported_claims": len(bad),
        "factcheck_worst": str(fc.get("worst", ""))[:160],
    }

    problems = article.validate(meta, body)
    words = len(body.split())
    if words < int(defaults.get("_min_words", 900)):
        problems.append(f"článek je kratší, než má být ({words} slov)")
    if problems:
        meta["status"] = "review"
        meta["problems"] = problems
        config.log("  ! " + "; ".join(problems[:2]))
    else:
        meta["status"] = "published" if conf >= config.confidence_threshold() else "review"

    p = article.save(meta, body)
    config.log(f"  ✓ {p.name}  jistota {conf}/100  stav {meta['status']}  ({words} slov)")
    return meta


def run(limit_news: int | None = None, limit_bible: int | None = None) -> None:
    brief_path = config.DATA / "brief.json"
    if not brief_path.exists():
        config.log("Brief neexistuje – spusť nejdřív `python -m engine.brief`.")
        return
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    state = config.load_state()
    written = 0

    news = brief["news_assignments"][: limit_news if limit_news is not None else len(brief["news_assignments"])]
    for e in news:
        task = (
            f"UDÁLOST: {e['headline']}\nRUBRIKA: {e['section']}\n"
            f"REŽIM ZÁVĚREČNÉ VRSTVY (depth): {e['depth']}\n\nZDROJE:\n"
            + "\n".join(
                f"- [{i['source']}] {i['title']}\n  {i['url']}\n  {i['summary'][:400]}"
                for i in e["items"]
            )
        )
        try:
            meta = _pipeline(
                _prompt("news_article.md"),
                task,
                {
                    "type": "news",
                    "section": e["section"],
                    "event_id": e["id"],
                    "depth": e["depth"],
                    "_label": e["headline"][:60],
                    "sources": [{"name": i["source"], "url": i["url"]} for i in e["items"][:6]],
                },
                sensitive=_is_sensitive(e["headline"] + " " + " ".join(i["title"] for i in e["items"])),
            )
            if meta:
                state.setdefault("used_events", []).append(e["id"])
                written += 1
        except ai.BudgetExceeded as ex:
            config.log(f"STOP: {ex}")
            break
        except Exception as ex:  # noqa: BLE001
            config.log(f"  ! událost přeskočena: {str(ex)[:200]}")

    d = brief.get("daily_assignment")
    if d:
        grounding = "\n\n".join(
            f"### {s['title']}\n{s['url']}\n{s['text']}" for s in d.get("sources", []))
        qs = "\n".join(f"- {q}" for q in d.get("questions", [])) or "(žádné konkrétní)"
        task = (
            f"TÉMA: {d['term']}\nRUBRIKA: {d['section']}\n"
            f"REŽIM ZÁVĚREČNÉ VRSTVY (depth): {d['depth']}\n"
            f"ROZSAH: {d['min_words']}–{d['max_words']} slov\n\n"
            f"OTÁZKY, KTERÉ K TOMU LIDÉ PÍŠÍ:\n{qs}\n\n"
            f"PODKLADY — piš z nich, ne z hlavy:\n{grounding[:40000]}"
        )
        try:
            meta = _deep_pipeline(task, {
                "type": "daily", "section": d["section"], "depth": d["depth"],
                "_label": d["term"][:60], "_min_words": d["min_words"],
                "sources": [{"name": s["title"], "url": s["url"]} for s in d.get("sources", [])],
            }, grounding)
            if meta:
                state.setdefault("used_topics", []).append(d["term"].lower())
                written += 1
        except ai.BudgetExceeded as ex:
            config.log(f"STOP: {ex}")
        except Exception as ex:  # noqa: BLE001
            config.log(f"  ! článek dne přeskočen: {str(ex)[:200]}")

    for t in brief.get("demand_assignments", []):
        qs = "\n".join(f"- {q}" for q in t.get("questions", []))
        task = (
            f"TÉMA: {t['term']}\nRUBRIKA: {t.get('section', 'meaning')}\n"
            f"REŽIM ZÁVĚREČNÉ VRSTVY (depth): {t.get('depth', 'open')}\n\n"
            f"OTÁZKY, KTERÉ LIDÉ PÍŠÍ DO VYHLEDÁVAČE:\n{qs}\n\n"
            f"Hlavní otázka je ta první. Odpověz na ni v prvním odstavci."
        )
        try:
            meta = _pipeline(
                _prompt("demand_article.md"), task,
                {"type": "demand", "section": t.get("section", "meaning"),
                 "depth": t.get("depth", "open"), "_label": t["term"][:60]},
                sensitive=False,
            )
            if meta:
                state.setdefault("used_topics", []).append(t["term"].lower())
                written += 1
        except ai.BudgetExceeded as ex:
            config.log(f"STOP: {ex}")
        except Exception as ex:  # noqa: BLE001
            config.log(f"  ! téma přeskočeno: {str(ex)[:200]}")

    for a in brief.get("analysis_assignments", []):
        task = (
            f"TÉMA: {a['title_hint']}\nRUBRIKA: {a['section']}\n"
            f"REŽIM ZÁVĚREČNÉ VRSTVY (depth): {a['depth']}\n\n"
            f"ČASOVÁ OSA TÉMATU:\n{a['timeline']}"
        )
        try:
            meta = _pipeline(
                _prompt("analysis_article.md"), task,
                {"type": "analysis", "section": a["section"], "depth": a["depth"],
                 "_label": a["title_hint"][:60]},
                sensitive=_is_sensitive(a["title_hint"] + " " + a["timeline"][:500]),
            )
            if meta:
                written += 1
        except ai.BudgetExceeded as ex:
            config.log(f"STOP: {ex}")
        except Exception as ex:  # noqa: BLE001
            config.log(f"  ! analýza přeskočena: {str(ex)[:200]}")

    bible = brief["feature_assignments"][: limit_bible if limit_bible is not None else len(brief["feature_assignments"])]
    for s in bible:
        task = (
            f"TÉMA: {s['title_hint']}\nSÉRIE: {s['series']}\n"
            f"RUBRIKA: {s.get('section', 'history')}\n"
            f"REŽIM ZÁVĚREČNÉ VRSTVY (depth): {s['depth']}\n"
            f"VÝCHOZÍ TEXT: {s.get('passage', '—')}\nÚHEL POHLEDU: {s['angle']}"
        )
        try:
            meta = _pipeline(
                _prompt("feature_article.md"),
                task,
                {
                    "type": "feature",
                    "section": s.get("section", "history"),
                    "series": s["series"],
                    "passage": s.get("passage", ""),
                    "depth": s["depth"],
                    "slug": s["id"],
                    "_label": s["title_hint"][:60],
                },
                sensitive=False,
            )
            if meta:
                state.setdefault("done_series", []).append(s["id"])
                written += 1
        except ai.BudgetExceeded as ex:
            config.log(f"STOP: {ex}")
            break
        except Exception as ex:  # noqa: BLE001
            config.log(f"  ! biblický článek přeskočen: {str(ex)[:200]}")

    state.setdefault("last_run", {})["write"] = config.today()
    config.save_state(state)
    config.log(f"Hotovo. Napsáno článků: {written}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    b = int(sys.argv[2]) if len(sys.argv) > 2 else None
    run(n, b)
