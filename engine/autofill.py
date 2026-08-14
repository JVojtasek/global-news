"""Záložní autor vydání — dopíše sloty, které nikdo jiný nedodal.

Proč existuje
-------------
Sloty 1–6 mají psát naplánované úlohy ChatGPT Work. Když ta strana vypadne
(vyčerpaný limit, výpadek, změna účtu), vydání zůstane prázdné a nikdo se to
včas nedozví. Tenhle modul je bezpečnostní síť: spouští se během dne
opakovaně, podívá se, co chybí, a chybějící slot napíše přes Anthropic API.

Co NEDĚLÁ
---------
Nepublikuje. Výsledek ukládá jako ``status: draft`` do ``content/inbox/``.
O tom, jestli článek vyjde, rozhoduje výhradně existující redakční síto
(``engine.inbox``) a vydání (``engine.release``) — stejně jako u textů
z ChatGPT Work. Tenhle modul nemá žádnou zkratku okolo kontroly.

Pojistky
--------
* **Ověřené zdroje.** Každý odkaz z hlavičky se skutečně stáhne. Odkaz, který
  nevrátí 2xx/3xx, se z hlavičky vyhodí. Když po očistě zbyde míň zdrojů, než
  vyžaduje typ článku, text se neuloží. Tím padá nejčastější způsob, jak si
  model vymyslí důkaz.
* **Vlastní kontrola před uložením.** Text projde stejným sítem, kterým ho
  potom prožene ``engine.inbox``. Když neprojde, model dostane seznam závad
  a jeden pokus na opravu. Když neprojde ani pak, slot zůstane prázdný —
  prázdná rubrika je menší škoda než odbytý text (CLAUDE.md, pravidlo 1).
* **Denní strop útraty.** Hlídá ``engine.ai`` přes ``ai.max_usd_per_day``
  v ``data/site.yml``. Při vyčerpání modul skončí bez chyby.
* **Slot 7 nikdy.** Rezerva se nedoplňuje na sílu.

Spuštění
--------
    python -m engine.autofill            # dopíše nejvýš MAX_PER_RUN slotů
    AUTOFILL_MAX=1 python -m engine.autofill
    AI_MOCK=1 python -m engine.autofill  # bez klíče a bez peněz
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys

import requests

from . import ai, article, config, edition, inbox

P = config.ROOT / "engine" / "prompts"
INBOX = config.CONTENT / "inbox"

MAX_PER_RUN = int(os.environ.get("AUTOFILL_MAX") or 3)
HTTP_TIMEOUT = 20
UA = "Mozilla/5.0 (compatible; MyPaper-SourceCheck/1.0; +https://mypaper.news)"


def _prompt(name: str) -> str:
    return (P / name).read_text(encoding="utf-8")


# --------------------------------------------------------------- chybějící sloty
def _occupied(day: dt.date) -> set[int]:
    """Čísla slotů, která už dnes někdo obsadil.

    Počítá se stejně jako v ``engine.edition_guard``: jen soubory v jazyce
    originálu, s dnešním datem a ``automation_generated: true``.
    """
    date = day.isoformat()
    master = str(config.site()["languages"]["master"])
    taken: set[int] = set()
    paths = list(INBOX.glob("*.md"))
    for lang_dir in config.CONTENT.iterdir():
        if lang_dir.is_dir() and lang_dir.name != "inbox":
            paths.extend(lang_dir.glob(f"{date}-*.md"))
    for path in paths:
        try:
            meta, _ = article.parse(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if meta.get("date") != date or str(meta.get("lang") or "en") != master:
            continue
        if not meta.get("automation_generated"):
            continue
        try:
            taken.add(int(meta.get("edition_slot") or 0))
        except (TypeError, ValueError):
            continue
    return taken


def missing_slots(day: dt.date) -> list[dict]:
    """Specifikace veřejných slotů 1–6, které dnes chybí. Rezervu vynechává."""
    plan = edition.build(day)
    taken = _occupied(day)
    return [s for s in (plan.get("slots") or []) if int(s["slot"]) not in taken]


# --------------------------------------------------------------- ověření zdrojů
def _verify_sources(meta: dict) -> tuple[list[dict], list[str]]:
    """Nechá v hlavičce jen odkazy, které se opravdu otevřou."""
    kept, dropped = [], []
    seen = set()
    for src in meta.get("sources") or []:
        if not isinstance(src, dict):
            continue
        url = str(src.get("url") or "").strip()
        if not url.startswith("https://") or url in seen:
            dropped.append(url or "(prázdný odkaz)")
            continue
        seen.add(url)
        try:
            r = requests.get(url, timeout=HTTP_TIMEOUT, headers={"User-Agent": UA},
                             allow_redirects=True, stream=True)
            ok = r.status_code < 400
            r.close()
        except Exception:  # noqa: BLE001
            ok = False
        (kept if ok else dropped).append(src if ok else url)
    return kept, dropped


# --------------------------------------------------------------- podklady
def _grounding(spec: dict, day: dt.date) -> str:
    """Co model dostane jako podklad: dnešní agenda + čerstvě sebraná témata."""
    parts = []
    agenda = config.DATA / "daily-agenda" / f"{day.isoformat()}.md"
    if agenda.exists():
        parts.append("DNEŠNÍ AGENDA REDAKCE:\n" + agenda.read_text(encoding="utf-8")[:12000])

    topics = config.DATA / "topics.json"
    if topics.exists():
        parts.append("SEBRANÁ TÉMATA (data/topics.json):\n" + topics.read_text(encoding="utf-8")[:6000])

    recent = []
    master = str(config.site()["languages"]["master"])
    for path in sorted((config.CONTENT / master).glob("*.md"))[-60:]:
        try:
            meta, _ = article.parse(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if meta.get("title"):
            recent.append(f"- {meta.get('date')} [{meta.get('section')}] {meta['title']}")
    if recent:
        parts.append("CO UŽ VYŠLO (neopakuj téma ani mechanismus):\n" + "\n".join(recent[-60:]))
    return "\n\n".join(parts)


def _task(spec: dict, day: dt.date, notes: str = "") -> str:
    rules = config.site()["automation"]
    min_src = int((rules.get("minimum_sources") or {}).get(spec["type"], 4))
    task = f"""Napiš JEDEN článek pro dnešní vydání novin My Paper.

