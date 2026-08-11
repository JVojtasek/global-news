"""Čisté redakční bezpečnostní funkce bez sítě a AI závislostí."""
from __future__ import annotations

import re


PROVENANCE_FIELDS = (
    "sources", "type", "section", "depth", "origin", "syndicated",
    "author", "byline", "review", "access", "tier",
)

SENSITIVE_TRIGGERS = {
    "prophecy": ("prophecy", "fulfil", "fulfill", "end times", "antichrist", "rapture", "revelation"),
    "death_toll": ("killed", "dead", "death toll", "casualties", "massacre"),
    "accusation": ("accused", "alleged", "allegation", "charged with", "fraud", "corruption"),
    "abuse": ("abuse", "assault", "rape", "trafficking"),
    "election": ("election", "vote", "ballot", "opinion poll", "candidate", "campaign"),
    # Obecné wellbeing texty nejsou samy o sobě medicínou. Lidskou kontrolu
    # vyžaduje až diagnóza, nemoc, léčba nebo konkrétní klinické tvrzení.
    "medical": ("doctor", "physician", "disease", "cancer", "diabetes", "drug", "medicine",
                "medication", "treatment", "diagnosis", "symptom", "vaccine", "therapy",
                "depression", "anxiety", "disorder", "dosage"),
    "financial": ("invest", "investing", "investment", "stock", "bond", "crypto", "trading",
                  "buy shares", "sell shares", "portfolio", "dividend", "promised return"),
    "children": ("child", "children", "toddler", "baby", "teen", "teenager", "parenting",
                 "school", "student", "minor"),
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
        any(re.search(rf"\b{re.escape(phrase)}\b", lowered) for phrase in phrases)
        for category, phrases in SENSITIVE_TRIGGERS.items()
        if category in enabled_categories
    )
