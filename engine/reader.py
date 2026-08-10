"""Váha článku — kolik psychické zátěže nese a čeho se týká.

K čemu to je: čtenář si na webu nastaví, kolik toho chce a jak natvrdo.
Aby to šlo, musí web o každém článku vědět dvě věci:

  load   0-100  jak těžké to je na čtení. 0 = recept na chleba,
                100 = mrtví, děti, násilí, katastrofa
  topics        štítky, které jde vypnout: war, crime, disaster,
                politics, health, money, tech

Počítá se to tady, ne v hlavičce článku, aby to platilo i pro převzaté
a starší texty. Když si autor v hlavičce nastaví `load:` sám, jeho
hodnota vyhrává.

Není to cenzura. Nic se nemaže. Jen se to řadí a v šetrném režimu se
místo celého textu ukáže shrnutí — a čtenář si kdykoli rozklikne zbytek.
"""
from __future__ import annotations

import re

# Slova, která zvedají zátěž. Váhy jsou schválně hrubé — nejde
# o přesnost na jednotky, jde o pořadí.
HEAVY = [
    (45, r"\b(?:killed|dead|deaths?|died|massacre|genocide|atrocity|execution)\b"),
    (35, r"\b(?:war|invasion|airstrike|bombing|shelling|offensive|militants?)\b"),
    (35, r"\b(?:rape|abuse|assault|torture|trafficking|abduct\w*)\b"),
    (30, r"\b(?:earthquake|tsunami|wildfire|hurricane|flooding|famine|epidemic|outbreak)\b"),
    (28, r"\b(?:shooting|stabbing|murder|homicide|terror\w*|hostage)\b"),
    (22, r"\b(?:crash|collision|derail\w*|explosion|collapse|evacuat\w*)\b"),
    (20, r"\b(?:cancer|tumour|tumor|overdose|suicide|self-harm|dementia)\b"),
    (18, r"\b(?:recession|layoffs?|redundanc\w*|bankrupt\w*|default)\b"),
    (15, r"\b(?:lawsuit|indicted|charged with|corruption|fraud|scandal)\b"),
    (12, r"\b(?:protests?|riot|crackdown|sanctions?|tariffs?|deportation)\b"),
    (10, r"\b(?:warning|threat|risk|crisis|emergency|shortage)\b"),
]

TOPIC_PATTERNS = {
    "war": r"\b(?:war|invasion|airstrike|bombing|shelling|militar\w*|troops?|missile|militants?|ceasefire)\b",
    "crime": r"\b(?:murder|shooting|stabbing|police|arrest\w*|court|trial|fraud|scam|prison)\b",
    "disaster": r"\b(?:earthquake|tsunami|wildfire|hurricane|typhoon|flood\w*|drought|famine|volcano|storm)\b",
    "politics": r"\b(?:election|parliament|senate|president|prime minister|party|vote|referendum|coalition|policy)\b",
    "health": r"\b(?:hospital|disease|virus|vaccine|cancer|patients?|trial|drug|therapy|mental health)\b",
    "money": r"\b(?:inflation|interest rate|market|stocks?|earnings|economy|tax|bank|price)\b",
    "tech": r"\b(?:software|algorithm|chip|robot|artificial intelligence|\bAI\b|data|app|platform)\b",
}

# Rubriky, které začínají níž nebo výš, ať to sedí i bez klíčových slov
SECTION_BASE = {
    "world": 34, "business": 20, "tech": 12, "science": 8, "health": 18,
    "culture": 8, "travel": 4, "motoring": 4, "sport": 6, "food": 2,
    "goodnews": 0, "history": 8, "questions": 12, "meaning": 12,
    "relationships": 14, "parenting": 12, "wonder": 2, "ai": 14,
    "safety": 16, "soul": 10,
}

# Co zátěž naopak snižuje: texty, které nabízejí řešení nebo návod
RELIEF = re.compile(
    r"\b(?:how to|what you can do|steps?|guide|recovered|recovery|improv\w+|"
    r"breakthrough|approved|cure|rescued|restored|solution|progress|"
    r"first time|record low|declin\w+ (?:in|of) (?:deaths|cases|poverty))\b",
    re.I,
)


def weigh(meta: dict, body: str = "") -> dict:
    """Vrátí {'load': int 0-100, 'topics': [str]} pro jeden článek."""
    if isinstance(meta.get("load"), int) and 0 <= meta["load"] <= 100:
        load = meta["load"]
    else:
        text = f"{meta.get('title','')} {meta.get('dek','')} {body[:3000]}"
        score = SECTION_BASE.get(meta.get("section", "world"), 15)
        for weight, pattern in HEAVY:
            hits = len(re.findall(pattern, text, re.I))
            if hits:
                score += weight * (1 if hits == 1 else 1.5 if hits < 4 else 2)
        if RELIEF.search(text):
            score -= 18
        # článek, který má shrnutí a návod, je snesitelnější
        if "## BRIEFLY" in body:
            score -= 6
        load = max(0, min(100, int(round(score))))

    topics = meta.get("topics")
    if not isinstance(topics, list) or not topics:
        text = f"{meta.get('title','')} {meta.get('dek','')} {body[:3000]}"
        topics = [k for k, pat in TOPIC_PATTERNS.items() if re.search(pat, text, re.I)]
        if meta.get("section") in ("goodnews", "wonder", "soul"):
            topics = [t for t in topics if t not in ("war", "crime", "disaster")]
    return {"load": load, "topics": topics[:4]}


def band(load: int) -> str:
    """Tři pásma, se kterými pracuje nastavení čtenáře."""
    return "light" if load < 30 else ("mid" if load < 58 else "heavy")