ZÁVAZNÉ ZADÁNÍ SLOTU (nesmíš změnit ani jedno pole):
  edition_slot: {spec['slot']}
  role:         {spec.get('role')}
  section:      {spec['section']}
  type:         {spec['type']}
  rozsah:       {spec['min_words']}–{spec['max_words']} slov (počítá se tělo bez hlavičky)
  date:         {day.isoformat()}
  lang:         en
  status:       draft

DALŠÍ POVINNÁ POLE HLAVIČKY:
  automation_generated: true
  automation_role: edition
  generator: claude-api

ZDROJE: nejméně {min_src} různé skutečné odkazy https v poli `sources`, každý
s `name`, `url` a pokud to jde `published`. Odkazy se po tobě STAHUJÍ a ověřují —
vymyšlený nebo neexistující odkaz článek zabije. Dávej přednost primárním
dokumentům, oficiálním statistikám, regulátorům, soudním a zákonodárným
materiálům a výročním zprávám před přehledovými stránkami. Uváděj jen odkazy,
o kterých si jsi jistý, že existují na uvedené adrese.

KVÍZ je povinný: `quiz` se třemi možnostmi, `answer` jako index 0–2 a
vysvětlením. Odpověď musí být přímo v textu článku.

Text piš anglicky. Vrať POUZE hotový Markdown soubor s YAML hlavičkou mezi
`---`, nic dalšího okolo.

