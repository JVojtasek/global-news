import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from engine import build, collect, livefeed


class LiveNewsTests(unittest.TestCase):
    def test_rss_publication_time_is_normalised_to_utc(self):
        entry = SimpleNamespace(published="Tue, 12 Aug 2026 08:15:00 +0200")
        self.assertEqual("2026-08-12T06:15:00+00:00", collect._entry_time(entry))

    def test_score_keeps_publication_time_separate_from_first_seen(self):
        item = {
            "title": "A sufficiently descriptive technology headline today",
            "url": "https://example.com/story", "summary": "technology data",
            "source": "Example", "weight": 8, "src_section": "tech",
            "published_at": "2026-08-12T06:15:00+00:00",
            "seen_at": "2026-08-12T06:20:00+00:00",
        }
        event = collect._score({"items": [item], "tokens": collect._tokens(item["title"])})
        self.assertEqual(item["published_at"], event["event_time"])
        self.assertEqual(item["published_at"], event["items"][0]["published_at"])
        self.assertNotEqual(event["created"], event["event_time"])

    def test_live_snapshot_rejects_items_without_real_publication_time(self):
        current = dt.datetime(2026, 8, 12, 8, 0, tzinfo=dt.timezone.utc)
        items = [
            {"title": "Fresh technology news with a precise timestamp", "url": "https://example.com/fresh",
             "summary": "software", "source": "Tech", "weight": 8, "src_section": "tech",
             "published_at": "2026-08-12T07:30:00+00:00", "seen_at": "2026-08-12T07:35:00+00:00"},
            {"title": "Undated headline that must not pretend to be new", "url": "https://example.com/undated",
             "summary": "software", "source": "Tech", "weight": 8, "src_section": "tech",
             "published_at": "", "seen_at": "2026-08-12T07:35:00+00:00"},
        ]
        with mock.patch("engine.livefeed.collect._fetch_all", return_value=items), \
             mock.patch("engine.livefeed.config.sources", return_value=[{"name": "Tech"}]):
            data = livefeed.snapshot(current)
        self.assertEqual(1, len(data["items"]))
        self.assertEqual("https://example.com/fresh", data["items"][0]["url"])
        self.assertEqual(300, data["refresh_seconds"])

    def test_empty_refresh_does_not_overwrite_last_usable_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            static = Path(tmp)
            target = static / "live-news.json"
            target.write_text('{"generated_at":"old","items":[{"headline":"kept"}]}', encoding="utf-8")
            with mock.patch.object(livefeed.config, "STATIC", static), \
                 mock.patch("engine.livefeed.snapshot", return_value={"generated_at": "new", "items": []}):
                with self.assertRaises(RuntimeError):
                    livefeed.run()
            self.assertIn('"kept"', target.read_text(encoding="utf-8"))

    def test_browser_has_a_newest_snapshot_fallback(self):
        source = (Path(__file__).parents[1] / "static" / "live.js").read_text(encoding="utf-8")
        self.assertIn('fetchFeed("/live-news.json")', source)
        self.assertIn("stamp(b.generated_at) - stamp(a.generated_at)", source)

    def test_ticker_uses_event_time_and_filters_technology(self):
        events = [
            {"headline": "Older technology headline with enough descriptive words", "section": "tech",
             "score": 90, "created": "2026-08-12T08:00:00+00:00", "event_time": "2026-08-12T05:00:00+00:00",
             "sources_count": 1, "items": [{"url": "https://example.com/old", "source": "Tech",
                                              "published_at": "2026-08-12T05:00:00+00:00"}]},
            {"headline": "Newer technology headline with enough descriptive words", "section": "tech",
             "score": 20, "created": "2026-08-12T08:00:00+00:00", "event_time": "2026-08-12T07:00:00+00:00",
             "sources_count": 1, "items": [{"url": "https://example.com/new", "source": "Tech",
                                              "published_at": "2026-08-12T07:00:00+00:00"}]},
            {"headline": "New world headline with enough descriptive words", "section": "world",
             "score": 99, "created": "2026-08-12T08:00:00+00:00", "event_time": "2026-08-12T07:30:00+00:00",
             "sources_count": 1, "items": [{"url": "https://example.com/world", "source": "World",
                                              "published_at": "2026-08-12T07:30:00+00:00"}]},
        ]
        site = {"sections": [{"id": "world", "en": "World", "cs": "Svět"},
                             {"id": "tech", "en": "Technology", "cs": "Technologie"}]}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "events.json").write_text(json.dumps(events), encoding="utf-8")
            with mock.patch("engine.build.config.DATA", Path(tmp)):
                ticker = build._ticker(site, "en", preferred_section="tech")
        self.assertEqual(["https://example.com/new", "https://example.com/old"],
                         [item["url"] for item in ticker["items"]])
        self.assertEqual("2026-08-12T07:00:00+00:00", ticker["items"][0]["published_iso"])

    def test_ticker_does_not_label_collection_time_as_publication_time(self):
        legacy = [{"headline": "Legacy technology headline with no publisher timestamp",
                   "section": "tech", "score": 90, "created": "2026-08-12T08:00:00+00:00",
                   "sources_count": 1,
                   "items": [{"url": "https://example.com/legacy", "source": "Tech"}]}]
        site = {"sections": [{"id": "tech", "en": "Technology", "cs": "Technologie"}]}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "events.json").write_text(json.dumps(legacy), encoding="utf-8")
            with mock.patch("engine.build.config.DATA", Path(tmp)):
                ticker = build._ticker(site, "en", preferred_section="tech")
        self.assertEqual([], ticker["items"])


if __name__ == "__main__":
    unittest.main()
