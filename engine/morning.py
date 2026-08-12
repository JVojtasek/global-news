"""Morning Briefing: a finite, source-labelled view of the last 24 hours.

The page is deliberately assembled from data the newsroom already produces:
published My Paper articles, the free event collector and the research desk's
daily agenda.  There is no API call at build time and no reader profile leaves
the browser.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

from . import config, countries


PRAGUE = ZoneInfo("Europe/Prague")
_JSON_HEADING = r"^## {heading}\s*$.*?^```json\s*$\s*(\[.*?\])\s*^```\s*$"
_WATCH_LABEL = {
    "en": re.compile(r"<strong>What to watch\.</strong>\s*(.*?)</p>", re.I | re.S),
    "cs": re.compile(r"<strong>Na co se dívat dál\.</strong>\s*(.*?)</p>", re.I | re.S),
}

_ACTION_LEVELS = {"know": 0, "watch": 1, "prepare": 2, "act": 3}
_ACTION_LABELS = {
    "en": {"know": "Know", "watch": "Watch", "prepare": "Prepare", "act": "Act"},
    "cs": {"know": "Vědět", "watch": "Sledovat", "prepare": "Připravit", "act": "Jednat"},
}

# A calm, low-cost task is useful even on days without a warning. These are
# deliberately not event predictions and never tell a reader to hoard. The
# same date always yields the same task, which keeps builds reproducible.
_READINESS = [
    {
        "source": "Ready.gov", "url": "https://www.ready.gov/plan",
        "en": ("Choose one family meeting point",
               "Agree where to meet if phones or local transport stop working. Add one contact outside your immediate area."),
        "cs": ("Domluvte si jedno rodinné místo setkání",
               "Dohodněte se, kde se sejdete, když nefungují telefony nebo místní doprava. Přidejte jeden kontakt mimo vaše bezprostřední okolí."),
    },
    {
        "source": "Ready.gov", "url": "https://www.ready.gov/low-and-no-cost",
        "en": ("Save the documents you would need first",
               "Put secure digital copies of identification, insurance and essential contacts somewhere you can reach away from home."),
        "cs": ("Uložte si doklady, které byste potřebovali jako první",
               "Dejte bezpečné digitální kopie dokladů, pojištění a důležitých kontaktů na místo dostupné i mimo domov."),
    },
    {
        "source": "American Red Cross",
        "url": "https://www.redcross.org/get-help/how-to-prepare-for-emergencies/anatomy-of-a-first-aid-kit.html",
        "en": ("Check the family medical list",
               "Record current medicines, allergies, doctors and emergency numbers. Do not change treatment; keep the list current and accessible."),
        "cs": ("Zkontrolujte rodinný zdravotní seznam",
               "Zapište současné léky, alergie, lékaře a nouzová čísla. Léčbu neměňte; seznam jen udržujte aktuální a dostupný."),
    },
    {
        "source": "Ready.gov", "url": "https://www.ready.gov/kit",
        "en": ("Test one thing that depends on power",
               "Charge a power bank and test a torch or radio. Replace only what does not work; preparedness does not require a shopping spree."),
        "cs": ("Vyzkoušejte jednu věc závislou na elektřině",
               "Dobijte powerbanku a vyzkoušejte svítilnu nebo rádio. Nahraďte jen to, co nefunguje; připravenost neznamená nákupní horečku."),
    },
    {
        "source": "European Commission", "url": "https://commission.europa.eu/topics/preparedness_en",
        "en": ("Map the first 72 hours before buying anything",
               "List what your household already has for water, food, medicines, light and communication; fill genuine gaps gradually and follow local guidance."),
        "cs": ("Zmapujte prvních 72 hodin dřív, než něco koupíte",
               "Sepište, co už domácnost má pro vodu, jídlo, léky, světlo a komunikaci; skutečné mezery doplňujte postupně podle místních pokynů."),
    },
    {
        "source": "Ready.gov", "url": "https://www.ready.gov/pets",
        "en": ("Add pets to the household plan",
               "Keep registration details, one current photo and a carrier or lead ready, and identify who can help if you are away."),
        "cs": ("Přidejte do rodinného plánu domácí zvířata",
               "Mějte po ruce údaje o registraci, aktuální fotografii a přepravku či vodítko a určete, kdo pomůže, když nebudete doma."),
    },
    {
        "source": "Ready.gov", "url": "https://www.ready.gov/low-and-no-cost",
        "en": ("Save official alert channels",
               "Bookmark your national weather and civil-protection services. A verified local warning outranks a viral post or a general news headline."),
        "cs": ("Uložte si oficiální varovné kanály",
               "Přidejte si do záložek národní meteorologickou a civilní ochranu. Ověřené místní varování má přednost před virálním příspěvkem i obecným titulkem."),
    },
]


def _time(value) -> dt.datetime | None:
    """Parse ISO time and always return an aware UTC datetime."""
    if isinstance(value, dt.datetime):
        parsed = value
    else:
        raw = str(value or "").strip().replace("Z", "+00:00")
        if len(raw) < 16:
            return None
        try:
            parsed = dt.datetime.fromisoformat(raw)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _now(value=None) -> dt.datetime:
    return _time(value) or dt.datetime.now(dt.timezone.utc)


def _relative(value, lang: str, now=None) -> str:
    stamp = _time(value)
    if not stamp:
        return ""
    seconds = max(0, int((_now(now) - stamp).total_seconds()))
    minutes = seconds // 60
    if minutes < 1:
        return "právě teď" if lang == "cs" else "just now"
    if minutes < 60:
        return f"před {minutes} min" if lang == "cs" else f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"před {hours} h" if lang == "cs" else f"{hours}h ago"
    return stamp.astimezone(PRAGUE).strftime("%-d %b, %H:%M")


def _country_data(value) -> dict:
    value = value if isinstance(value, dict) else {}
    return {
        "direct": [str(x).lower() for x in value.get("direct", []) if re.fullmatch(r"[a-zA-Z]{2}", str(x))],
        "scope": value.get("scope") if value.get("scope") in {"eu", "global"} else "none",
    }


def _agenda_json(path: Path, heading: str) -> list:
    """Return one fenced JSON array beneath an exact agenda heading."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return []
    rx = re.compile(_JSON_HEADING.format(heading=re.escape(heading)), re.I | re.M | re.S)
    match = rx.search(raw)
    if not match:
        return []
    try:
        rows = json.loads(match.group(1))
    except (TypeError, ValueError):
        return []
    return rows if isinstance(rows, list) else []