PODKLADY:
{_grounding(spec, day)[:30000]}
"""
    if notes:
        task += ("\n\nPŘEDCHOZÍ POKUS NEPROŠEL REDAKČNÍ KONTROLOU. Oprav přesně tohle "
                 "a vrať celý článek znovu:\n" + notes)
    return task


# --------------------------------------------------------------- zápis slotu
def _force_header(meta: dict, spec: dict, day: dt.date) -> dict:
    """Hlavičku neurčuje model. Určuje ji plán vydání."""
    meta["date"] = day.isoformat()
    meta["lang"] = str(config.site()["languages"]["master"])
    meta["section"] = spec["section"]
    meta["type"] = spec["type"]
    meta["status"] = "draft"
    meta["automation_generated"] = True
    meta["automation_role"] = "edition"
    meta["edition_slot"] = int(spec["slot"])
    meta["generator"] = "claude-api"
    meta.setdefault("depth", "open")
    meta.setdefault("confidence", 0)
    meta.setdefault("load", 0)
    meta.setdefault("topics", [])
    meta.setdefault("series", "")
    meta.setdefault("event_id", "")
    meta.setdefault("format", "")
    meta.setdefault("image_query", "")
    if not meta.get("slug"):
        meta["slug"] = article.slugify(str(meta.get("title") or f"slot-{spec['slot']}"))
    return meta


def _inbox_path(spec: dict, day: dt.date, meta: dict) -> "config.pathlib.Path":
    slug = re.sub(r"[^a-z0-9-]+", "-", str(meta.get("slug") or "").lower()).strip("-")[:60]
    return INBOX / f"{day.isoformat()}-slot-{spec['slot']}-{slug or 'text'}.md"


def _attempt(spec: dict, day: dt.date, notes: str = "") -> tuple[dict | None, str, list[str]]:
    raw = ai.ask(
        _prompt("analysis_article.md") + "\n\n" + _prompt("VOICE.md") + "\n\n" + _prompt("FORMAT.md"),
        _task(spec, day, notes),
        max_tokens=12000,
        temperature=0.6,
    )
    meta, body = article.parse(raw)
    if not meta:
        return None, "", ["model nevrátil platnou YAML hlavičku"]

    meta = _force_header(meta, spec, day)

    kept, dropped = _verify_sources(meta)
    meta["sources"] = kept
    if dropped:
        config.log(f"    zahozené neověřitelné odkazy: {len(dropped)}")
        for u in dropped[:4]:
            config.log(f"      × {str(u)[:110]}")

    problems = inbox._rule_check(meta, body)
    return meta, body, problems


def write_slot(spec: dict, day: dt.date) -> "config.pathlib.Path | None":
    config.log(f"  → slot {spec['slot']} ({spec['section']}/{spec['type']}, "
               f"{spec['min_words']}–{spec['max_words']} slov)")
    meta, body, problems = _attempt(spec, day)

    if problems and meta:
        config.log("    kontrola nalezla: " + "; ".join(problems[:3]))
        config.log("    zkouším jednu opravu")
        meta2, body2, problems2 = _attempt(spec, day, "- " + "\n- ".join(problems[:8]))
        if meta2 and not problems2:
            meta, body, problems = meta2, body2, problems2
        elif meta2 and len(problems2) < len(problems):
            meta, body, problems = meta2, body2, problems2

    if not meta:
        config.log("    ✗ slot zůstal prázdný (model nedodal použitelný text)")
        return None
    if problems:
        config.log("    ✗ slot zůstal prázdný — " + "; ".join(problems[:3]))
        return None

    path = _inbox_path(spec, day, meta)
    if path.exists():
        config.log("    ✗ soubor už existuje, nepřepisuji")
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(article.dump(meta, body), encoding="utf-8")
    config.log(f"    ✓ {path.name}  ({len(body.split())} slov, {len(meta.get('sources') or [])} ověřených zdrojů)")
    return path


# --------------------------------------------------------------- běh
def run(day: dt.date | None = None) -> int:
    day = day or dt.date.today()
    missing = missing_slots(day)
    if not missing:
        config.log("Vydání je kompletní, záložní autor nic nepíše.")
        return 0

    config.log(f"Chybí sloty: {', '.join(str(s['slot']) for s in missing)} "
               f"(v tomhle běhu napíšu nejvýš {MAX_PER_RUN})")

    written = 0
    for spec in missing[:MAX_PER_RUN]:
        try:
            if write_slot(spec, day):
                written += 1
        except ai.BudgetExceeded as ex:
            config.log(f"STOP: {ex}")
            break
        except ai.AIUnavailable as ex:
            config.log(f"STOP: AI nedostupná — {str(ex)[:200]}")
            break
        except Exception as ex:  # noqa: BLE001
            config.log(f"  ! slot {spec['slot']} přeskočen: {str(ex)[:200]}")

    state = config.load_state()
    state.setdefault("last_run", {})["autofill"] = config.today()
    config.save_state(state)
    config.log(f"Hotovo. Doplněno slotů: {written}")
    return written


if __name__ == "__main__":
    sys.exit(0 if run() >= 0 else 1)
