"""Deterministický plán sedmi samostatných ranních redakčních úloh.

Tento modul nepoužívá AI ani placené API. Jen rozdělí dnešní práci mezi
šest veřejných článků a jeden text do zásoby tak, aby se rubriky střídaly,
neopakovala se jedna oblast a naplánované úlohy měly jednoznačný kontrakt.
"""
from __future__ import annotations

import datetime as dt
import json

from . import article, config

# Kolik dní zpátky se počítá, jak je která rubrika nasycená.
HUNGER_WINDOW = 21
# Kolik hladových rubrik smí být v jednom vydání. Bez tohohle stropu by
# se po přidání nové rubriky několik dní po sobě vydávaly noviny složené
# jen z ní — což je sice spravedlivé, ale číst se to nedá.
HUNGRY_PER_EDITION = 2


def _coverage(day: dt.date, window: int = HUNGER_WINDOW) -> dict:
    """Kolik článků každá rubrika dostala za poslední tři týdny.

    Rotace sama o sobě je slepá: jede pořád dokola bez ohledu na to, co
    do rubrik nateklo odjinud — z přebírání, z QMA, z intradenních analýz.
    Proto byznys 17. srpna 2026 držel 63 článků, zatímco cestování, jídlo,
    sport a motorismus nulu. Tenhle výpočet dá plánu oči.
    """
    cut = (day - dt.timedelta(days=window)).isoformat()
    seen: dict[str, int] = {}
    try:
        lang = config.site()["languages"]["master"]
        for meta, _body, _path in article.load_all(lang):
            if meta.get("status") != "published":
                continue
            if str(meta.get("date") or "") < cut:
                continue
            sec = str(meta.get("section") or "")
            if sec:
                seen[sec] = seen.get(sec, 0) + 1
    except Exception:
        # Když se obsah z jakéhokoli důvodu nedá přečíst, plán se musí
        # postavit stejně. Beze změny se prostě vrátíme k čisté rotaci.
        return {}
    return seen


def _order(rotation: list, day: dt.date, start: int) -> list:
    """Pořadí rubrik pro dnešek: napřed pár hladových, pak obvyklá rotace.

    Řazení je čistě deterministické — stejný den a stejný obsah dá vždycky
    stejný plán, takže se dá zpětně ověřit, proč co vyšlo.
    """
    cover = _coverage(day)
    if not cover:
        return [rotation[(start + i) % len(rotation)] for i in range(len(rotation))]

    cycle = [rotation[(start + i) % len(rotation)] for i in range(len(rotation))]
    # Hladová je rubrika, která za tři týdny dostala nejvýš jeden článek.
    hungry = [s for s in cycle if cover.get(s, 0) <= 1]
    hungry.sort(key=lambda s: (cover.get(s, 0), cycle.index(s)))
    picked = hungry[:HUNGRY_PER_EDITION]
    return picked + [s for s in cycle if s not in picked]


def build(day: dt.date | None = None) -> dict:
    day = day or dt.date.today()
    site = config.site()
    auto = site.get("automation") or {}
    rotation = site["editorial"].get("daily_feature", {}).get("rotation") or ["meaning"]
    start = (day - dt.date(2026, 1, 1)).days % len(rotation)

    # Pořadí už není slepý cyklus — napřed přijdou rubriky, které dlouho
    # nic nedostaly. Krok `section_step` se tím stává zbytečným, pořadí
    # určuje hlad a za ním obvyklá rotace.
    order = _order(list(rotation), day, start)

    slots = []
    used = set()
    for spec in auto.get("public_slots", []):
        section = next((x for x in order if x not in used), order[0])
        used.add(section)
        slots.append({**spec, "section": section, "status": "draft"})

    reserve = dict(auto.get("reserve_slot") or {})
    if reserve:
        reserve["section"] = next((x for x in order if x not in used), order[0])
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


def today_plan(day: dt.date | None = None) -> dict:
    """Plán, podle kterého se dnešek opravdu psal.

    Tohle je důležitější, než vypadá. Od chvíle, kdy se pořadí rubrik
    řídí tím, co už vyšlo, by `build()` vrátil během dne pokaždé něco
    jiného — ráno by pisatelům zadal cestování, a když by cestování
    vyšlo, odpoledne by hlídač vyžadoval rubriku jinou a vydání by
    označil za špatné. Plán se proto **zmrazí**: jakmile ho ranní úloha
    zapíše do `data/edition-plan.json`, platí ten a nic ho ten den
    nepřepíše.

    Když soubor chybí nebo je z jiného dne, spočítá se znovu.
    """
    day = day or dt.date.today()
    path = config.DATA / "edition-plan.json"
    if path.exists():
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
            if stored.get("date") == day.isoformat() and stored.get("slots"):
                return stored
        except (ValueError, OSError):
            pass
    return build(day)


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
