"""Paměť světa — dlouhodobý přehled o tom, co se kde vyvíjí.

Zpravodajství má krátkou paměť: každý den začíná znovu od nuly. Tenhle
modul je opak. Události, které spolu souvisejí, spojuje do **vláken**
(threads) a u každého vlákna si drží celou časovou osu.

Díky tomu systém ví věci, které z jednoho dne poznat nejdou:
  * tohle se letos stalo počtvrté
  * tahle věc byla v květnu popřena a teď se potvrdila
  * o tomhle tématu se tři týdny nemluvilo a najednou zase ano
  * tyhle dva zdroje si od začátku odporují

To je materiál pro původní analýzy, které jinde nenajdeš — a nestojí
to nic, protože je to jen práce s texty, které už máme uložené.
"""
from __future__ import annotations

import datetime as dt
import json
import re

from . import config

THREADS = config.DATA / "memory" / "threads.json"
STOP = set("""says said report reports live latest breaking update updates video watch after
before over under about into than then them they with from this that these those what when
where which their more most will would could should have been being also just than only""".split())

MATCH_MIN = 2          # kolik shodných vlastních jmen stačí na přiřazení
DORMANT_DAYS = 45      # po kolika dnech ticha se vlákno považuje za spící
ARCHIVE_DAYS = 200     # po kolika dnech se odloží stranou


def _entities(text: str) -> set:
    """Vlastní jména a významová slova z titulku."""
    out = set()
    for w in re.findall(r"\b[A-Z][A-Za-z'-]{2,}\b", text):
        lw = w.lower()
        if lw not in STOP and len(lw) > 3:
            out.add(lw)
    return out


def load() -> dict:
    if not THREADS.exists():
        return {"threads": [], "updated": ""}
    return json.loads(THREADS.read_text(encoding="utf-8"))


def save(mem: dict) -> None:
    THREADS.parent.mkdir(parents=True, exist_ok=True)
    mem["updated"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    THREADS.write_text(json.dumps(mem, ensure_ascii=False, indent=1), encoding="utf-8")


def _match(ents: set, thread: dict) -> int:
    return len(ents & set(thread["entities"]))


def update() -> dict:
    """Zanese dnešní události do dlouhodobé paměti."""
    ev_path = config.DATA / "events.json"
    if not ev_path.exists():
        config.log("Nejsou žádné události — paměť se nemění.")
        return load()

    events = json.loads(ev_path.read_text(encoding="utf-8"))
    mem = load()
    threads = mem["threads"]
    today = config.today()
    known_events = {e for t in threads for e in t.get("event_ids", [])}

    new_threads = 0
    updated_threads = set()

    for ev in events:
        if ev["id"] in known_events or ev["score"] < 40:
            continue
        ents = _entities(ev["headline"])
        if len(ents) < 2:
            continue

        best, best_score = None, 0
        for t in threads:
            sc = _match(ents, t)
            if sc > best_score:
                best, best_score = t, sc

        entry = {
            "date": today,
            "headline": ev["headline"],
            "sources": ev["sources_count"],
            "score": ev["score"],
            "event_id": ev["id"],
            "links": [i["url"] for i in ev["items"][:3]],
        }

        if best is not None and best_score >= MATCH_MIN:
            best["timeline"].append(entry)
            best["timeline"] = best["timeline"][-60:]
            best["entities"] = list(set(best["entities"]) | ents)[:40]
            best["event_ids"] = (best.get("event_ids", []) + [ev["id"]])[-200:]
            best["last_seen"] = today
            best["section"] = best.get("section") or ev["section"]
            updated_threads.add(best["id"])
        elif ev["score"] >= 55:
            threads.append({
                "id": ev["id"],
                "title": ev["headline"][:110],
                "section": ev["section"],
                "entities": list(ents)[:40],
                "event_ids": [ev["id"]],
                "first_seen": today,
                "last_seen": today,
                "timeline": [entry],
            })
            new_threads += 1

    # úklid
    cutoff_archive = (dt.date.today() - dt.timedelta(days=ARCHIVE_DAYS)).isoformat()
    threads[:] = [t for t in threads if t["last_seen"] >= cutoff_archive]
    threads.sort(key=lambda t: (t["last_seen"], len(t["timeline"])), reverse=True)
    mem["threads"] = threads[:400]

    save(mem)
    config.log(f"Paměť: {len(mem['threads'])} vláken "
               f"(nových {new_threads}, doplněných {len(updated_threads)}).")
    return mem


def active(days: int = 14, min_entries: int = 2) -> list:
    """Vlákna, která žijí — materiál pro analýzy."""
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    out = [t for t in load()["threads"]
           if t["last_seen"] >= cutoff and len(t["timeline"]) >= min_entries]
    out.sort(key=lambda t: (len(t["timeline"]), t["last_seen"]), reverse=True)
    return out


def dormant(days: int = DORMANT_DAYS) -> list:
    """Vlákna, o kterých se přestalo mluvit — často zajímavější než ta hlasitá."""
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    return [t for t in load()["threads"]
            if t["last_seen"] < cutoff and len(t["timeline"]) >= 3]


def describe(thread: dict, max_entries: int = 12) -> str:
    """Vlákno v čitelné podobě pro AI analytika."""
    lines = [f"VLÁKNO: {thread['title']}",
             f"rubrika: {thread['section']} · sledováno od {thread['first_seen']} "
             f"· záznamů: {len(thread['timeline'])}"]
    for e in thread["timeline"][-max_entries:]:
        lines.append(f"  {e['date']}  ({e['sources']} zdrojů, síla {e['score']})  {e['headline']}")
    return "\n".join(lines)


if __name__ == "__main__":
    update()
