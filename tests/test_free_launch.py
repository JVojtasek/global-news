from pathlib import Path
import unittest
import yaml


ROOT = Path(__file__).resolve().parents[1]

# Workflowy, které nesmí sáhnout na placené modelové API. Sběr zpráv, ranní
# uzávěrka, intradenní brána a publikace webu musí běžet i s prázdnými Secrets.
FREE_WORKFLOWS = (
    "1-sber-zprav.yml",
    "2-redakce.yml",
    "2b-intraday.yml",
    "3-publikace.yml",
    "4-hlidac.yml",
)

# Jediná výjimka: záložní autor. Smí volat API, ale jen aby dopsal slot, který
# ChatGPT Work nedodala — a jeho výstup jde stejným redakčním sítem jako ostatní.
PAID_WORKFLOW = "2c-zalozni-autor.yml"


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

    def test_daily_workflows_never_expose_a_model_key(self):
        """Bez klíče v prostředí nemůže žádný z těchto kroků utratit ani cent."""
        for name in FREE_WORKFLOWS:
            path = ROOT / ".github/workflows" / name
            if not path.exists():
                continue
            text = _executable(path)
            for token in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
                self.assertNotIn(token, text, f"{name} nesmi nacitat {token}")

    def test_editorial_close_never_runs_a_generator(self):
        """Ranní uzávěrka smí články jen převzít a vydat, nikdy je psát."""
        text = _executable(ROOT / ".github/workflows/2-redakce.yml")
        for token in (
            "python -m engine.write",
            "python -m engine.autofill",
            "python -m engine.translate",
            "python -m engine.analyst",
        ):
            self.assertNotIn(token, text, f"2-redakce.yml nesmi spoustet {token}")

    def test_paid_backup_writer_has_a_hard_spending_cap(self):
        """Placené API je povolené, ale nikdy bez stropu a nikdy bez síta."""
        site = yaml.safe_load((ROOT / "data/site.yml").read_text(encoding="utf-8"))
        cap = float(site["ai"]["max_usd_per_day"])

        if not site["ai"]["providers"]:
            # Placená cesta je vypnutá — pak musí být vypnutá úplně.
            self.assertEqual(0.0, cap)
            return

        self.assertGreater(cap, 0.0, "zapnuty poskytovatel bez denniho stropu")
        self.assertLessEqual(cap, 10.0, "denni strop je neprimerene vysoky")
        self.assertTrue(
            str(site["ai"].get("anthropic_model") or "").strip(),
            "zapnuty anthropic bez uvedeneho modelu",
        )

        path = ROOT / ".github/workflows" / PAID_WORKFLOW
        self.assertTrue(path.exists(), "chybi workflow zalozniho autora")
        text = _executable(path)
        # Klíč smí načíst jen krok, který píše. O vydání rozhoduje síto, ne model.
        self.assertIn("python -m engine.autofill", text)
        self.assertIn("python -m engine.inbox", text)
        self.assertNotIn("OPENAI_API_KEY", text)


if __name__ == "__main__":
    unittest.main()