def _agenda_path(day: str, agenda_path: Path | None = None) -> Path:
    return agenda_path or (config.DATA / "daily-agenda" / f"{day}.md")


def _localise(row: dict, key: str, lang: str) -> str:
    return str(row.get(f"{key}_{lang}") or row.get(f"{key}_en") or "").strip()


def readiness_tip(day: str, lang: str) -> dict:
    """Pick one evergreen, official-source preparedness task for the day."""
    try:
        date = dt.date.fromisoformat(day)
    except ValueError:
        date = dt.date.today()
    tip = _READINESS[(date.toordinal() - 1) % len(_READINESS)]
    title, action = tip.get(lang, tip["en"])
    return {
        "level": "prepare", "level_label": _ACTION_LABELS.get(lang, _ACTION_LABELS["en"])["prepare"],
        "title": title, "action": action, "trigger": "", "source": tip["source"],
        "url": tip["url"], "countries": _country_data({"scope": "global"}),
        "baseline": True,
    }


def local_from_agenda(day: str, lang: str, now=None, agenda_path: Path | None = None,
                      limit: int = 8) -> list:
    """Read current, source-labelled country notes from the daily agenda."""
    current = _now(now)
    rows = _agenda_json(_agenda_path(day, agenda_path), "Briefing country notes")
    found = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get("source_url") or "").strip()
        title, why = _localise(row, "title", lang), _localise(row, "why", lang)
        published = _time(row.get("published_at"))
        valid_until = _time(row.get("valid_until"))
        if not url.startswith("https://") or len(title) < 12 or len(why) < 20:
            continue
        if published and published > current + dt.timedelta(minutes=15):
            continue
        if valid_until and valid_until < current:
            continue
        country_data = _country_data({"direct": row.get("countries") or [],
                                      "scope": row.get("scope") or "none"})
        if not country_data["direct"] and country_data["scope"] == "none":
            continue
        stamp = published or current
        found.append((stamp, {
            "title": title[:180], "why": why[:420], "url": url,
            "source": str(row.get("publisher") or ""),
            "section": _localise(row, "section", lang),
            "section_id": str(row.get("section_id") or "world"),
            "created_iso": stamp.isoformat(timespec="minutes"),
            "brief_time": _relative(stamp, lang, current) if published else "",
            "countries": country_data,
        }))
    found.sort(key=lambda item: (item[0], item[1]["title"]), reverse=True)
    return [item for _, item in found[:limit]]


