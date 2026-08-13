"""Read-only completeness check for the scheduled daily edition.

The guard never invents content and never publishes it. It gives GitHub
Actions a clear failing signal when the research agenda or public slots are
missing, while treating the reserve slot as a warning rather than filler.
"""
from __future__ import annotations

import datetime as dt

from . import article, config, edition, inbox


def inspect(day: dt.date | None = None) -> tuple[list[str], list[str]]:
    day = day or dt.date.today()
    date = day.isoformat()
    errors, warnings = [], []
    agenda = config.DATA / "daily-agenda" / f"{date}.md"
    if not agenda.exists():
        errors.append(f"chybí výzkumná agenda {agenda.relative_to(config.ROOT)}")

    candidates = []
    for path in (config.CONTENT / "inbox").glob("*.md"):
        candidates.append(path)
    for lang_dir in config.CONTENT.iterdir():
        if lang_dir.is_dir() and lang_dir.name != "inbox":
            candidates.extend(lang_dir.glob(f"{date}-*.md"))

    # Vydání se plánuje v jazyce originálu; překlady se posuzují jinde.
    master = str(config.site()["languages"]["master"])
    by_slot: dict[int, list] = {}
    strays: dict[tuple, list] = {}
    for path in candidates:
        meta, body = article.parse(path.read_text(encoding="utf-8"))
        if meta.get("date") != date:
            continue
        try:
            slot = int(meta.get("edition_slot") or 0)
        except (TypeError, ValueError):
            continue
        # Cizí článek, který si vzal číslo slotu, se nesmí přehlédnout.
        # 12. srpna 2026 dvě zprávy ze světa nesly `edition_slot: 1` a `2`
        # s `automation_generated: false`. Hlídač je přeskočil, ohlásil
        # vydání jako kompletní — a sloty 5 a 6 ten den nevyšly vůbec.
        # Obsazenost se proto počítá ze všech souborů, redakční smlouva
        # se pak kontroluje jen u těch automatických.
        # Překlad není druhý článek. Bez jazyka v klíči by hlídač hlásil
        # každý přeložený slot jako obsazený dvakrát — a protože čeština
        # zaostává, projevilo by se to až v den, kdy se překlad doplní.
        lang = str(meta.get("lang") or "en")
        if lang != master:
            continue
        if not meta.get("automation_generated"):
            if slot > 0:
                strays.setdefault((lang, slot), []).append(path)
            continue
        by_slot.setdefault(slot, []).append((meta, body, path))

    for (lang, slot), paths in sorted(strays.items()):
        names = ", ".join(sorted(x.name for x in paths))
        errors.append(
            f"slot {slot} ({lang}) si vzal článek, který do vydání nepatří "
            f"(automation_generated: false): {names}"
        )

    plan = edition.build(day)
    specs = list(plan.get("slots") or [])
    if plan.get("reserve"):
        specs.append(plan["reserve"])
    for spec in specs:
        slot = int(spec["slot"])
        rows = by_slot.get(slot, [])
        if not rows:
            message = f"chybí automatický slot {slot} ({spec['section']}/{spec['type']})"
            (warnings if slot == 7 else errors).append(message)
            continue
        if len(rows) > 1:
            errors.append(f"slot {slot} je obsazen {len(rows)}krát")
            continue
        meta, body, path = rows[0]
        # The inbox gate validates the incoming state (draft/reserve). This
        # guard also inspects files that the gate has already promoted to
        # ``published``, so it validates the same editorial contract while
        # accepting that legitimate final-state transition.
        problems = inbox._edition_check(meta, body, allow_published=True)
        if problems:
            errors.append(f"{path.name}: {problems[0]}")
    return errors, warnings


def run(day: dt.date | None = None) -> int:
    errors, warnings = inspect(day)
    for warning in warnings:
        config.log(f"⚠️  {warning}")
    for error in errors:
        config.log(f"✗ {error}")
    if not errors:
        config.log("✓ Denní agenda a všech šest veřejných slotů jsou kompletní.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(run())
