import datetime as dt
import json

from engine import morning


NOW = dt.datetime(2026, 8, 12, 8, 0, tzinfo=dt.timezone.utc)


def _article(slug, published, section="world", watch=""):
    layers = []
    if watch:
        layers = [{"id": "BRIEFLY", "html": f"<p><strong>What to watch.</strong> {watch}</p>"}]
    return {
        "slug": slug, "title": slug.replace("-", " ").title(), "dek": "A useful summary.",
        "lang": "en", "section": section, "section_label": section.title(),
        "published_iso": published, "url": f"/en/{section}/{slug}/", "layers": layers,
        "countries": {"direct": ["gb"] if slug == "new" else [], "scope": "none"},
        "tags_csv": "", "topics_csv": "",
    }


def test_articles_last_24_hours_are_exact_and_newest_first():
    arts = [
        _article("old", "2026-08-11T07:59:00+00:00"),
        _article("new", "2026-08-12T07:30:00+00:00"),
        _article("middle", "2026-08-11T20:00:00+00:00"),
    ]
    got = morning.articles_last_24h(arts, NOW)
    assert [item["slug"] for item in got] == ["new", "middle"]
    assert got[0]["brief_time"] == "30 min ago"
    assert got[0]["countries"]["direct"] == ["gb"]


def test_live_events_drop_stale_or_unverifiable_items_and_sort(tmp_path):
    events = [
        {"headline": "A stale but otherwise perfectly valid headline", "event_time": "2026-08-11T07:00:00Z",
         "time_kind": "published",
         "section": "world", "items": [{"url": "https://example.com/stale", "source": "Example"}]},
        {"headline": "The second fresh event has a useful direct source", "event_time": "2026-08-12T06:00:00Z",
         "time_kind": "published",
         "section": "world", "sources_count": 2,
         "items": [{"url": "https://example.com/second", "source": "Example"}]},
        {"headline": "The newest fresh event has a useful direct source", "event_time": "2026-08-12T07:00:00Z",
         "time_kind": "published",
         "section": "world", "items": [{"url": "https://example.com/newest", "source": "Example"}]},
        {"headline": "A fresh collection time must not revive an old headline", "created": "2026-08-12T07:55:00Z",
         "event_time": "2026-08-10T07:55:00Z", "time_kind": "seen", "section": "world",
         "items": [{"url": "https://example.com/seen", "source": "Example"}]},
        {"headline": "No publisher timestamp means this cannot be called fresh", "section": "world",
         "items": [{"url": "https://example.com/no-time", "source": "Example"}]},
    ]
    path = tmp_path / "events.json"
    path.write_text(json.dumps(events), encoding="utf-8")
    site = {"sections": [{"id": "world", "en": "World", "cs": "Svět"}]}
    got = morning.live_last_24h(site, "en", NOW, events_path=path)
    assert [item["url"] for item in got] == [
        "https://example.com/newest", "https://example.com/second"
    ]


def test_watch_fallback_extracts_explicit_editorial_signal_and_diversifies():
    arts = [
        _article("one", "2026-08-12T07:00:00Z", "world", "Watch the first measurable signal closely."),
        _article("two", "2026-08-12T06:00:00Z", "world", "Watch the second measurable signal closely."),
        _article("three", "2026-08-12T05:00:00Z", "science", "Watch the scientific result when it arrives."),
    ]
    got = morning.watch_from_articles(arts, "en")
    assert [item["title"] for item in got] == ["One", "Three", "Two"]
    assert got[0]["why"] == "Watch the first measurable signal closely."


def test_agenda_calendar_requires_same_day_direct_https_and_localises(tmp_path):
    rows = [
        {
            "starts_at": "2026-08-12T09:00:00+02:00", "all_day": False,
            "title_en": "A verified statistical release", "title_cs": "Ověřené zveřejnění statistiky",
            "why_en": "It can materially change the current economic picture.",
            "why_cs": "Může podstatně změnit současný ekonomický obraz.",
            "publisher": "Statistics Office", "source_url": "https://example.com/calendar",
            "section_id": "economy", "section_en": "Economy", "section_cs": "Ekonomika",
            "countries": ["gb"], "scope": "none",
        },
        {
            "starts_at": "2026-08-13T09:00:00+02:00", "all_day": False,
            "title_en": "Tomorrow's event must not leak in", "why_en": "It belongs to another edition entirely.",
            "publisher": "Office", "source_url": "https://example.com/tomorrow",
        },
        {
            "starts_at": "2026-08-12T10:00:00+02:00", "all_day": False,
            "title_en": "An insecure source must be rejected", "why_en": "HTTPS is required for the direct record.",
            "publisher": "Office", "source_url": "http://example.com/insecure",
        },
    ]
    path = tmp_path / "agenda.md"
    path.write_text("# Agenda\n\n## Briefing watch calendar\n\n```json\n" +
                    json.dumps(rows, ensure_ascii=False) + "\n```\n", encoding="utf-8")
    got = morning.watch_from_agenda("2026-08-12", "cs", path)
    assert len(got) == 1
    assert got[0]["title"] == "Ověřené zveřejnění statistiky"
    assert got[0]["starts_label"] == "09:00 CEST"
    assert got[0]["countries"]["direct"] == ["gb"]


def test_practical_decisions_enforce_official_source_expiry_and_country(tmp_path):
    rows = [
        {
            "level": "prepare", "title_en": "A valid low-cost preparation",
            "why_en": "An official current warning justifies a reversible preparation.",
            "action_en": "Charge the device you already own.", "trigger_en": "Only if the warning remains active.",
            "publisher": "Authority", "source_url": "https://example.com/official",
            "official": True, "valid_until": "2026-08-12T12:00:00Z",
            "countries": ["gb"], "scope": "none",
        },
        {
            "level": "act", "title_en": "An unsourced order must be rejected",
            "why_en": "The wording sounds urgent but the safety contract must still hold.",
            "action_en": "Do something irreversible now.", "trigger_en": "Immediately.",
            "publisher": "Blog", "source_url": "https://example.com/blog",
            "official": False, "valid_until": "2026-08-12T12:00:00Z",
            "countries": ["gb"], "scope": "none",
        },
        {
            "level": "act", "title_en": "A global act order must be rejected",
            "why_en": "Even an official source cannot issue a placeless instruction here.",
            "action_en": "Leave the area immediately.", "trigger_en": "When told.",
            "publisher": "Authority", "source_url": "https://example.com/global",
            "official": True, "valid_until": "2026-08-12T12:00:00Z",
            "countries": [], "scope": "global",
        },
    ]
    path = tmp_path / "agenda.md"
    path.write_text("## Briefing practical decisions\n\n```json\n" + json.dumps(rows) + "\n```\n",
                    encoding="utf-8")
    got = morning.actions_from_agenda("2026-08-12", "en", NOW, path)
    assert [item["title"] for item in got] == ["A valid low-cost preparation"]


def test_readiness_tip_is_deterministic_and_uses_official_https_source():
    one = morning.readiness_tip("2026-08-12", "cs")
    two = morning.readiness_tip("2026-08-12", "cs")
    assert one == two
    assert one["url"].startswith("https://")
    assert one["level"] == "prepare"
