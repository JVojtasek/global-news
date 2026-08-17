import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from engine import article, build, config, edition, edition_guard, inbox


class EditionPlanTests(unittest.TestCase):
    def test_six_public_sections_are_unique_and_reserve_is_seventh(self):
        plan = edition.build(dt.date(2026, 8, 12))
        self.assertEqual(6, plan["public_count"])
        self.assertEqual(6, len({slot["section"] for slot in plan["slots"]}))
        self.assertEqual([1, 2, 3, 4, 5, 6], [slot["slot"] for slot in plan["slots"]])
        self.assertEqual(7, plan["reserve"]["slot"])
        self.assertEqual("reserve", plan["reserve"]["status"])

    def test_rotation_changes_the_next_day(self):
        first = edition.build(dt.date(2026, 8, 12))
        second = edition.build(dt.date(2026, 8, 13))
        self.assertNotEqual(
            [slot["section"] for slot in first["slots"]],
            [slot["section"] for slot in second["slots"]],
        )


class ScheduledArticleGateTests(unittest.TestCase):
    def setUp(self):
        self.layers = "\n\n".join(
            f"## {name}\n\n" + ("Clear evidence and careful explanation " * 30)
            for name in ("BRIEFLY", "FACTS", "EVIDENCE", "PERSPECTIVES", "CONTEXT", "DEEPER")
        )
        self.meta = {
            "title": "A test analysis",
            "section": "ai",
            "type": "analysis",
            "lang": "en",
            "date": "2026-08-13",
            "status": "draft",
            "automation_generated": True,
            "edition_slot": 5,
            "sources": [
                {"name": f"Source {n}", "url": f"https://example.com/{n}"}
                for n in range(4)
            ],
            "quiz": {
                "question": "What follows?",
                "options": ["A", "B", "C"],
                "answer": 1,
                "explanation": "The body supports B.",
            },
        }

    def test_deterministic_quality_score_cannot_be_self_awarded(self):
        self.meta["confidence"] = 100
        score = inbox._quality_score(self.meta, self.layers)
        self.assertLessEqual(score, 95)
        self.assertGreaterEqual(score, 80)

    def test_source_gate_rejects_duplicate_urls(self):
        self.meta["sources"] = [
            {"name": "Repeated", "url": "https://example.com/same"}
        ] * 4
        problems = inbox._rule_check(self.meta, self.layers)
        self.assertTrue(any("unikátních HTTPS zdrojů" in p for p in problems))

    def test_ordinary_news_cannot_claim_a_scheduled_slot(self):
        meta = dict(self.meta, automation_generated=False, edition_slot=1)
        problems = inbox._edition_check(meta, self.layers)
        self.assertTrue(any("běžný článek" in problem for problem in problems))

    def test_scheduled_slot_must_match_plan_contract(self):
        meta = dict(self.meta, section="world", type="news", status="published")
        problems = inbox._edition_check(meta, "Too short for the assigned slot. " * 40)
        self.assertTrue(any("patří rubrice" in problem for problem in problems))
        self.assertTrue(any("vyžaduje typ" in problem for problem in problems))
        self.assertTrue(any("plán vyžaduje" in problem for problem in problems))
        self.assertTrue(any("status: draft" in problem for problem in problems))


