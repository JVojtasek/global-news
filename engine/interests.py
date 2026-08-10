"""Štítky zájmů — podle čeho web pozná, komu který článek nabídnout.

Čtenář si při první návštěvě naklikne, co ho zajímá. Aby to k něčemu
bylo, musí web u každého článku vědět, do kterých škatulek patří.
Počítá se to tady, při stavbě webu, ze slovníku v `data/interests.yml`.

Dvě věci, které je potřeba mít pořád na paměti:

1. **Zájmy čtenáře nikdy neopustí jeho zařízení.** Web je statický,
   nemá databázi ani účty. Řazení dělá prohlížeč sám nad seznamem
   článků, který je stejný pro všechny. My se nedozvíme nic.

2. **Zdravotní zájmy nejsou diagnóza.** Když si někdo zaškrtne cukrovku,
   znamená to „tohle mě zajímá", ne „tohle mám". Web mu proto nikdy
   nic nedoporučuje ani neradí — jen dřív ukáže výzkum, prevenci
   a praktické informace a vždy uvede zdroj.
"""
from __future__ import annotations

import re

import yaml

from . import config

_cache: dict = {}


def catalogue() -> list:
    """Skupiny zájmů z data/interests.yml."""
    if "cat" not in _cache:
        p = config.DATA / "interests.yml"
        data = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
        _cache["cat"] = data.get("groups", [])
    return _cache["cat"]


def _compiled() -> list[tuple[str, re.Pattern]]:
    if "rx" not in _cache:
        out = []
        for g in catalogue():
            for it in g.get("items", []):
                if it.get("match"):
                    # slova hledáme jako celá slova, jinak „chef" najde
                    # „Scheffler" a štítky jsou k ničemu
                    out.append((it["id"], re.compile(rf"\b(?:{it['match']})\b", re.I)))
        _cache["rx"] = out
    return _cache["rx"]


def tags(meta: dict, body: str = "") -> list[str]:
    """Do kterých zájmů článek spadá. Titulek váží víc než tělo."""
    if isinstance(meta.get("interests"), list) and meta["interests"]:
        return [str(t) for t in meta["interests"]][:8]

    head = f"{meta.get('title','')} {meta.get('dek','')} {meta.get('image_query','')}"
    text = body[:6000]
    scored: list[tuple[int, str]] = []
    for tag, rx in _compiled():
        n = len(rx.findall(head)) * 3 + len(rx.findall(text))
        if n >= 3:                      # jeden náhodný výskyt nestačí
            scored.append((n, tag))
    scored.sort(reverse=True)
    return [t for _, t in scored[:5]]


def health_ids() -> set[str]:
    return {
        it["id"]
        for g in catalogue()
        if g.get("id") == "health"
        for it in g.get("items", [])
    }