def actions_from_agenda(day: str, lang: str, now=None, agenda_path: Path | None = None,
                        limit: int = 6) -> list:
    """Read practical decisions, enforcing a high bar for consequential advice.

    KNOW can explain; WATCH can name a measurable trigger. PREPARE and ACT must
    cite an official source and have an expiry. ACT must also target a concrete
    country. This prevents a generic headline from becoming panic advice.
    """
    current = _now(now)
    rows = _agenda_json(_agenda_path(day, agenda_path), "Briefing practical decisions")
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        level = str(row.get("level") or "").lower()
        title = _localise(row, "title", lang)
        why = _localise(row, "why", lang)
        action = _localise(row, "action", lang)
        trigger = _localise(row, "trigger", lang)
        url = str(row.get("source_url") or "").strip()
        expires = _time(row.get("valid_until"))
        country_data = _country_data({"direct": row.get("countries") or [],
                                      "scope": row.get("scope") or "none"})
        if level not in _ACTION_LEVELS or not url.startswith("https://"):
            continue
        if len(title) < 12 or len(why) < 20 or len(action) < 12:
            continue
        if level in {"watch", "prepare", "act"} and (not expires or expires < current):
            continue
        if level in {"prepare", "act"} and row.get("official") is not True:
            continue
        if level == "act" and not country_data["direct"]:
            continue
        out.append({
            "level": level,
            "level_label": _ACTION_LABELS.get(lang, _ACTION_LABELS["en"])[level],
            "title": title[:180], "why": why[:420], "action": action[:420],
            "trigger": trigger[:280], "url": url,
            "source": str(row.get("publisher") or ""), "countries": country_data,
            "valid_until": expires.isoformat(timespec="minutes") if expires else "",
            "baseline": False,
        })
    out.sort(key=lambda item: (-_ACTION_LEVELS[item["level"]], item["title"]))
    return out[:limit]


def impacts_from_articles(arts: list, lang: str, limit: int = 5) -> list:
    """Turn already reviewed article impact blocks into a finite decision desk."""
    out = []
    for article in arts:
        block = article.get("impact") or {}
        if not block.get("line"):
            continue
        out.append({
            "level": "watch", "level_label": _ACTION_LABELS.get(lang, _ACTION_LABELS["en"])["watch"],
            "title": article.get("title", ""), "why": block.get("line", ""),
            "action": block.get("todo", ""), "trigger": "", "url": article.get("url", ""),
            "source": "My Paper", "countries": _country_data(article.get("countries")),
            "areas": block.get("areas", []), "baseline": False,
        })
        if len(out) >= limit:
            break
    return out


def durable_from_articles(arts: list, limit: int = 3) -> list:
    """Choose recent explanatory work readers may still need in six months."""
    picked, sections = [], set()
    for article in arts:
        if article.get("type") not in {"analysis", "feature", "evergreen", "daily"}:
            continue
        section = str(article.get("section") or "")
        if section in sections:
            continue
        picked.append(article)
        sections.add(section)
        if len(picked) >= limit:
            break
    return picked


def articles_last_24h(arts: list, now=None, limit: int = 12) -> list:
    """Return published articles in exact reverse-chronological order."""
    current = _now(now)
    cutoff = current - dt.timedelta(hours=24)
    found = []
    for article in arts:
        stamp = _time(article.get("published_iso"))
        if stamp and cutoff <= stamp <= current + dt.timedelta(minutes=10):
            found.append((stamp, article))
    found.sort(key=lambda row: (row[0], row[1].get("slug", "")), reverse=True)
    out = []
    for stamp, article in found[:limit]:
        item = dict(article)
        item["brief_time"] = _relative(stamp, article.get("lang", "en"), current)
        item["countries"] = _country_data(article.get("countries"))
        out.append(item)
    return out


def live_last_24h(site: dict, lang: str, now=None, limit: int = 10,
                  events_path: Path | None = None) -> list:
    """Return fresh event clusters with a direct source link.

    Events without a parseable creation time are excluded: a headline cannot
    honestly be labelled "last 24 hours" if we do not know when it arrived.
    """
    path = events_path or (config.DATA / "events.json")
    try:
        events = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return []
    if not isinstance(events, list):
        return []

    current = _now(now)
    cutoff = current - dt.timedelta(hours=24)
    labels = {s["id"]: (s.get(lang) or s.get("en") or s["id"]) for s in site.get("sections", [])}
    found, seen = [], set()
    for event in events:
        if not isinstance(event, dict):
            continue
        # `event_time` is publisher time only when the collector says so.
        # `created`/`seen_at` are collection times and must never make an old
        # story appear fresh.
        stamp = _time(event.get("event_time")) if event.get("time_kind") == "published" else None
        headline = str(event.get("headline") or "").strip()
        if not stamp or not (cutoff <= stamp <= current + dt.timedelta(minutes=10)) or len(headline) < 20:
            continue
        key = re.sub(r"\W+", " ", headline.lower()).strip()[:80]
        if key in seen:
            continue
        source = next((x for x in (event.get("items") or [])
                       if isinstance(x, dict) and str(x.get("url") or "").startswith("https://")), None)
        if not source:
            continue
        seen.add(key)
        summary = str(source.get("summary") or "").strip()
        section = str(event.get("section") or "")
        reach = countries.detect(
            {"lang": lang, "title": headline, "dek": summary, "section": section},
            f"{headline}. {summary}",
        )
        found.append((stamp, {
            "headline": headline[:150],
            "summary": summary[:260],
            "url": source["url"],
            "source": str(source.get("source") or ""),
            "section": labels.get(section, section),
            "section_id": section,
            "sources_count": max(1, int(event.get("sources_count") or 1)),
            "created_iso": stamp.isoformat(timespec="minutes"),
            "brief_time": _relative(stamp, lang, current),
            "countries": _country_data(reach),
        }))
    found.sort(key=lambda row: (row[0], row[1]["headline"]), reverse=True)
    return [item for _, item in found[:limit]]


