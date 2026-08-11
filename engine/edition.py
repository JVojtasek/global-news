"""Deterministický plán sedmi samostatných ranních redakčních úloh.

Tento modul nepoužívá AI ani placené API. Jen rozdělí dnešní práci mezi
šest veřejných článků a jeden text do zásoby tak, aby se rubriky střídaly,
neopakovala se jedna oblast a naplánované úlohy měly jednoznačný kontrakt.
"""
from __future__ import annotations

import datetime as dt
import json

from . import config


def build(day: dt.date | None = None) -> dict:
    day = day or dt.date.today()
    site = config.site()
    auto = site.get("automation") or {}
    rotation = site["editorial"].get("daily_feature", {}).get("rotation") or ["meaning"]
    step = max(1, int(auto.get("section_step", 3)))
    start = (day - dt.date(2026, 1, 1)).days % len(rotation)

    slots = []
    used = set()
    for spec in auto.get("public_slots", []):
        idx = (start + (int(spec["slot"]) - 1) * step) % len(rotation)
        # Když délka rotace a krok vytvoří kolizi, posuneme se na nejbližší
        # dosud nepoužitou rubriku. Plán tak vždy obsahuje šest různých oblastí.
        for _ in range(len(rotation)):
            section = rotation[idx]
            if section not in used:
                break
            idx = (idx + 1) % len(rotation)
        used.add(section)
        slots.append({**spec, "section": section, "status": "draft"})

    reserve = dict(auto.get("reserve_slot") or {})
    if reserve:
        idx = (start + len(slots) * step) % len(rotation)
        reserve["section"] = rotation[idx]
        reserve["status"] = "reserve"

    plan = {
        "date": day.isoformat(),
        "timezone": auto.get("timezone", "Europe/Prague"),
        "public_count": len(slots),
        "slots": slots,
        "reserve": reserve,
        "rules": {
            "unique_topics": True,
            "recent_article_window_days": 14,
            "wider_lens_layers": ["EVIDENCE", "PERSPECTIVES"],
            "quiz_per_public_article": 1,
        },
    }
    return plan


def run() -> dict:
    plan = build()
    (config.DATA / "edition-plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        f"# MY PAPER EDITION PLAN — {plan['date']}", "",
        "Six original public analyses plus one reserve feature.", "",
    ]
    for s in plan["slots"]:
        lines.append(
            f"- Slot {s['slot']}: `{s['role']}` · `{s['section']}` · `{s['type']}` "
            f"· {s['min_words']}–{s['max_words']} words"
        )
    if plan["reserve"]:
        s = plan["reserve"]
        lines.append(
            f"- Slot {s['slot']}: `{s['role']}` · `{s['section']}` · `{s['type']}` "
            f"· {s['min_words']}–{s['max_words']} words · reserve"
        )
    (config.DATA / "edition-plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    config.log(f"Plán vydání: {len(plan['slots'])} veřejných článků + "
               f"{1 if plan['reserve'] else 0} do zásoby.")
    return plan


if __name__ == "__main__":
    run()
