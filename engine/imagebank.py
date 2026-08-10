"""Knihovna obrázků z volných zdrojů.

Nepoužíváme generativní AI. Hledáme skutečné fotografie a umělecká díla,
u kterých licence dovoluje použití — a vždy uvádíme autora a licenci.

Pořadí hledání je od nejpřesnějšího k nejobecnějšímu:

  1. static/covers/<slug>.jpg  — obrázek, který jsi tam položil ty
  2. data/images.json          — vlastní knihovna už jednou stažených obrázků
  3. Wikipedia — hlavní fotka článku o tématu. Tohle je nejlepší zdroj:
     když píšeme o Islandu, o inzulinu nebo o Amazonu, Wikipedie má
     k tomu tématu vybranou jednu dobrou fotku a je volně licencovaná.
  4. Openverse — ~800 milionů volně licencovaných fotek. Doplňujeme
     kontrolu, jestli výsledek vůbec souvisí s dotazem; bez ní to
     vracelo náhodné obrázky.
  5. Koncepční banka podle rubriky — ověřené obecné dotazy, které
     spolehlivě vracejí použitelnou fotku. Aby nebyly všechny články
     v rubrice stejné, vybírá se podle slugu.

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

UA = "MyPaper/1.0 (newsroom bot; contact via site)"
LIB = config.DATA / "images.json"

LICENSE_LABEL = {
    "pdm": "public domain",
    "cc0": "CC0",
    "by": "CC BY",
    "by-sa": "CC BY-SA",
}

STOP = {
    "with", "from", "that", "this", "have", "into", "over", "after", "says",
    "said", "will", "more", "than", "what", "when", "where", "which", "their",
    "about", "your", "just", "they", "them", "were", "been", "being", "some",
    "could", "would", "should", "there", "these", "those", "here", "much",
    "very", "many", "most", "také", "také", "does", "doing", "make", "made",
    "year", "years", "week", "day", "days", "time", "times", "first", "last",
    "new", "news", "how", "why", "who",
}

# Ověřené obecné dotazy. Každý z nich vrací v Openverse použitelné
# fotografie — vyzkoušeno. Pro rubriku se vybere podle slugu, aby
# se obrázky neopakovaly.
CONCEPTS = {
    "world": ["city skyline dusk", "crowded street market", "national flags united nations",
              "harbour cargo containers", "parliament building facade"],
    "business": ["stock exchange trading floor", "office skyscrapers glass", "shipping port cranes",
                 "factory production line", "coins and banknotes close up"],
    "tech": ["circuit board macro", "server room data centre", "smartphone in hand screen",
             "fibre optic cables light", "robot arm factory"],
    "science": ["laboratory glassware experiment", "microscope close up", "telescope night sky stars",
                "dna model molecule", "researcher pipette sample"],
    "health": ["hospital corridor", "stethoscope on table", "pharmacy medicine shelves",
               "running shoes park path", "fresh vegetables market stall"],
    "culture": ["art gallery interior visitors", "old library bookshelves", "theatre stage lights",
                "musician playing violin", "cinema seats screen"],
    "travel": ["mountain valley morning mist", "coastal cliffs sea", "old town narrow street",
               "train window landscape", "desert dunes sunset"],
    "motoring": ["highway aerial view", "electric car charging", "classic car detail chrome",
                 "car assembly robot", "mountain road curves"],
    "sport": ["empty stadium seats", "running track lanes", "football pitch grass",
              "swimming pool lanes", "cyclists road race"],
    "food": ["fresh bread bakery", "vegetables cutting board", "coffee cup wooden table",
             "market spices colourful", "family dinner table"],
    "goodnews": ["sunrise over field", "hands planting seedling", "volunteers community garden",
                 "dog rescue shelter", "children playing outdoors"],
    "history": ["ancient ruins columns", "archaeological excavation site", "old manuscript parchment",
                "medieval castle stone", "roman mosaic floor"],
    "questions": ["night sky milky way", "empty road horizon", "open book candlelight",
                  "person looking at stars", "labyrinth stone path"],
    "meaning": ["quiet window morning light", "walking forest path alone", "empty bench park autumn",
                "candle in dark room", "calm lake reflection"],
    "relationships": ["two people holding hands", "couple walking beach", "friends talking cafe",
                      "wedding rings on table", "two chairs facing each other"],
    "parenting": ["parent and child reading", "children playground", "family kitchen breakfast",
                  "toddler first steps", "school classroom desks"],
    "wonder": ["aurora borealis sky", "deep space nebula", "microscopic snowflake",
               "bioluminescent ocean", "storm clouds lightning"],
    "ai": ["neural network visualisation", "server room data centre", "robot hand detail",
           "computer code screen", "person using laptop office"],
    "safety": ["padlock on keyboard", "security camera wall", "phone screen warning",
               "server rack cables", "hand typing password"],
    "soul": ["quiet chapel light", "open old book pages", "sunrise through trees",
             "hands open palms up", "stone path through mist"],
}


def _library() -> dict:
    return json.loads(LIB.read_text(encoding="utf-8")) if LIB.exists() else {}


def _save_library(lib: dict) -> None:
    LIB.write_text(json.dumps(lib, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[A-Za-z]{4,}", (text or "").lower()) if w not in STOP]


def _proper_nouns(title: str) -> list[str]:
    """Vlastní jména z titulku — to je to, o čem článek doopravdy je."""
    # první slovo vynecháme, to je velké vždycky
    parts = re.findall(r"\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,})*", (title or "")[1:])
    return [p for p in parts if p.lower() not in STOP][:3]


# Fotky, které se na zpravodajský web nehodí, i když je licence v pořádku.
# Openverse i Commons obsahují lékařské a anatomické snímky, které se
# k obchodní zprávě dostanou přes jedno společné slovo.
BLOCK = re.compile(
    r"\b(?:nude|naked|nudity|breast|buttock|genital|erotic|porn|lingerie|"
    r"underwear|topless|bikini|anatomy of the|dissection|autopsy|corpse|"
    r"cadaver|wound|surgery|blood|injur\w*|skin lesion|tattoo on)\b", re.I)


def _decent(hit: dict) -> bool:
    hay = f"{hit.get('title','')} {hit.get('tags','')} {hit.get('url','')}"
    return not BLOCK.search(hay)


def _relevant(hit: dict, query: str) -> bool:
    """Souvisí nalezený obrázek vůbec s dotazem?

    Bez téhle kontroly vracela Openverse na dotaz „insulin price" fotku
    kočky. Stačí, aby se shodovalo jedno podstatné slovo.
    """
    q = set(_words(query))
    if not q:
        return True
    hay = set(_words(hit.get("title", "") + " " + hit.get("tags", "")))
    return bool(q & hay)


# ------------------------------------------------------------- Wikipedia
def _commons_license(filename: str) -> dict | None:
    """Zjistí licenci a autora souboru na Wikimedia Commons."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "titles": f"File:{filename}",
                "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1600,
            },
            headers={"User-Agent": UA}, timeout=25,
        )
        if r.status_code != 200:
            return None
        pages = (r.json().get("query") or {}).get("pages") or {}
        for page in pages.values():
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            lic = (meta.get("LicenseShortName", {}).get("value") or "").lower()
            if "public domain" in lic or lic.startswith("pd") or "cc0" in lic:
                code = "pdm"
            elif "cc by-sa" in lic:
                code = "by-sa"
            elif "cc by" in lic:
                code = "by"
            else:
                return None
            author = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value") or "Unknown").strip()
            return {
                "url": info.get("thumburl") or info.get("url"),
                "license": code,
                "license_label": meta.get("LicenseShortName", {}).get("value") or LICENSE_LABEL[code],
                "author": (author or "Unknown")[:120],
                "page": info.get("descriptionurl") or "",
            }
    except Exception as e:  # noqa: BLE001
        config.log(f"    Commons nedostupný: {str(e)[:90]}")
    return None


