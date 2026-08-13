import unittest
from pathlib import Path

from engine import inbox


def lens_body(extra=""):
    parts = []
    for layer in ("BRIEFLY", "FACTS", "EVIDENCE", "PERSPECTIVES", "CONTEXT", "DEEPER"):
        text = ("Clear evidence supports this careful explanation. " * 30) + extra
        parts.append(f"## {layer}\n\n{text}")
    return "\n\n".join(parts)


class IntradayContractTests(unittest.TestCase):
    def setUp(self):
        self.meta = {
            "title": "A material change explained",
            "section": "world",
            "type": "analysis",
            "lang": "en",
            "date": "2026-08-13",
            "status": "draft",
            "format": "roundtable",
            "automation_generated": True,
            "automation_role": "intraday",
            "edition_slot": 0,
            "event_id": "example-material-change",
            "generator": "chatgpt-work",
            "sources": [
                {"name": f"Source {n}", "url": f"https://example.com/{n}"}
                for n in range(4)
            ],
        }

    def test_valid_intraday_article_uses_slot_zero(self):
        problems = inbox._edition_check(self.meta, lens_body())
        self.assertEqual([], problems)

    def test_intraday_requires_roundtable_sources_and_event_id(self):
        meta = dict(self.meta, format="", event_id="", sources=[])
        problems = inbox._edition_check(meta, lens_body())
        self.assertTrue(any("format: roundtable" in problem for problem in problems))
        self.assertTrue(any("event_id" in problem for problem in problems))
        self.assertTrue(any("HTTPS" in problem for problem in problems))

    def test_sensitive_intraday_draft_is_held_for_review(self):
        meta = dict(self.meta)
        problems = inbox._rule_check(meta, lens_body(" election "))
        self.assertEqual([], problems)
        self.assertEqual("review", meta["status"])


class VoiceContractTests(unittest.TestCase):
    def test_every_editorial_prompt_loads_or_references_voice_contract(self):
        prompt_dir = Path(__file__).resolve().parents[1] / "engine" / "prompts"
        prompts = [path for path in prompt_dir.iterdir() if path.is_file() and path.name != "VOICE.md"]
        missing = [path.name for path in prompts if "VOICE.md" not in path.read_text(encoding="utf-8")]
        self.assertEqual([], missing)

    def test_roundtable_roles_are_stable_and_transparent(self):
        prompt = (
            Path(__file__).resolve().parents[1] / "engine" / "prompts" / "INTRADAY-DESK.md"
        ).read_text(encoding="utf-8")
        for role in ("KAI · Moderator", "MIRA · Evidence analyst", "ORIN · Risk analyst"):
            self.assertIn(role, prompt)
        self.assertIn("not real people", prompt)


if __name__ == "__main__":
    unittest.main()
