import copy
import json
import unittest
from pathlib import Path

from engine import quizzes


FIXTURE = Path("data/quizzes/2026-08-12-calmly-ready-for-72-hours.json")


class DailyQuizTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_first_quiz_is_bilingual_and_actionable(self):
        checked = quizzes._validate(copy.deepcopy(self.raw), FIXTURE)
        self.assertEqual("assessment", checked["mode"])
        self.assertEqual(10, len(checked["questions"]))
        for lang in ("en", "cs"):
            view = quizzes.view(checked, lang)
            self.assertTrue(view["title"])
            self.assertTrue(view["disclaimer"])
            self.assertTrue(all(dim["action"] for dim in view["dimensions"]))

    def test_diagnostic_claim_is_rejected(self):
        unsafe = copy.deepcopy(self.raw)
        unsafe["diagnostic"] = True
        with self.assertRaises(quizzes.QuizValidationError):
            quizzes._validate(unsafe, FIXTURE)

    def test_result_ranges_must_cover_every_possible_score(self):
        broken = copy.deepcopy(self.raw)
        broken["outcomes"][0]["max"] = 6
        with self.assertRaises(quizzes.QuizValidationError):
            quizzes._validate(broken, FIXTURE)

    def test_sources_must_be_unique_https_pages(self):
        broken = copy.deepcopy(self.raw)
        broken["sources"][1]["url"] = broken["sources"][0]["url"]
        with self.assertRaises(quizzes.QuizValidationError):
            quizzes._validate(broken, FIXTURE)


if __name__ == "__main__":
    unittest.main()
