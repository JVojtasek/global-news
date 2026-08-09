"""Přebírání celých článků ze zdrojů, které to výslovně dovolují.

Pravidla jsou v data/syndication.yml a systém je dodržuje doslova:
kde licence zakazuje překlad, článek se nepřeloží; kde zakazuje úpravy,
text se nezkracuje; kde nejsou fotky pod licencí, fotky se zahodí.

Ke každému převzatému článku se vždy připojí uvedení autora, zdroje
a licence — to je podmínka, bez které bychom neměli právo ho vydat.
"""
from __future__ import annotations

import datetime as dt
import re

import feedparser
import yaml
from bs4 import BeautifulSoup

from . import article, config

MAX_PER_SOURCE = 4


def _sources() -> list:
    p = config.DATA / "syndication.yml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else []


def _to_markdown(html: str, keep_images: bool) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for bad in soup(["script", "style", "iframe", "form", "aside"]):
        bad.decompose()
    if not keep_images:
        for img in soup(["img", "figure", "picture"]):
            img.decompose()

    out = []
    for el in soup.find_all(["h2", "h3", "p", "blockquote", "li", "img"]):
        if el.name == "img":
            src = el.get("src")
            if src:
                out.append(f"![]({src})")
            continue
        text = " ".join(el.get_text(" ", strip=True).split())
        if not text:
            continue
        if el.name in ("h2", "h3"):
            out.append(f"### {text}")
        elif el.name == "blockquote":
            out.append(f"> {text}")
        elif el.name == "li":
            out.append(f"- {text}")
        else:
            out.append(text)
    return "\n\n".join(out)


def _author(entry) -> str:
    for key in ("author", "dc_creator"):
        val = getattr(entry, key, None)
        if val:
            return re.sub(r"<[^>]+>", "", str(val)).strip()
    return "the original author"


def run(limit_per_source: int = MAX_PER_SOURCE) -> int:
    state = config.load_state()
    seen = set(state.get("syndicated_urls", []))
    taken = 0

    for src in _sources():
        try:
            feed = feedparser.parse(src["url"])
        except Exception as e:  # noqa: BLE001
            config.log(f"  ! {src['name']} nedostupný: {str(e)[:100]}")
            continue

        n = 0
        for entry in feed.entries:
            if n >= limit_per_source:
                break
            link = getattr(entry, "link", "")
            title = " ".join(getattr(entry, "title", "").split())
            if not link or not title or link in seen:
                continue

            html = ""
            if getattr(entry, "content", None):
                html = entry.content[0].get("value", "")
            if len(html) < 800:
                continue   # bez plného textu nemá cenu přebírat

            body = _to_markdown(html, src.get("keep_images", False))
            if len(body.split()) < 250:
                continue

            author = _author(entry)
            attribution = src["attribution"].format(author=author, url=link)

            meta = {
                "slug": article.slugify(title),
                "title": title,
                "dek": " ".join(re.sub(r"<[^>]+>", "", getattr(entry, "summary", ""))
                                .split())[:200] or title,
                "section": src.get("section", "world"),
                "type": "syndicated",
                "depth": "open",
                "lang": config.site()["languages"]["master"],
                "date": config.today(),
                "status": "published",
                "confidence": 100,
                "image_query": " ".join(title.split()[:6]),
                "syndicated": {
                    "source": src["name"],
                    "author": author,
                    "url": link,
                    "license": src["license"],
                    "license_url": src.get("license_url", ""),
                    "attribution": attribution,
                    "may_translate": bool(src.get("may_translate", False)),
                    "may_edit": bool(src.get("may_edit", False)),
                },
                "sources": [{"name": src["name"], "url": link}],
            }
            article.save(meta, body)
            seen.add(link)
            n += 1
            taken += 1
            config.log(f"  ✓ {src['name']}: {title[:60]}")

        if n:
            config.log(f"  {src['name']}: převzato {n} článků ({src['license']})")

    state["syndicated_urls"] = list(seen)[-2000:]
    state.setdefault("last_run", {})["syndicate"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    config.save_state(state)
    config.log(f"Celkem převzato {taken} článků.")
    return taken


if __name__ == "__main__":
    run()
