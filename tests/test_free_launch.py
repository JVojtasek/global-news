from pathlib import Path
import unittest
import yaml


ROOT = Path(__file__).resolve().parents[1]

# NULOVÉ NÁKLADY JSOU ZÁKLADNÍ PRAVIDLO TĚCHTO NOVIN.
# Žádný workflow v repozitáři nesmí načíst klíč k placenému modelovému API.
# Články píší předplacení asistenti (Claude Code na majitelově počítači,
# naplánované úlohy ChatGPT Work a Cowork). GitHub Actions je jen přebírají,
# kontrolují a vydávají — a u veřejného repozitáře jsou minuty zdarma.
MODEL_KEYS = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")

# Uzávěrky nesmí spustit generátor článků ani omylem.
CLOSE_WORKFLOWS = ("2-redakce.yml", "2c-zalozni-autor.yml")
GENERATORS = (
    "python -m engine.write",
    "python -m engine.autofill",
    "python -m engine.translate",
)


def _executable(path: Path) -> str:
    """Text workflow bez komentářů — v komentářích smí být cokoli."""
    return "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )


class FreeLaunchTest(unittest.TestCase):
    def test_membership_is_free_and_open(self):
        cfg = yaml.safe_load((ROOT / "data/members.yml").read_text(encoding="utf-8"))
        self.assertFalse(cfg["enabled"])
        self.assertEqual(1, len(cfg["tiers"]))
        self.assertEqual(0, cfg["tiers"][0]["price_eur"])

    def test_no_workflow_anywhere_loads_a_model_key(self):
        """Bez klíče v prostředí nemůže žádný běh utratit ani cent."""
        found = list((ROOT / ".github/workflows").glob("*.yml"))
        self.assertTrue(found, "nenalezen zadny workflow")
        for path in found:
            text = _executable(path)
            for token in MODEL_KEYS:
                self.assertNotIn(token, text, f"{path.name} nesmi nacitat {token}")

    def test_closes_never_run_a_generator(self):
        """Uzávěrka smí články jen převzít, zkontrolovat a vydat."""
        for name in CLOSE_WORKFLOWS:
            path = ROOT / ".github/workflows" / name
            if not path.exists():
                continue
            text = _executable(path)
            for token in GENERATORS:
                self.assertNotIn(token, text, f"{name} nesmi spoustet {token}")

    def test_paid_model_api_is_switched_off(self):
        """Konfigurace nesmí mít zapnutého poskytovatele ani rozpočet."""
        site = yaml.safe_load((ROOT / "data/site.yml").read_text(encoding="utf-8"))
        self.assertEqual([], site["ai"]["providers"])
        self.assertEqual(0.0, float(site["ai"]["max_usd_per_day"]))


if __name__ == "__main__":
    unittest.main()
