import datetime as dt
import unittest

from engine import article, build, config, edition, inbox, refresh


class EditionPlanTests(unittest.TestCase):
    def test_four_new_two_refreshes_and_reserve_are_planned(self):
        plan = edition.build(dt.date(2026, 8, 12))
        self.assertEqual(6, plan["output_count"])
        self.assertEqual(4, plan["public_count"])
        self.assertEqual(2, plan["refresh_count"])
        self.assertEqual(6, len({slot["section"] for slot in plan["slots"]}))
        self.assertEqual([1, 2, 3, 4, 5, 6], [slot["slot"] for slot in plan["slots"]])
        self.assertEqual(["new"] * 4 + ["refresh"] * 2,
                         [slot["action"] for slot in plan["slots"]])
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
            "section": "tech",
            "type": "analysis",
            "lang": "en",
            "automation_generated": True,
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

    def test_value_article_requires_cluster_and_practical_asset(self):
        self.meta["value_article"] = True
        problems = inbox._rule_check(self.meta, self.layers)
        self.assertTrue(any("pillar" in p for p in problems))
        self.assertTrue(any("practical_asset" in p for p in problems))


class RefreshGateTests(unittest.TestCase):
    def test_refresh_target_cannot_escape_english_content(self):
        target, problems = refresh._target({"refresh_target": "../../etc/passwd"})
        self.assertIsNone(target)
        self.assertTrue(any("content/en" in p for p in problems))

    def test_refresh_cannot_change_stable_url_fields(self):
        original = {"slug": "stable", "lang": "en", "date": "2026-01-01", "section": "meaning"}
        updated = {
            **original, "slug": "changed", "title": "Changed", "type": "analysis",
            "status": "published", "refresh_reason": "Added a new systematic review",
            "updated_at": "2026-08-11",
            "sources": [{"name": f"S{n}", "url": f"https://example.com/{n}"} for n in range(4)],
        }
        body = "\n\n".join(
            f"## {name}\n\n" + "\n\n".join(["Clear evidence supports this careful explanation. " * 12] * 4)
            for name in ("BRIEFLY", "FACTS", "EVIDENCE", "PERSPECTIVES", "CONTEXT", "DEEPER")
        )
        problems = refresh._check(original, body, updated, body)
        self.assertTrue(any("slug" in p for p in problems))


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

    def test_related_articles_prefer_same_evergreen_cluster(self):
        base = {"slug": "a", "title": "Completely different words", "dek": "Unique summary",
                "section": "meaning", "type": "daily", "date": "2026-08-11",
                "pillar": "mental-resilience", "cluster": "burnout-recovery"}
        same = {**base, "slug": "b", "date": "2026-08-10", "section": "health"}
        generic = {**base, "slug": "c", "date": "2026-08-09", "pillar": "other",
                   "cluster": "other", "title": "Completely different words"}
        self.assertEqual("b", build._related(base, [same, generic], 1)[0]["slug"])


if __name__ == "__main__":
    unittest.main()
