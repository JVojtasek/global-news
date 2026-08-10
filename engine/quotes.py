"""Myšlenka dne a Poslední slovo.

Záměrně **bez cizí služby**. Seznam je v data/quotes.yml a obsahuje
jen autory, jejichž dílo je ve veřejném vlastnictví — takže je právně
čisté je citovat a žádná externí databáze nám nemůže spadnout ani
podstrčit podvrh (těch po internetu koluje víc než pravých citátů).

Výběr se řídí datem, takže stejný den má stejný citát a nemění se
při každé přestavbě webu.
"""
from __future__ import annotations

import datetime as dt
import hashlib

import yaml

from . import config


def _all() -> list:
    p = config.DATA / "quotes.yml"
    if not p.exists():
        return []
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or []
    except Exception:  # noqa: BLE001
        return []


def _pick(kind: str, salt: str = "") -> dict | None:
    pool = [q for q in _all() if q.get("kind") == kind and q.get("text")]
    if not pool:
        return None
    day = dt.date.today().isoformat()
    idx = int(hashlib.sha1((day + salt + kind).encode()).hexdigest()[:8], 16) % len(pool)
    return pool[idx]


def thought() -> dict | None:
    """Myšlenka dne do postranního sloupce."""
    return _pick("thought")


def wit() -> dict | None:
    """Poslední slovo — citát s humorem do patičky."""
    return _pick("wit")


if __name__ == "__main__":
    t, w = thought(), wit()
    print("MYŠLENKA DNE:")
    print(f'  „{t["text"]}“\n  — {t["author"]}' if t else "  (nic)")
    print("\nPOSLEDNÍ SLOVO:")
    print(f'  „{w["text"]}“\n  — {w["author"]}' if w else "  (nic)")
