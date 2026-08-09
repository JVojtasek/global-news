"""Knihovna obrázků z volných zdrojů.

Nepoužíváme generativní AI. Hledáme skutečné fotografie a umělecká díla,
u kterých licence dovoluje použití — a vždy uvádíme autora a licenci.

Zdroje:
  1. static/covers/<slug>.jpg  — obrázek, který jsi tam položil ty
  2. data/images.json          — vlastní knihovna už jednou stažených obrázků
  3. Openverse                 — ~800 milionů volně licencovaných obrázků
  4. Wikimedia Commons         — mimo jiné veškeré klasické malířství
  5. typografická obálka       — vždy funguje, nikdy neselže

Licence, které přijímáme: public domain, CC0, CC BY, CC BY-SA.
Vše ostatní se zahodí. U CC BY a CC BY-SA se pod obrázkem zobrazí autor.
"""
from __future__ import annotations

import hashlib
import json
import re
import time

import requests

from . import config

UA = "TheDeeperStory/1.0 (newsroom bot; contact via site)"
LIB = config.DATA / "images.json"

LICENSE_LABEL = {
    "pdm": "public domain",
    "cc0": "CC0",
    "by": "CC BY",
    "by-sa": "CC BY-SA",
}


def _library() -> dict:
    return json.loads(LIB.read_text(encoding="utf-8")) if LIB.exists() else {}


def _save_library(lib: dict) -> None:
    LIB.write_text(json.dumps(lib, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def _keywords(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z]{4,}", text.lower())
    stop = {"with", "from", "that", "this", "have", "into", "over", "after", "says", "said",
            "will", "more", "than", "what", "when", "where", "which", "their", "about"}
    return [w for w in words if w not in stop][:5]


# ------------------------------------------------------------- Openverse
def _openverse(query: str, allowed: list[str]) -> dict | None:
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={
                "q": query,
                "license": ",".join(allowed),
                "size": "large",
                "page_size": 8,
                "mature": "false",
            },
            headers={"User-Agent": UA},
            timeout=25,
        )
        if r.status_code != 200:
            return None
        for item in r.json().get("results", []):
            url = item.get("url")
            lic = (item.get("license") or "").lower()
            if not url or lic not in allowed:
                continue
            return {
                "url": url,
                "license": lic,
                "license_label": LICENSE_LABEL.get(lic, lic.upper()),
                "author": item.get("creator") or "Unknown",
                "title": item.get("title") or "",
                "page": item.get("foreign_landing_url") or url,
                "provider": item.get("provider") or "Openverse",
                "source": "openverse",
            }
    except Exception as e:  # noqa: BLE001
        config.log(f"    Openverse nedostupný: {str(e)[:90]}")
    return None


# -------------------------------------------------------- Wikimedia Commons
def _wikimedia(query: str) -> dict | None:
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 8,
                "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1600,
            },
            headers={"User-Agent": UA},
            timeout=25,
        )
        if r.status_code != 200:
            return None
        pages = (r.json().get("query") or {}).get("pages") or {}
        for page in pages.values():
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            lic = (meta.get("LicenseShortName", {}).get("value") or "").lower()
            url = info.get("thumburl") or info.get("url")
            if not url:
                continue
            if "public domain" in lic or lic.startswith("pd") or "cc0" in lic:
                code = "pdm"
            elif "cc by-sa" in lic:
                code = "by-sa"
            elif "cc by" in lic:
                code = "by"
            else:
                continue
            author = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value") or "Unknown").strip()
            return {
                "url": url,
                "license": code,
                "license_label": meta.get("LicenseShortName", {}).get("value") or LICENSE_LABEL[code],
                "author": author[:120] or "Unknown",
                "title": page.get("title", "").replace("File:", ""),
                "page": info.get("descriptionurl") or url,
                "provider": "Wikimedia Commons",
                "source": "wikimedia",
            }
    except Exception as e:  # noqa: BLE001
        config.log(f"    Wikimedia nedostupná: {str(e)[:90]}")
    return None


# ------------------------------------------------------------------ API
def find(meta: dict) -> dict | None:
    """Najde vhodný obrázek. Vrací popis včetně licence, nebo None."""
    cfg = config.site().get("images", {})
    allowed = cfg.get("allowed_licenses", ["pdm", "cc0", "by", "by-sa"])
    order = cfg.get("order", ["library", "openverse", "wikimedia"])

    query = (meta.get("image_query") or "").strip()
    if not query:
        query = " ".join(_keywords(meta.get("title", "")))
    if not query:
        return None

    lib = _library()
    key = hashlib.sha1(query.lower().encode()).hexdigest()[:12]

    for step in order:
        if step == "library" and key in lib:
            config.log(f"    z knihovny: {query}")
            return lib[key]
        if step == "openverse":
            hit = _openverse(query, allowed)
        elif step == "wikimedia":
            hit = _wikimedia(query)
        else:
            continue
        if hit:
            hit["query"] = query
            lib[key] = hit
            _save_library(lib)
            config.log(f"    nalezeno ({hit['source']}): {hit['title'][:50]} · {hit['license_label']}")
            time.sleep(1)   # slušnost vůči cizím službám
            return hit
    return None


def download(hit: dict, out_path) -> bool:
    """Stáhne obrázek do public/. Vrátí False, když se to nepovede."""
    try:
        r = requests.get(hit["url"], headers={"User-Agent": UA}, timeout=60)
        if r.status_code != 200 or len(r.content) < 5000:
            return False
        from io import BytesIO

        from PIL import Image

        img = Image.open(BytesIO(r.content)).convert("RGB")
        img.thumbnail((1600, 1600))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "JPEG", quality=84, optimize=True)
        return True
    except Exception as e:  # noqa: BLE001
        config.log(f"    stažení selhalo: {str(e)[:90]}")
        return False
