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

    by_slot: dict[int, list] = {}
    for path in candidates:
        meta, body = article.parse(path.read_text(encoding="utf-8"))
        if meta.get("date") != date or not meta.get("automation_generated"):
            continue
        try:
            slot = int(meta.get("edition_slot") or 0)
        except (TypeError, ValueError):
            continue
        by_slot.setdefault(slot, []).append((meta, body, path))

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
        problems = inbox._edition_check(meta, body)
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
