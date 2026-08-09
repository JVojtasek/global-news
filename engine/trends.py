"""Poptávka — o čem lidé skutečně chtějí číst.

POZOR NA ROZDÍL, KTERÝ ROZHODUJE O ÚSPĚCHU:

Denní žebříčky vyhledávání jsou z devadesáti procent sport a celebrity.
Když se dnes podíváš na Google Trends, uvidíš „Benfica", „Kylie Jenner",
„Djoković". To nejsou témata pro tenhle web a nikdy je nevyhrajeme —
píše o nich tisíc redakcí, které tam byly dřív.

Co má cenu, jsou **otázky, které lidé píší do vyhledávače pořád dokola**:
„proč inflace nikdy neklesá", „co se stane, když…", „je pravda, že…".
Ty mají stálou poptávku, slabou konkurenci a nezastarají za týden.
Přesně na ně je tenhle web stavěný.

Modul proto dělá dvě věci:
  1. z denních trendů vezme jen to, co vůbec patří do našich rubrik
  2. každé téma rozvine na skutečné otázky, které lidé píší

Všechny zdroje jsou zdarma a bez klíčů.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import time
import urllib.parse
import urllib.request

import feedparser

from . import article, config
from .collect import SECTION_HINTS

UA = {"User-Agent": "TheDeeperStory/1.0 (topic research)"}

# Co nikdy nepíšeme, ať se to v žebříčcích objeví jakkoli vysoko
BLOCK = re.compile(
    r"\b(vs\.?|fc|cup|league|match|fixture|standings|score|goal|transfer|nba|nfl|nhl|"
    r"ufc|f1|grand prix|premier league|championship|playoff|odds|betting|lottery|jackpot|"
    r"episode|season \d|trailer|box office|red carpet|dating|girlfriend|boyfriend|"
    r"net worth|divorce|instagram|onlyfans|leaked|nude|arrested|mugshot|obituary|"
    r"died|death of|funeral|weather forecast|horoscope)\b",
    re.I,
)

QUESTION_STARTS = ["why does", "why is", "how does", "how much", "what happens if",
                   "is it true that", "what causes", "should i", "can you", "does"]


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as f:
        return f.read().decode("utf-8", "replace")


# ------------------------------------------------------------- zdroje signálu
def _google_trends(geos: list[str]) -> list[dict]:
    out = []
    for geo in geos:
        try:
            feed = feedparser.parse(f"https://trends.google.com/trending/rss?geo={geo}")
            for e in feed.entries[:20]:
                out.append({"term": e.title.strip(), "source": f"trends/{geo}", "weight": 3})
        except Exception as e:  # noqa: BLE001
            config.log(f"  ! Google Trends {geo}: {str(e)[:80]}")
    return out


def _wikipedia(lang: str = "en") -> list[dict]:
    d = dt.date.today() - dt.timedelta(days=2)
    try:
        j = json.loads(_get(
            f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
            f"{lang}.wikipedia/all-access/{d.year}/{d.month:02d}/{d.day:02d}"))
        out = []
        for a in j["items"][0]["articles"][:60]:
            name = a["article"]
            if name.startswith(("Main_Page", "Special:", "Wikipedia:", "Portal:")):
                continue
            out.append({"term": name.replace("_", " "), "source": "wikipedia",
                        "weight": 2, "views": a["views"]})
        return out
    except Exception as e:  # noqa: BLE001
        config.log(f"  ! Wikipedia: {str(e)[:80]}")
        return []


def _hackernews() -> list[dict]:
    try:
        j = json.loads(_get("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"))
        return [{"term": h["title"], "source": "hn", "weight": 4, "points": h.get("points", 0)}
                for h in j["hits"] if h.get("title")]
    except Exception as e:  # noqa: BLE001
        config.log(f"  ! Hacker News: {str(e)[:80]}")
        return []


def _suggest(prefix: str) -> list[str]:
    """Co lidé skutečně dopisují do vyhledávače."""
    try:
        url = ("https://suggestqueries.google.com/complete/search?client=firefox&q="
               + urllib.parse.quote(prefix))
        j = json.loads(_get(url, timeout=12))
        return [q for q in j[1] if isinstance(q, str)]
    except Exception:  # noqa: BLE001
        return []


# ------------------------------------------------------------------ hodnocení
def _section_fit(text: str) -> tuple[str | None, int]:
    t = text.lower()
    best, score = None, 0
    for sec, kws in SECTION_HINTS.items():
        n = sum(1 for w in kws.split() if w in t)
        if n > score:
            best, score = sec, n
    return best, score


def _clean_term(term: str) -> str:
    term = re.sub(r"\s*[\(\[].*?[\)\]]", "", term)
    term = re.sub(r"[^\w\s'-]", " ", term)
    return " ".join(term.split())[:60]


def _already_covered(term: str, covered: set) -> bool:
    words = {w for w in re.findall(r"[a-z]{4,}", term.lower())}
    return any(len(words & c) >= 2 for c in covered)


def run(limit: int = 8) -> list:
    cfg = config.site().get("topics", {})
    if not cfg.get("enabled", True):
        config.log("Hledání témat je vypnuté.")
        return []

    config.log("Sbírám signály poptávky…")
    seeds = (_google_trends(cfg.get("geos", ["US", "GB"]))
             + _wikipedia()
             + _hackernews())
    config.log(f"  surových signálů: {len(seeds)}")

    # o čem už jsme psali
    covered = set()
    for lang in [config.site()["languages"]["master"]]:
        for m, _, _ in article.load_all(lang):
            covered.add({w for w in re.findall(r"[a-z]{4,}", (m.get("title") or "").lower())})

    kept = []
    for s in seeds:
        term = _clean_term(s["term"])
        if len(term) < 6 or BLOCK.search(term):
            continue
        sec, fit = _section_fit(term)
        if fit < 1:
            continue
        if _already_covered(term, covered):
            continue
        kept.append({**s, "term": term, "section": sec,
                     "score": fit * 10 + s["weight"] * 3})

    # vlastní stálá témata, ať to funguje i ve dnech, kdy jsou trendy samý fotbal
    for t in cfg.get("evergreen_seeds", []):
        sec, _ = _section_fit(t)
        kept.append({"term": t, "source": "evergreen", "weight": 2,
                     "section": sec or "meaning", "score": 22})

    # sloučení stejných témat
    merged: dict = {}
    for k in kept:
        key = k["term"].lower()
        if key in merged:
            merged[key]["score"] += k["score"] // 2
        else:
            merged[key] = k
    kept = sorted(merged.values(), key=lambda k: -k["score"])[: limit * 2]
    config.log(f"  po odfiltrování sportu a celebrit zbylo: {len(kept)}")

    # rozvinutí na skutečné otázky
    topics = []
    for k in kept:
        questions = []
        for start in QUESTION_STARTS[:5]:
            for q in _suggest(f"{start} {k['term'].lower()}")[:3]:
                q = q.strip()
                if len(q) > 18 and q.lower().startswith(start) and q not in questions:
                    questions.append(q)
            time.sleep(0.4)
            if len(questions) >= 6:
                break
        if not questions:
            continue
        k["questions"] = questions[:6]
        k["score"] += len(questions) * 4
        topics.append(k)
        if len(topics) >= limit:
            break

    topics.sort(key=lambda k: -k["score"])
    out = {"date": config.today(), "topics": topics}
    (config.DATA / "topics.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    config.log(f"Nalezeno {len(topics)} témat s doloženou poptávkou.")
    for t in topics[:5]:
        config.log(f"  {t['score']:>3}  [{t['section']}] {t['term']} "
                   f"— „{t['questions'][0][:60]}“")
    return topics


if __name__ == "__main__":
    import sys
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