def _plain(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    return " ".join(html.unescape(text).split())


def watch_from_articles(arts: list, lang: str, limit: int = 5) -> list:
    """Use explicit editorial 'What to watch' statements as a safe fallback."""
    candidates = []
    rx = _WATCH_LABEL.get(lang, _WATCH_LABEL["en"])
    for article in arts:
        brief = next((layer.get("html", "") for layer in article.get("layers", [])
                      if layer.get("id") == "BRIEFLY"), "")
        match = rx.search(brief)
        if not match:
            continue
        text = _plain(match.group(1))
        if len(text) < 20:
            continue
        candidates.append({
            "title": article.get("title", ""),
            "why": text,
            "url": article.get("url", ""),
            "source": "My Paper",
            "section": article.get("section_label", ""),
            "section_id": article.get("section", ""),
            "starts_label": "",
            "countries": _country_data(article.get("countries")),
            "tags_csv": article.get("tags_csv", ""),
            "topics_csv": article.get("topics_csv", ""),
        })

    # Preserve recency but avoid presenting five watch points from one desk.
    diverse, rest, used = [], [], set()
    for item in candidates:
        if item["section_id"] not in used:
            diverse.append(item)
            used.add(item["section_id"])
        else:
            rest.append(item)
    return (diverse + rest)[:limit]


def watch_from_agenda(day: str, lang: str, agenda_path: Path | None = None,
                      limit: int = 6) -> list:
    """Read the research desk's source-verified, time-bound watch calendar."""
    rows = _agenda_json(_agenda_path(day, agenda_path), "Briefing watch calendar")

    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        stamp = _time(row.get("starts_at"))
        url = str(row.get("source_url") or "").strip()
        title = str(row.get(f"title_{lang}") or row.get("title_en") or "").strip()
        why = str(row.get(f"why_{lang}") or row.get("why_en") or "").strip()
        if not stamp or stamp.astimezone(PRAGUE).date().isoformat() != day:
            continue
        if not url.startswith("https://") or len(title) < 12 or len(why) < 20:
            continue
        local = stamp.astimezone(PRAGUE)
        out.append((stamp, {
            "title": title[:180], "why": why[:360], "url": url,
            "source": str(row.get("publisher") or ""),
            "section": str(row.get(f"section_{lang}") or row.get("section_en") or ""),
            "section_id": str(row.get("section_id") or ""),
            "starts_label": ("Celý den" if lang == "cs" else "All day")
                            if row.get("all_day") else local.strftime("%H:%M %Z"),
            "countries": _country_data({
                "direct": row.get("countries") or [],
                "scope": row.get("scope") or "none",
            }),
            "tags_csv": "", "topics_csv": "",
        }))
    out.sort(key=lambda row: (row[0], row[1]["title"]))
    return [item for _, item in out[:limit]]


def edition(arts: list, site: dict, lang: str, now=None, day: str | None = None,
            events_path: Path | None = None, agenda_path: Path | None = None) -> dict:
    """Build all server-side layers used by the Briefing template."""
    current = _now(now)
    local_day = day or current.astimezone(PRAGUE).date().isoformat()
    recent = articles_last_24h(arts, current)
    agenda = watch_from_agenda(local_day, lang, agenda_path)
    watch = agenda or watch_from_articles(recent or arts[:12], lang)
    practical = actions_from_agenda(local_day, lang, current, agenda_path)
    practical += impacts_from_articles(recent or arts[:12], lang, limit=max(0, 5 - len(practical)))
    return {
        "live": live_last_24h(site, lang, current, events_path=events_path),
        "local": local_from_agenda(local_day, lang, current, agenda_path),
        "recent": recent,
        "practical": practical[:5],
        "watch": watch,
        "watch_is_calendar": bool(agenda),
        "readiness": readiness_tip(local_day, lang),
        "durable": durable_from_articles(arts),
        "date": local_day,
    }
