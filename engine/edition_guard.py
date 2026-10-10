"""Read-only completeness check for the scheduled daily edition.

The guard never invents content and never publishes it. It gives GitHub
Actions a clear failing signal when the research agenda or public slots are
missing on a planned close, while treating the reserve slot as a warning
rather than filler.

The edition day is Europe/Prague, the same clock frozen into
``data/edition-plan.json``. A GitHub runner's clock is UTC. Those two
dates differ only around midnight, never at the 09:35 UTC morning cron.

Not every run of workflow ``2 · Redakce`` is that close. The push filter
also matches a merge that rewrites older quizzes or the newsroom code.
On those runs the guard still reports the real gaps and then exits 0,
so inbox, release and the rest of the job can continue. A failing exit
is reserved for the daily cron and for a push that added today's quiz
file — the free signal that the morning hand-off is ready to publish.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from zoneinfo import ZoneInfo

from . import article, config, edition, inbox

# Stejné pásmo jako ``timezone`` v plánu vydání a v ``engine.morning``.
PRAGUE = ZoneInfo("Europe/Prague")
_UNSET = object()
_QUIZ_ADDED = re.compile(r"^data/quizzes/(\d{4}-\d{2}-\d{2})-[^/]+\.json$")


def edition_day(now: dt.datetime | None = None) -> dt.date:
    """Kalendářní den vydání podle hodin v Praze.

    Naivní čas se bere jako pražský. Čas s pásmem se do Prahy přepočte.
    """
    if now is None:
        now = dt.datetime.now(PRAGUE)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=PRAGUE)
    return now.astimezone(PRAGUE).date()


def push_adds_todays_quiz(event: dict | None, day: dt.date) -> bool:
    """Push přidal soubor ``data/quizzes/<den>-*.json``.

    To je signál poslední ranní úlohy. Úprava staršího kvízu, i když
    leží ve stejné složce, ten signál není.
    """
    date = day.isoformat()
    commits = []
    for commit in (event or {}).get("commits") or []:
        if isinstance(commit, dict):
            commits.append(commit)
    head = (event or {}).get("head_commit")
    if isinstance(head, dict):
        commits.append(head)
    for commit in commits:
        added = commit.get("added") or []
        if isinstance(added, str):
            added = [added]
        for path in added:
            normalized = str(path).replace("\\", "/").lstrip("./")
            match = _QUIZ_ADDED.match(normalized)
            if match and match.group(1) == date:
                return True
    return False


def should_block(event_name: str | None, event: dict | None, day: dt.date) -> bool:
    """Má chybějící veřejný slot shodit proces?

    Plánovaná uzávěrka je denní cron a push, který přidal dnešní kvíz.
    Lokální spuštění bez události GitHubu se chová jako dřív a blokuje.
    Všechno ostatní (sloučení opravy, ruční spuštění) jen ohlásí díry.
    """
    if not event_name:
        return True
    if event_name == "schedule":
        return True
    if event_name == "push":
        return push_adds_todays_quiz(event, day)
    return False


def _github_event() -> dict:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        return {}
    try:
        loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def inspect(day: dt.date | None = None) -> tuple[list[str], list[str]]:
    day = day or edition_day()
    date = day.isoformat()
    errors, warnings = [], []
    # Agenda je vstup pro pisatele, ne výstup vydání. Když sloty nakonec
    # vyšly i bez ní, na hotových novinách není nic špatně a nemá cenu
    # kvůli tomu shodit celou ranní úlohu — zvlášť když ta úloha teprve
    # přebírá články z inboxu a je to jediný krok, který díru zaplní.
    # 17. srpna 2026 přesně tohle nastalo: agenda nevznikla, tři sloty
    # se doplnily ručně, a hlídač zablokoval jejich převzetí.
    agenda = config.DATA / "daily-agenda" / f"{date}.md"
    if not agenda.exists():
        warnings.append(f"chybí výzkumná agenda {agenda.relative_to(config.ROOT)}")

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

    # Zmrazený plán z rána, ne přepočet. Jinak by hlídač soudil vydání
    # podle jiného zadání, než jaké pisatelé ráno dostali.
    plan = edition.today_plan(day)
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
        # Článek, který síto schválně zadrželo pro člověka (`status: review`),
        # není chyba vydání. Redakce svou práci odvedla a teď je na řadě
        # člověk. Kdyby to bylo tvrdá chyba, jeden citlivý text by shodil
        # celé ranní vydání — a přesně to se 17. srpna 2026 stalo: článek
        # o úmrtí konkrétního člověka uprostřed obvinění zůstal čekat na
        # rozhodnutí a zablokoval tím zbytek novin.
        if str(meta.get("status") or "").lower() == "review":
            warnings.append(
                f"slot {slot} čeká na člověka: {path.name} má status: review"
            )
            continue
        problems = inbox._edition_check(meta, body, allow_published=True)
        if problems:
            errors.append(f"{path.name}: {problems[0]}")
    return errors, warnings


def run(day: dt.date | None = None, event_name: str | None | object = _UNSET,
        event: dict | None | object = _UNSET) -> int:
    day = day or edition_day()
    if event_name is _UNSET:
        event_name = os.environ.get("GITHUB_EVENT_NAME") or None
    if event is _UNSET:
        event = _github_event()
    errors, warnings = inspect(day)
    # 10. října 2026 sloučení opravy starých kvízů spustilo workflow pushem,
    # protože filtr cest hlídá celé ``data/quizzes/**``. Checkout byl celý
    # a datum sedělo na 2026-10-10 — sloty v repozitáři opravdu chyběly.
    # Ranní cron téhož dne ty díry jen ohlásil. Push mimo ranní kvíz proto
    # nesmí uzávěrku shodit.
    blocking = should_block(
        None if event_name is None else str(event_name),
        event if isinstance(event, dict) else {},
        day,
    )
    for warning in warnings:
        config.log(f"⚠️  {warning}")
    if errors and not blocking:
        config.log(
            "Běh mimo plánovanou uzávěrku. Chybějící sloty se hlásí "
            "a redakce pokračuje. Blokuje jen denní cron a push, "
            "který přidal dnešní kvíz."
        )
        for error in errors:
            config.log(f"⚠️  {error}")
        return 0
    for error in errors:
        config.log(f"✗ {error}")
    if not errors:
        config.log("✓ Všech šest veřejných slotů je obsazeno."
                   + (" Agenda a zadržené texty jsou ve varováních výš."
                      if warnings else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(run())
