"""Článek dne — jeden pořádně propracovaný text denně.

Rubriky se střídají podle pořadí v nastavení, takže žádná nezůstane
hluchá. Téma se vybírá podle doložené poptávky (co lidé opravdu hledají),
a k němu se stáhnou podklady z Wikipedie, aby AI nepsala jen z hlavy.

Právě ty podklady jsou důvod, proč je tenhle článek spolehlivější než
běžný AI text: kontrolor faktů pak porovnává každé číslo a jméno
s tím, co v podkladech skutečně stojí.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.parse
import urllib.request

from . import article, config

UA = {"User-Agent": "TheDeeperStory/1.0 (research)"}


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as f:
        return f.read().decode("utf-8", "replace")


# ------------------------------------------------------------ podklady
def ground(term: str, max_pages: int = 3) -> list[dict]:
    """Stáhne k tématu výtahy z Wikipedie jako ověřitelný podklad."""
    out = []
    try:
        srch = json.loads(_get(
            "https://en.wikipedia.org/w/api.php?action=query&format=json&list=search"
            f"&srsearch={urllib.parse.quote(term)}&srlimit={max_pages}&srnamespace=0"))
        titles = [h["title"] for h in srch.get("query", {}).get("search", [])]
    except Exception as e:  # noqa: BLE001
        config.log(f"  ! podklady se nepodařilo najít: {str(e)[:90]}")
        return out

    for title in titles:
        try:
            j = json.loads(_get(
                "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts"
                "&explaintext=1&exsectionformat=plain&redirects=1&titles="
                + urllib.parse.quote(title)))
            for page in j.get("query", {}).get("pages", {}).values():
                text = (page.get("extract") or "").strip()
                if len(text) < 400:
                    continue
                text = re.sub(r"\n{2,}", "\n\n", text)[:9000]
                out.append({
                    "title": page.get("title", title),
                    "url": "https://en.wikipedia.org/wiki/" + page.get("title", title).replace(" ", "_"),
                    "text": text,
                })
        except Exception:  # noqa: BLE001
            continue
    return out


# ------------------------------------------------------------- výběr
def todays_section() -> str:
    cfg = config.site()["editorial"].get("daily_feature", {})
    rot = cfg.get("rotation") or ["meaning"]
    # pořadí se odvíjí od data, takže se rubriky rovnoměrně střídají
    idx = (dt.date.today() - dt.date(2026, 1, 1)).days % len(rot)
    return rot[idx]


def pick(section: str) -> dict | None:
    """Nejlepší téma pro dnešní rubriku."""
    state = config.load_state()
    used = set(state.get("used_topics", []))

    tp = config.DATA / "topics.json"
    if tp.exists():
        try:
            data = json.loads(tp.read_text(encoding="utf-8"))
            same = [t for t in data.get("topics", [])
                    if t.get("section") == section and t["term"].lower() not in used]
            if same:
                return max(same, key=lambda t: t.get("score", 0))
        except Exception:  # noqa: BLE001
            pass

    # záložní varianta: stálé téma, které do rubriky svým slovníkem sedí
    from .collect import SECTION_HINTS
    kws = set(SECTION_HINTS.get(section, "").split())
    for seed in config.site().get("topics", {}).get("evergreen_seeds", []):
        if seed.lower() in used:
            continue
        if any(w in seed.lower() for w in kws):
            return {"term": seed, "section": section, "source": "evergreen",
                    "score": 20, "questions": []}
    return None


def build() -> dict | None:
    cfg = config.site()["editorial"].get("daily_feature", {})
    if not cfg.get("enabled", True):
        return None

    section = todays_section()
    topic = pick(section)
    if not topic:
        config.log(f"Pro rubriku `{section}` se dnes nenašlo téma.")
        return None

    config.log(f"Článek dne: rubrika `{section}`, téma „{topic['term']}“ — sháním podklady…")
    sources = ground(topic["term"])
    config.log(f"  podklady: {len(sources)} stránek "
               f"({sum(len(s['text']) for s in sources) // 1000} tisíc znaků)")

    from .brief import depth_for
    return {
        "section": section,
        "term": topic["term"],
        "questions": topic.get("questions", []),
        "depth": depth_for(section, topic["term"]),
        "sources": sources,
        "min_words": cfg.get("min_words", 1100),
        "max_words": cfg.get("max_words", 1900),
    }


if __name__ == "__main__":
    d = build()
    if d:
        print(json.dumps({k: v for k, v in d.items() if k != "sources"},
                         ensure_ascii=False, indent=1))
        for s in d["sources"]:
            print(f"  podklad: {s['title']} ({len(s['text'])} znaků)")
