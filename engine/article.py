"""Práce s článkem jako souborem: čtení, zápis, hlavička, validace."""
from __future__ import annotations

import datetime as dt
import re
import unicodedata

import yaml

from . import config

LAYERS = ["FACTS", "CONTEXT", "PEOPLE", "DEEPER", "REFLECT"]
REQUIRED_LAYERS = ["FACTS", "CONTEXT", "DEEPER"]
# starší názvy vrstev, aby fungovaly i dřív napsané články
ALIASES = {"SCRIPTURE": "DEEPER", "RESPONSE": "REFLECT", "BACKGROUND": "CONTEXT"}

LAYER_LABELS = {
    "en": {
        "FACTS": ("What happened", ""),
        "CONTEXT": ("The background", ""),
        "PEOPLE": ("Who it touches", ""),
        "DEEPER": ("The deeper story", ""),
        "REFLECT": ("Something to sit with", ""),
    },
    "cs": {
        "FACTS": ("Co se stalo", ""),
        "CONTEXT": ("Souvislosti", ""),
        "PEOPLE": ("Koho se to týká", ""),
        "DEEPER": ("Hlubší příběh", ""),
        "REFLECT": ("K zamyšlení", ""),
    },
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)[:70] or "article"


def parse(raw: str) -> tuple[dict, str]:
    """Rozdělí soubor na hlavičku (dict) a tělo (markdown)."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:markdown|md)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        return {}, raw
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return _coerce(meta), m.group(2).strip()


def _coerce(meta: dict) -> dict:
    """YAML si z `date: 2026-08-10` udělá datum, ne text.

    Celý systém s daty pracuje jako s řetězci, takže je tady srovnáme.
    Bez toho spadne stavba webu, jakmile někdo napíše datum bez uvozovek.
    """
    import datetime as _dt

    for key, val in list(meta.items()):
        if isinstance(val, (_dt.datetime, _dt.date)):
            meta[key] = val.isoformat()[:10]
        elif isinstance(val, list):
            meta[key] = [
                v.isoformat()[:10] if isinstance(v, (_dt.datetime, _dt.date)) else v
                for v in val
            ]
    return meta


def dump(meta: dict, body: str) -> str:
    head = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{head}\n---\n\n{body.strip()}\n"


def sections(body: str) -> dict:
    """Rozseká tělo na vrstvy podle ## NADPISŮ."""
    out, current = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+([A-Z][A-Z ]+)\s*$", line.strip())
        if m:
            name = ALIASES.get(m.group(1).strip(), m.group(1).strip())
            if name in LAYERS:
                current = name
                out[current] = []
                continue
        if current:
            out[current].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def validate(meta: dict, body: str) -> list[str]:
    """Vrátí seznam problémů. Prázdný seznam = článek je v pořádku."""
    problems = []
    for field in ("title", "section", "type", "lang"):
        if not meta.get(field):
            problems.append(f"chybí pole '{field}' v hlavičce")
    secs = sections(body)
    for layer in REQUIRED_LAYERS:
        if layer not in secs:
            problems.append(f"chybí povinná sekce ## {layer}")
    for layer, text in secs.items():
        if len(text.split()) < 25:
            problems.append(f"sekce ## {layer} je příliš krátká ({len(text.split())} slov)")
    valid_sections = {s["id"] for s in config.site()["sections"]}
    if meta.get("section") not in valid_sections:
        problems.append(f"neznámá rubrika '{meta.get('section')}'")
    if meta.get("type") == "news" and not meta.get("sources"):
        problems.append("zpravodajský článek bez uvedených zdrojů")
    return problems


def normalise(meta: dict, body: str, *, defaults: dict | None = None) -> tuple[dict, str]:
    d = defaults or {}
    meta.setdefault("date", d.get("date", config.today()))
    meta.setdefault("lang", config.site()["languages"]["master"])
    meta.setdefault("type", d.get("type", "news"))
    meta.setdefault("section", d.get("section", "world"))
    meta.setdefault("status", "draft")
    meta.setdefault("confidence", 0)
    meta.setdefault("depth", d.get("depth", "open"))
    meta.setdefault("image_query", "")
    meta.setdefault("sources", [])
    if not meta.get("slug"):
        meta["slug"] = slugify(str(meta.get("title", "")) or d.get("id", "article"))
    for k, v in d.items():
        meta.setdefault(k, v)
    return meta, body


def path_for(meta: dict) -> "config.pathlib.Path":
    return config.CONTENT / meta["lang"] / f"{meta['date']}-{meta['slug']}.md"


def save(meta: dict, body: str) -> "config.pathlib.Path":
    p = path_for(meta)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump(meta, body), encoding="utf-8")
    return p


def load_all(lang: str) -> list[tuple[dict, str, "config.pathlib.Path"]]:
    out = []
    d = config.CONTENT / lang
    if not d.exists():
        return out
    for p in sorted(d.glob("*.md")):
        meta, body = parse(p.read_text(encoding="utf-8"))
        if meta:
            out.append((meta, body, p))
    return out