def _wikipedia_lead(query: str, allowed: list[str]) -> dict | None:
    """Hlavní fotka článku na Wikipedii o daném tématu.

    Tohle je nejpřesnější zdroj, jaký zadarmo máme: Wikipedie k tématu
    už jednu dobrou fotku vybrala a skoro vždy je z Commons.
    """
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": query, "gsrlimit": 3, "gsrnamespace": 0,
                "prop": "pageimages", "piprop": "original", "pilicense": "free",
            },
            headers={"User-Agent": UA}, timeout=25,
        )
        if r.status_code != 200:
            return None
        pages = (r.json().get("query") or {}).get("pages") or {}
        ordered = sorted(pages.values(), key=lambda p: p.get("index", 99))
        for page in ordered:
            src = (page.get("original") or {}).get("source")
            if not src or "/wikipedia/commons/" not in src:
                continue          # /wikipedia/en/ = fair use, nesmíme
            src = src.split("?", 1)[0]        # API připojuje utm_ parametry
            if src.lower().endswith((".svg", ".gif")):
                continue
            filename = requests.utils.unquote(src.rsplit("/", 1)[-1])
            lic = _commons_license(filename)
            if not lic or lic["license"] not in allowed or not lic["url"]:
                continue
            cand = {
                "url": lic["url"],
                "license": lic["license"],
                "license_label": lic["license_label"],
                "author": lic["author"],
                "title": page.get("title", ""),
                "page": lic["page"] or f"https://en.wikipedia.org/wiki/{page.get('title','').replace(' ','_')}",
                "provider": "Wikipedia / Wikimedia Commons",
                "source": "wikipedia",
            }
            if not _decent(cand):
                continue
            return cand
    except Exception as e:  # noqa: BLE001
        config.log(f"    Wikipedie nedostupná: {str(e)[:90]}")
    return None


