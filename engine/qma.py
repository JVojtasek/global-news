"""Přebírání vlastních článků z QMA magazínu.

Tohle jsou TVOJE články, takže se nepřebírají jako cizí — nejdou pod
licenční poznámku, ale pod tvoje jméno, s odkazem na původní vydání.

Postup:
  1. načte se sitemap QMA
  2. vyberou se články z rubrik, které chceš (výchozí: analýzy)
  3. z každé stránky se vytáhne titulek, popis, datum a text
  4. uloží se jako český článek
  5. při dalším běhu je `engine.translate` přeloží do angličtiny

U finančních článků se automaticky připojí upozornění, že jde
o vzdělávací obsah, ne investiční doporučení.
"""
from __future__ import annotations

import re
import time
import urllib.request

from bs4 import BeautifulSoup

from . import article, config

UA = {"User-Agent": "TheDeeperStory/1.0 (own-content importer)"}

DISCLAIMER = (
    "> **Analytical and educational content — not investment advice.** "
    "The author is not a registered investment adviser. "
    "Past performance is not a guide to future results."
)


def _cfg() -> dict:
    return config.site().get("import", {}).get("qma", {})


def _get(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as f:
        return f.read().decode("utf-8", "replace")


def _urls() -> list[str]:
    cfg = _cfg()
    sm = _get(cfg["sitemap"])
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    keep = []
    for u in locs:
        if not any(p in u for p in cfg.get("paths", ["/magazin/"])):
            continue
        if u.count("/") < cfg.get("min_depth", 5):
            continue
        keep.append(u)
    return keep


def _extract(url: str) -> dict | None:
    html = _get(url)
    soup = BeautifulSoup(html, "html.parser")

    meta = {}
    for m in soup.find_all("meta"):
        prop = m.get("property") or m.get("name")
        if prop in ("og:title", "og:description", "article:published_time", "description"):
            meta[prop] = m.get("content", "")

    title = (meta.get("og:title") or (soup.title.string if soup.title else "") or "").strip()
    title = re.sub(r"\s*[|·—-]\s*(QMA|Quantum Market Analyzer).*$", "", title).strip()
    dek = (meta.get("og:description") or meta.get("description") or "").strip()
    date = (meta.get("article:published_time") or "")[:10] or config.today()

    for bad in soup(["script", "style", "noscript", "nav", "header", "footer", "aside"]):
        bad.decompose()

    best, best_len = None, 0
    for el in soup.find_all(["article", "main", "div", "section"]):
        ps = el.find_all("p", recursive=True)
        n = sum(len(p.get_text(strip=True)) for p in ps)
        if len(ps) >= 4 and n > best_len:
            best, best_len = el, n
    if best is None:
        return None

    parts = []
    for el in best.find_all(["h2", "h3", "p", "li", "blockquote"]):
        txt = " ".join(el.get_text(" ", strip=True).split())
        if len(txt) < 25:
            continue
        if txt.startswith("Analytical & educational content"):
            continue          # vlastní upozornění doplníme sami a v angličtině
        if el.name in ("h2", "h3"):
            parts.append(f"### {txt}")
        elif el.name == "li":
            parts.append(f"- {txt}")
        elif el.name == "blockquote":
            parts.append(f"> {txt}")
        else:
            parts.append(txt)

    # odstranění opakujících se odstavců (patičky, upozornění)
    seen, body = set(), []
    for p in parts:
        if p in seen:
            continue
        seen.add(p)
        body.append(p)

    if len(" ".join(body).split()) < 150:
        return None

    return {"title": title, "dek": dek[:220], "date": date, "body": "\n\n".join(body), "url": url}


def run(limit: int | None = None) -> int:
    cfg = _cfg()
    if not cfg.get("enabled"):
        config.log("Import z QMA je vypnutý (data/site.yml → import.qma.enabled).")
        return 0

    state = config.load_state()
    seen = set(state.get("qma_urls", []))
    limit = limit if limit is not None else int(cfg.get("max_per_run", 5))
    lang = cfg.get("lang", "cs")
    section = cfg.get("section", "business")

    try:
        urls = _urls()
    except Exception as e:  # noqa: BLE001
        config.log(f"Sitemapu QMA se nepodařilo načíst: {str(e)[:140]}")
        return 0

    todo = [u for u in urls if u not in seen][:limit]
    config.log(f"QMA: v sitemapě {len(urls)} článků, nových {len([u for u in urls if u not in seen])}, "
               f"beru {len(todo)}.")

    taken = 0
    for url in todo:
        try:
            data = _extract(url)
        except Exception as e:  # noqa: BLE001
            config.log(f"  ! {url[-50:]}: {str(e)[:90]}")
            seen.add(url)
            continue
        if not data:
            config.log(f"  – přeskočeno (málo textu): {url[-50:]}")
            seen.add(url)
            continue

        body = data["body"]
        if cfg.get("add_disclaimer", True):
            body = body + "\n\n" + DISCLAIMER

        meta = {
            "slug": article.slugify(data["title"]),
            "title": data["title"],
            "dek": data["dek"] or data["title"],
            "section": section,
            "type": "imported",
            "depth": "open",
            "lang": lang,
            "date": data["date"],
            "status": "published",
            # Převzetí z vlastního sesterského webu není nezávislý fact-check.
            # Nula znamená „neskórováno“ a šablona proto neukáže zavádějící
            # odznak 100/100. Ověřené vlastní články skóruje až redakční pipeline.
            "confidence": 0,
            "image_query": " ".join(data["title"].split()[:5]),
            "origin": {
                "name": cfg.get("name", "QMA"),
                "url": data["url"],
                "note": cfg.get("note", ""),
            },
            "sources": [{"name": cfg.get("name", "QMA"), "url": data["url"]}],
        }
        article.save(meta, body)
        seen.add(url)
        taken += 1
        config.log(f"  ✓ {data['title'][:65]}")
        time.sleep(1.5)

    state["qma_urls"] = list(seen)[-2000:]
    config.save_state(state)
    config.log(f"Převzato {taken} vlastních článků z QMA.")
    return taken


if __name__ == "__main__":
    import sys
    run(int(sys.argv[1]) if len(sys.argv) > 1 else None)
