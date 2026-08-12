from pathlib import Path
import unittest
import yaml


ROOT = Path(__file__).resolve().parents[1]


class FreeLaunchTest(unittest.TestCase):
    def test_membership_is_free_and_open(self):
        cfg = yaml.safe_load((ROOT / "data/members.yml").read_text(encoding="utf-8"))
        self.assertFalse(cfg["enabled"])
        self.assertEqual(1, len(cfg["tiers"]))
        self.assertEqual(0, cfg["tiers"][0]["price_eur"])

    def test_paid_model_api_is_disabled(self):
        site = yaml.safe_load((ROOT / "data/site.yml").read_text(encoding="utf-8"))
        self.assertEqual([], site["ai"]["providers"])
        self.assertEqual(0.0, float(site["ai"]["max_usd_per_day"]))

        workflow = (ROOT / ".github/workflows/2-redakce.yml").read_text(encoding="utf-8")
        forbidden = (
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "python -m engine.write",
            "python -m engine.translate",
            "python -m engine.analyst",
        )
        # Explanatory comments may mention secret names. Executable lines must not.
        executable = "\n".join(
            line for line in workflow.splitlines()
            if not line.lstrip().startswith("#")
        )
        for token in forbidden:
            self.assertNotIn(token, executable)


if __name__ == "__main__":
    unittest.main()