# ------------------------------------------------------------- Openverse
def _openverse(query: str, allowed: list[str]) -> dict | None:
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={
                "q": query,
                "license": ",".join(allowed),
                "size": "large",
                "aspect_ratio": "wide",
                "page_size": 12,
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
            hit = {
                "url": url,
                "license": lic,
                "license_label": LICENSE_LABEL.get(lic, lic.upper()),
                "author": item.get("creator") or "Unknown",
                "title": item.get("title") or "",
                "tags": " ".join(t.get("name", "") for t in (item.get("tags") or [])[:12]),
                "page": item.get("foreign_landing_url") or url,
                "provider": item.get("provider") or "Openverse",
                "source": "openverse",
            }
            if not _relevant(hit, query) or not _decent(hit):
                continue
            hit.pop("tags", None)
            return hit
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
            cand = {
                "url": url,
                "license": code,
                "license_label": meta.get("LicenseShortName", {}).get("value") or LICENSE_LABEL[code],
                "author": author[:120] or "Unknown",
                "title": page.get("title", "").replace("File:", ""),
                "page": info.get("descriptionurl") or url,
                "provider": "Wikimedia Commons",
                "source": "wikimedia",
            }
            if not _decent(cand):
                continue
            return cand
    except Exception as e:  # noqa: BLE001
        config.log(f"    Wikimedia nedostupná: {str(e)[:90]}")
    return None


# ------------------------------------------------------------------ API
def _queries(meta: dict) -> list[tuple[str, bool]]:
    """Dotazy od nejpřesnějšího k nejobecnějšímu.

    Druhá hodnota říká, jestli je dotaz konkrétní (a smí se tedy hledat
    na Wikipedii), nebo je to obecný koncept (tam Wikipedie nedává smysl).
    """
    out: list[tuple[str, bool]] = []
    title = meta.get("title", "")
    english = meta.get("lang", "en") == "en"

    if english:
        for p in _proper_nouns(title):
            out.append((p, True))
    q = (meta.get("image_query") or "").strip()
    # Dotaz hledáme vždy anglicky. Český dotaz by na anglické Wikipedii
    # ani v Openverse nic rozumného nenašel.
    if q and q.isascii():
        out.append((q, True))
    if english:
        kws = _words(title)
        if len(kws) >= 2:
            out.append((" ".join(kws[:3]), True))
            out.append((" ".join(kws[:2]), True))

    section = meta.get("section", "world")
    pool = CONCEPTS.get(section) or CONCEPTS["world"]
    start = int(hashlib.sha1(meta.get("slug", "x").encode()).hexdigest()[:4], 16) % len(pool)
    for i in range(len(pool)):
        out.append((pool[(start + i) % len(pool)], False))

    seen, uniq = set(), []
    for q, specific in out:
        q = q.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            uniq.append((q, specific))
    return uniq


def find(meta: dict, skip: set | None = None) -> dict | None:
    """Najde vhodný obrázek. Vrací popis včetně licence, nebo None.

    `skip` jsou adresy fotek, které už na webu jsou. Dvakrát stejná
    fotka u dvou různých článků vypadá jako chyba, i když není.
    """
    skip = skip or set()
    cfg = config.site().get("images", {})
    allowed = cfg.get("allowed_licenses", ["pdm", "cc0", "by", "by-sa"])
    order = cfg.get("order", ["library", "wikipedia", "openverse", "wikimedia"])

    lib = _library()

    for query, specific in _queries(meta):
        key = hashlib.sha1(query.lower().encode()).hexdigest()[:12]
        for step in order:
            hit = None
            if step == "library":
                if key in lib and lib[key].get("url") not in skip:
                    config.log(f"    z knihovny: {query}")
                    return lib[key]
                continue
            if step == "wikipedia":
                if not specific:
                    continue
                hit = _wikipedia_lead(query, allowed)
            elif step == "openverse":
                hit = _openverse(query, allowed)
            elif step == "wikimedia":
                if not specific:
                    continue
                hit = _wikimedia(query)
            else:
                continue
            if hit and hit.get("url") in skip:
                hit = None
            if hit:
                hit["query"] = query
                lib[key] = hit
                _save_library(lib)
                config.log(
                    f"    nalezeno ({hit['source']}): {hit['title'][:46]} · {hit['license_label']}"
                )
                time.sleep(0.5)
                return hit
    return None


def download(hit: dict, out_path) -> bool:
    """Stáhne obrázek do public/. Vrátí False, když se to nepovede.

    Wikimedia při rychlém stahování vrací 429 („moc dotazů"). Není to
    chyba, jen se má počkat — tak počkáme a zkusíme to znovu.
    """
    try:
        r = None
        for attempt in range(4):
            r = requests.get(hit["url"], headers={"User-Agent": UA}, timeout=60)
            if r.status_code != 429:
                break
            time.sleep(4 * (attempt + 1))
        if r is None or r.status_code != 200 or len(r.content) < 5000:
            if r is not None and r.status_code != 200:
                config.log(f"    stažení {r.status_code}: {hit['url'][:70]}")
            return False
        from io import BytesIO

        from PIL import Image

        img = Image.open(BytesIO(r.content)).convert("RGB")
        if min(img.size) < 320:
            return False
        # 1200 px stačí i na velké obrazovky a stránka se načte dvakrát rychleji
        img.thumbnail((1200, 1200))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "JPEG", quality=78, optimize=True, progressive=True)
        return True
    except Exception as e:  # noqa: BLE001
        config.log(f"    stažení selhalo: {str(e)[:90]}")
        return False
