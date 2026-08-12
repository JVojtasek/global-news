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
_WATCH_HEADING = re.compile(
    r"^## Briefing watch calendar\s*$.*?^```json\s*$\s*(\[.*?\])\s*^```\s*$",
    re.I | re.M | re.S,
)
_WATCH_LABEL = {
    "en": re.compile(r"<strong>What to watch\.</strong>\s*(.*?)</p>", re.I | re.S),
    "cs": re.compile(r"<strong>Na co se dívat dál\.</strong>\s*(.*?)</p>", re.I | re.S),
}


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
        stamp = _time(event.get("created"))
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
    path = agenda_path or (config.DATA / "daily-agenda" / f"{day}.md")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return []
    match = _WATCH_HEADING.search(raw)
    if not match:
        return []
    try:
        rows = json.loads(match.group(1))
    except (TypeError, ValueError):
        return []
    if not isinstance(rows, list):
        return []

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
    return {
        "live": live_last_24h(site, lang, current, events_path=events_path),
        "recent": recent,
        "watch": watch,
        "watch_is_calendar": bool(agenda),
        "date": local_day,
    }
