"""Deterministický plán denního Evergreen Value Engine.

Tento modul nepoužívá AI ani placené API. Rozdělí práci mezi čtyři nové
hodnotové stránky, dvě aktualizace a jeden text do zásoby. Pilíře se střídají
deterministicky, takže redakce nevyrábí náhodnou směs článků.
"""
from __future__ import annotations

import datetime as dt
import json

import yaml

from . import config


def build(day: dt.date | None = None) -> dict:
    day = day or dt.date.today()
    site = config.site()
    auto = site.get("automation") or {}
    clusters = yaml.safe_load(
        (config.DATA / "evergreen_clusters.yml").read_text(encoding="utf-8")
    ) or {}
    pillars = clusters.get("pillars") or []
    if not pillars:
        raise ValueError("data/evergreen_clusters.yml neobsahuje žádné pilíře")
    step = max(1, int(auto.get("pillar_step", 1)))
    start = (day - dt.date(2026, 1, 1)).days % len(pillars)

    slots = []
    for spec in auto.get("public_slots", []):
        pillar = pillars[(start + (int(spec["slot"]) - 1) * step) % len(pillars)]
        slots.append({
            **spec,
            "pillar": pillar["id"],
            "section": pillar["section"],
            "candidate_clusters": [c["id"] for c in pillar.get("clusters", [])],
            "status": "draft",
        })

    for spec in auto.get("refresh_slots", []):
        pillar = pillars[(start + (int(spec["slot"]) - 1) * step) % len(pillars)]
        slots.append({
            **spec,
            "pillar": pillar["id"],
            "section": pillar["section"],
            "candidate_clusters": [c["id"] for c in pillar.get("clusters", [])],
            "status": "refresh-proposal",
        })

    reserve = dict(auto.get("reserve_slot") or {})
    if reserve:
        pillar = pillars[(start + len(slots) * step) % len(pillars)]
        reserve["pillar"] = pillar["id"]
        reserve["section"] = pillar["section"]
        reserve["candidate_clusters"] = [c["id"] for c in pillar.get("clusters", [])]
        reserve["status"] = "reserve"

    plan = {
        "date": day.isoformat(),
        "timezone": auto.get("timezone", "Europe/Prague"),
        "output_count": len(slots),
        "public_count": len([s for s in slots if s.get("action") == "new"]),
        "refresh_count": len([s for s in slots if s.get("action") == "refresh"]),
        "slots": slots,
        "reserve": reserve,
        "rules": {
            "unique_topics": True,
            "duplicate_window_days": 180,
            "evergreen_target_years": int((auto.get("value_gate") or {}).get("target_years", 3)),
            "minimum_value_score": int((auto.get("value_gate") or {}).get("minimum_score", 80)),
            "wider_lens_layers": ["EVIDENCE", "PERSPECTIVES"],
            "practical_asset_per_new_article": 1,
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
        "Four new value pages, two meaningful refreshes and one reserve feature.", "",
    ]
    for s in plan["slots"]:
        lines.append(
            f"- Slot {s['slot']}: `{s['action']}` · `{s['role']}` · "
            f"`{s['pillar']}` · `{s['section']}`"
            + (f" · `{s['type']}` · {s['min_words']}–{s['max_words']} words"
               if s.get("type") else f" · at least {s['min_words']} words")
        )
    if plan["reserve"]:
        s = plan["reserve"]
        lines.append(
            f"- Slot {s['slot']}: `{s['role']}` · `{s['section']}` · `{s['type']}` "
            f"· {s['min_words']}–{s['max_words']} words · reserve"
        )
    (config.DATA / "edition-plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    config.log(
        f"Plán vydání: {plan['public_count']} nové články + "
        f"{plan['refresh_count']} aktualizace + {1 if plan['reserve'] else 0} do zásoby."
    )
    return plan


if __name__ == "__main__":
    run()