class EditionCompletenessTests(unittest.TestCase):
    @staticmethod
    def _meta(spec, day="2026-08-13"):
        slot = int(spec["slot"])
        return {
            "slug": f"slot-{slot}", "title": f"Slot {slot}", "lang": "en", "date": day,
            "section": spec["section"], "type": spec["type"],
            "status": "reserve" if slot == 7 else "draft",
            "automation_generated": True, "edition_slot": slot,
            "quiz": {"question": "What does the evidence show?", "options": ["A", "B", "C"],
                     "answer": 1, "explanation": "The evidence in the article supports B."},
        }

    def test_guard_requires_six_public_slots_and_only_warns_for_reserve(self):
        config.site()  # Fill the config cache before redirecting DATA in this isolated test.
        plan = edition.build(dt.date(2026, 8, 13))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content, data = root / "content", root / "data"
            (content / "inbox").mkdir(parents=True)
            (content / "en").mkdir()
            (data / "daily-agenda").mkdir(parents=True)
            (data / "daily-agenda" / "2026-08-13.md").write_text("# Agenda\n", encoding="utf-8")
            for spec in plan["slots"]:
                words = "useful " * int(spec["min_words"])
                path = content / "inbox" / f"slot-{spec['slot']}.md"
                path.write_text(article.dump(self._meta(spec), words), encoding="utf-8")
            with mock.patch.object(config, "CONTENT", content), mock.patch.object(config, "DATA", data):
                errors, warnings = edition_guard.inspect(dt.date(2026, 8, 13))
            self.assertEqual([], errors)
            self.assertTrue(any("slot 7" in warning for warning in warnings))

    def test_guard_rejects_duplicate_public_slot(self):
        config.site()
        plan = edition.build(dt.date(2026, 8, 13))
        spec = plan["slots"][0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content, data = root / "content", root / "data"
            (content / "inbox").mkdir(parents=True)
            (content / "en").mkdir()
            (data / "daily-agenda").mkdir(parents=True)
            (data / "daily-agenda" / "2026-08-13.md").write_text("# Agenda\n", encoding="utf-8")
            body = "useful " * int(spec["min_words"])
            for suffix in ("a", "b"):
                meta = self._meta(spec)
                meta["slug"] += suffix
                (content / "inbox" / f"slot-{suffix}.md").write_text(
                    article.dump(meta, body), encoding="utf-8")
            with mock.patch.object(config, "CONTENT", content), mock.patch.object(config, "DATA", data):
                errors, _ = edition_guard.inspect(dt.date(2026, 8, 13))
            self.assertTrue(any("obsazen 2krát" in error for error in errors))

    def test_guard_accepts_public_slots_after_publication(self):
        config.site()
        plan = edition.build(dt.date(2026, 8, 13))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content, data = root / "content", root / "data"
            (content / "inbox").mkdir(parents=True)
            (content / "en").mkdir()
            (data / "daily-agenda").mkdir(parents=True)
            (data / "daily-agenda" / "2026-08-13.md").write_text(
                "# Agenda\n", encoding="utf-8"
            )
            # Ranní úloha plán zapisuje na disk a hlídač ho pak jen čte.
            # Bez toho by si ho přepočítal nad prázdným obsahem a soudil
            # vydání podle jiných rubrik, než pro které se psalo.
            (data / "edition-plan.json").write_text(
                json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            for spec in plan["slots"]:
                words = "useful " * int(spec["min_words"])
                meta = self._meta(spec)
                meta["status"] = "published"
                path = content / "en" / f"2026-08-13-slot-{spec['slot']}.md"
                path.write_text(article.dump(meta, words), encoding="utf-8")
            with mock.patch.object(config, "CONTENT", content), mock.patch.object(
                config, "DATA", data
            ):
                errors, warnings = edition_guard.inspect(dt.date(2026, 8, 13))
            self.assertEqual([], errors)
            self.assertTrue(any("slot 7" in warning for warning in warnings))

    def test_inbox_gate_still_rejects_published_submission(self):
        plan = edition.build(dt.date(2026, 8, 13))
        spec = plan["slots"][0]
        meta = self._meta(spec)
        meta["status"] = "published"
        body = "useful " * int(spec["min_words"])
        problems = inbox._edition_check(meta, body)
        self.assertTrue(any("status: draft" in problem for problem in problems))


class QmaAndQuizTests(unittest.TestCase):
    def test_contextual_qma_link_contains_measurable_attribution(self):
        meta = {
            "slug": "ai-grid-test", "section": "tech", "title": "AI infrastructure",
            "dek": "Data centers", "topics": ["tech"], "tickers": ["NVDA"],
        }
        target = build._qma_target(meta, config.site()["wider_lens"])
        self.assertEqual("/stocks/NVDA", target["path"])
        self.assertIn("utm_source=mypaper", target["url"])
        self.assertIn("utm_content=ai-grid-test", target["url"])

    def test_quiz_requires_three_answers_and_valid_index(self):
        self.assertIsNone(build._clean_quiz({"quiz": {
            "question": "Q", "options": ["A", "B"], "answer": 1,
            "explanation": "Because",
        }}))


if __name__ == "__main__":
    unittest.main()
