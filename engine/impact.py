"""Co ta zpráva znamená prakticky — pro peníze, zdraví a běžný život.

Tohle je ta „přidaná hodnota" v praxi. Zpráva sama o sobě je jen událost.
Teprve odpověď na otázku *a co z toho pro mě plyne* je něco, kvůli čemu
má cenu ji číst.

Kde se to bere:

1. Když má článek v hlavičce blok `impact:`, platí ten. Vyplňuje ho
   redakce (ranní směna) a je nejpřesnější.
2. Když ho nemá, ale má vrstvu `## BRIEFLY`, vytáhnou se z ní odstavce
   „Rizika a dopady" a „Co se s tím dá dělat". To je přesně ono a je to
   už jednou ověřené faktcheckem.
3. Když nemá ani to, článek se mezi praktickými dopady neukáže.
   Radši nic než vymyšlený dopad.

Oblasti schválně nejsou vymyšlené chytře — jsou to čtyři věci, na které
se lidé opravdu ptají: peníze, zdraví, každodenní život a bezpečí.
"""
from __future__ import annotations

import re

AREAS = ["money", "health", "life", "safety"]

AREA_RX = {
    "money": re.compile(
        r"\b(?:price|prices|inflation|cost|costs|tax|taxes|wage|wages|salary|"
        r"mortgage|rent|energy bill|tariff|tariffs|interest rate|pension|"
        r"subsidy|subsidies|fee|fees|cheaper|dearer|expensive|afford\w*)\b", re.I),
    "health": re.compile(
        r"\b(?:health|patients?|disease|vaccine|treatment|drug|drugs|hospital|"
        r"clinic|diagnosis|therapy|infection|air quality|pollution|asthma|"
        r"sleep|diet|exercise|mental health)\b", re.I),
    "life": re.compile(
        r"\b(?:school|schools|childcare|commute|travel|flight|flights|"
        r"housing|rent|job|jobs|employment|shortage|supply|queue|waiting|"
        r"internet access|electricity|water supply|transport)\b", re.I),
    "safety": re.compile(
        r"\b(?:scam|fraud|phishing|data breach|surveillance|privacy|password|"
        r"malware|hack\w*|stolen data|identity theft|recall|warning|unsafe)\b", re.I),
}

_LABEL = {
    "risks": re.compile(r"^\*\*(?:Risks and impact|Rizika a dopady)\.\*\*\s*(.+)$",
                        re.I | re.M),
    "todo": re.compile(r"^\*\*(?:What can be done|Co se s tím dá dělat)\.\*\*\s*(.+)$",
                       re.I | re.M),
}


def _briefly(body: str) -> str:
    m = re.search(r"^##\s*BRIEFLY\s*$(.*?)(?=^##\s|\Z)", body, re.S | re.M)
    return m.group(1) if m else ""


def read(meta: dict, body: str = "") -> dict | None:
    """Vrátí {'areas': [...], 'line': '…', 'todo': '…'} nebo None."""
    block = meta.get("impact")
    if isinstance(block, dict) and (block.get("line") or block.get("todo")):
        areas = [a for a in block.get("areas", []) if a in AREAS]
        line, todo = str(block.get("line", "")).strip(), str(block.get("todo", "")).strip()
    else:
        b = _briefly(body)
        if not b:
            return None
        mr = _LABEL["risks"].search(b)
        mt = _LABEL["todo"].search(b)
        if not mr:
            return None
        line = mr.group(1).strip()
        todo = mt.group(1).strip() if mt else ""
        areas = []

    if not areas:
        head = f"{meta.get('title','')} {meta.get('dek','')} {line} {todo}"
        rest = body[:4000]
        scored = [(len(rx.findall(head)) * 3 + len(rx.findall(rest)), a)
                  for a, rx in AREA_RX.items()]
        scored.sort(reverse=True)
        areas = [a for n, a in scored if n >= 2][:3] or [scored[0][1]]
    if not areas or not line:
        return None
    return {"areas": areas, "line": line[:420], "todo": todo[:420]}
