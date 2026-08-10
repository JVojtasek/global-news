"""Obálky článků — zdarma, vždy fungují, vždy vypadají stejně dobře.

Nepoužíváme generativní AI obrázky. Důvod je praktický i estetický:
generované obrázky stojí peníze, občas vypadají trapně a u zpravodajství
jsou eticky sporné. Místo toho děláme typografické obálky s barvou
odvozenou od rubriky — vypadá to jako záměr, ne jako nouzovka.

Kdo chce vlastní obrázek (třeba vygenerovaný v ChatGPT), stačí ho položit
do static/covers/<slug>.jpg a systém ho automaticky použije místo obálky.
"""
from __future__ import annotations

import hashlib
import json
import textwrap

from PIL import Image, ImageDraw, ImageFont

from . import config, imagebank

W, H = 1200, 630

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/liberation/",
]
SERIF_BOLD = ["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"]
SANS = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]

PALETTE = {
    "world":     ((16, 42, 67), (36, 84, 112)),
    "business":  ((30, 34, 30), (66, 78, 60)),
    "tech":      ((22, 32, 54), (52, 62, 110)),
    "science":   ((16, 46, 44), (34, 92, 84)),
    "health":    ((20, 44, 52), (44, 92, 100)),
    "culture":   ((44, 24, 44), (96, 52, 92)),
    "travel":    ((18, 40, 58), (46, 96, 118)),
    "motoring":  ((32, 32, 36), (72, 74, 84)),
    "sport":     ((20, 44, 30), (48, 96, 62)),
    "food":      ((48, 34, 22), (108, 76, 44)),
    "goodnews":  ((22, 48, 34), (54, 104, 70)),
    "history":   ((40, 30, 22), (104, 74, 44)),
    "questions": ((28, 26, 44), (66, 60, 100)),
    "meaning":   ((34, 28, 40), (82, 66, 96)),
    "relationships": ((48, 26, 38), (104, 56, 78)),
    "parenting": ((44, 36, 24), (100, 84, 52)),
    "wonder":    ((22, 30, 48), (58, 76, 112)),
    "ai":        ((18, 26, 40), (48, 66, 98)),
    "safety":    ((38, 24, 24), (86, 52, 48)),
}


def _font(names: list[str], size: int):
    for d in FONT_DIRS:
        for n in names:
            try:
                return ImageFont.truetype(d + n, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _gradient(section: str, seed: str) -> Image.Image:
    a, b = PALETTE.get(section, PALETTE["world"])
    shift = int(hashlib.sha1(seed.encode()).hexdigest()[:2], 16) - 128
    a = tuple(max(0, min(255, c + shift // 8)) for c in a)
    b = tuple(max(0, min(255, c + shift // 6)) for c in b)
    img = Image.new("RGB", (W, H), a)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return img


def cover(meta: dict, out_path) -> None:
    section = meta.get("section", "world")
    img = _gradient(section, meta.get("slug", ""))
    d = ImageDraw.Draw(img)

    # jemná mřížka, aby plocha nebyla mrtvá
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)

    title = meta.get("title", "")
    f_title = _font(SERIF_BOLD, 58 if len(title) < 60 else 46)
    f_small = _font(SANS, 24)

    wrapped = textwrap.wrap(title, width=30 if len(title) < 60 else 38)[:4]
    y = H // 2 - (len(wrapped) * (f_title.size + 14)) // 2 - 20
    for line in wrapped:
        d.text((80, y), line, font=f_title, fill=(255, 250, 244))
        y += f_title.size + 14

    label = next(
        (s["en"] for s in config.site()["sections"] if s["id"] == section), section
    ).upper()
    d.line([(80, 96), (140, 96)], fill=(255, 220, 160), width=3)
    d.text((80, 62), label, font=f_small, fill=(255, 220, 160))
    d.text((80, H - 70), config.site()["brand"]["name_en"], font=f_small, fill=(255, 255, 255, 180))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=86, optimize=True)


_downloaded = 0


def ensure(meta: dict) -> dict:
    """Zajistí obrázek k článku.

    Vrací {"src": cesta, "credit": text pod obrázkem nebo None}.
    Pořadí hledání je v data/site.yml → images.order.
    """
    global _downloaded
    slug = meta.get("slug", "x")
    out = config.PUBLIC / "img" / f"{slug}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    cache = config.DATA / "covers" / f"{slug}.jpg"
    credits = config.DATA / "covers" / f"{slug}.json"

    # 1) ruční obrázek, který jsi tam položil ty
    manual = config.STATIC / "covers" / f"{slug}.jpg"
    if manual.exists():
        out.write_bytes(manual.read_bytes())
        return {"src": f"{config.base_path()}/img/{slug}.jpg", "credit": None}

    # 2) obrázek stažený při některém dřívějším běhu
    if cache.exists():
        out.write_bytes(cache.read_bytes())
        cred = json.loads(credits.read_text(encoding="utf-8")) if credits.exists() else None
        return {"src": f"{config.base_path()}/img/{slug}.jpg", "credit": cred}

    # 3) volné zdroje na internetu
    cfg = config.site().get("images", {})
    limit = int(cfg.get("max_per_run", 12))
    if _downloaded < limit and "typographic" != cfg.get("order", [""])[0]:
        hit = imagebank.find(meta)
        if hit:
            cache.parent.mkdir(parents=True, exist_ok=True)
            if imagebank.download(hit, cache):
                _downloaded += 1
                cred = {
                    "text": f"{hit['author']} · {hit['license_label']}",
                    "url": hit["page"],
                    "provider": hit["provider"],
                }
                credits.write_text(json.dumps(cred, ensure_ascii=False), encoding="utf-8")
                out.write_bytes(cache.read_bytes())
                return {"src": f"{config.base_path()}/img/{slug}.jpg", "credit": cred}

    # 4) když se skutečná fotka nenašla
    if cfg.get("fallback", "none") == "typographic":
        cover(meta, out)
        return {"src": f"{config.base_path()}/img/{slug}.jpg", "credit": None}
    return {"src": None, "credit": None}
