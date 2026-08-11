"""Čisté redakční bezpečnostní funkce bez sítě a AI závislostí."""
from __future__ import annotations


PROVENANCE_FIELDS = (
    "sources", "type", "section", "depth", "origin", "syndicated",
    "author", "byline", "review", "access", "tier",
)

SENSITIVE_TRIGGERS = {
    "prophecy": "prophecy fulfil fulfill end times antichrist rapture revelation beast",
    "death_toll": "killed dead death toll casualties massacre",
    "accusation": "accused alleged allegation charged fraud corruption",
    "abuse": "abuse assault rape trafficking",
    "election": "election vote ballot poll candidate campaign",
    "medical": "health doctor disease cancer diabetes drug medicine treatment diagnosis symptom vaccine therapy",
    "financial": "invest investing investment stock bond crypto trading buy sell portfolio return dividend",
    "children": "child children toddler baby teen teenager parenting school student minor",
}


def translation_allowed(meta: dict) -> bool:
    """Vrátí False, pokud licence převzatého článku překlad zakazuje."""
    syndicated = meta.get("syndicated") or {}
    return not syndicated or bool(syndicated.get("may_translate", False))


def copy_provenance(source: dict, target: dict, *, source_lang: str) -> dict:
    """Přenese redakční a licenční metadata z originálu do překladu."""
    for field in PROVENANCE_FIELDS:
        if field in source:
            target[field] = source[field]
    target["translated_from"] = source_lang
    return target


def is_sensitive(text: str, enabled_categories: set[str]) -> bool:
    """Rozpozná témata, která musí čekat na lidskou kontrolu."""
    lowered = text.lower()
    return any(
        any(word in lowered for word in words.split())
        for category, words in SENSITIVE_TRIGGERS.items()
        if category in enabled_categories
    )
