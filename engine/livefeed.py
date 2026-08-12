"""Create the zero-API live-news snapshot used by the browser.

This is intentionally separate from the heavier three-hour newsroom run. It
only reads public RSS/Atom feeds, keeps items whose real publication time is
known, clusters duplicates and writes one compact JSON file. No model, API key,
database or reader data is involved.
"""
from __future__ import annotations

import datetime as dt
import json

from . import collect, config


WINDOW_HOURS = 48
MAX_ITEMS = 400


def _time(value) -> dt.datetime | None:
    try:
        stamp = dt.datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=dt.timezone.utc)
    return stamp.astimezone(dt.timezone.utc)


def snapshot(now=None) -> dict:
    current = _time(now) or dt.datetime.now(dt.timezone.utc)
    cutoff = current - dt.timedelta(hours=WINDOW_HOURS)
    future = current + dt.timedelta(minutes=15)

    # A headline without a publisher-supplied time is still useful for the
    # research desk, but it is not allowed in a feed that promises exact age.
    items = []
    for item in collect._fetch_all():
        published = _time(item.get("published_at"))
        if published and cutoff <= published <= future:
            items.append(item)

    events = [collect._score(cluster) for cluster in collect._cluster(items)]
    events.sort(key=lambda event: (event.get("event_time", ""), event.get("score", 0)), reverse=True)

    out = []
    seen = set()
    for event in events:
        lead = (event.get("items") or [{}])[0]
        url = str(lead.get("url") or "")
        published = str(lead.get("published_at") or event.get("event_time") or "")
        key = (url, event.get("headline", "").lower()[:100])
        if not url.startswith(("https://", "http://")) or not _time(published) or key in seen:
            continue
        seen.add(key)
        out.append({
            "id": event.get("id", ""),
            "headline": event.get("headline", "")[:180],
            "url": url,
            "source": lead.get("source", ""),
            "section": event.get("section", "world"),
            "sources_count": event.get("sources_count", 1),
            "published_at": published,
            "score": event.get("score", 0),
        })
        if len(out) >= MAX_ITEMS:
            break

    completed = current if now is not None else dt.datetime.now(dt.timezone.utc)
    return {
        "generated_at": completed.isoformat(timespec="seconds"),
        "refresh_seconds": 300,
        "window_hours": WINDOW_HOURS,
        "source_count": len(config.sources()),
        "items": out,
    }


def run() -> dict:
    data = snapshot()
    path = config.STATIC / "live-news.json"
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    config.log(f"Živý feed: {len(data['items'])} zpráv z {data['source_count']} zdrojů → {path}")
    return data


if __name__ == "__main__":
    run()
