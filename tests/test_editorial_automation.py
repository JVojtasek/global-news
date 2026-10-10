import datetime as dt
import json
import os
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

    def test_extra_article_outside_the_edition_uses_slot_zero(self):
        # Otevření prázdné rubriky mimo číslované vydání: slot 0 nic nezabírá,
        # ale nesmí propustit hotový text rovnou na web.
        meta = dict(self.meta, section="travel", edition_slot=0,
                    automation_role="edition", generator="claude-cowork")
        self.assertEqual([], inbox._edition_check(meta, self.layers))
        published = dict(meta, status="published")
        self.assertTrue(
            any("mimo vydání" in problem
                for problem in inbox._edition_check(published, self.layers))
        )

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
            # Provoz si plán dne zmrazí do data/edition-plan.json a hlídač
            # čte právě ten. Test to musí udělat taky — jinak si hlídač
            # plán přepočítá nad prázdnou složkou článků, vyjde mu jiné
            # pořadí rubrik (hladové rubriky jdou dopředu) a spadne to
            # na rozdílu, který v provozu nikdy nenastane.
            (data / "edition-plan.json").write_text(json.dumps(plan), encoding="utf-8")
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


class EditionGuardTriggerTests(unittest.TestCase):
    """Kdy smí hlídač shodit běh a kdy jen ohlásí díru.

    10. října 2026 sloučení opravy starých kvízů spustilo ``2 · Redakce``
    pushem. Datum i checkout seděly, sloty v repozitáři chyběly. Ranní
    cron téhož dne ty díry taky viděl a díky continue-on-error doběhl.
    """

    DAY = dt.date(2026, 10, 10)
    GAPS = (["chybí automatický slot 1 (parenting/daily)"], ["chybí výzkumná agenda"])

    def test_prague_day_matches_the_morning_cron_instant(self):
        # cron „35 9 * * *“ je 09:35 UTC. V říjnu je v Praze UTC+2, tedy 11:35
        # téhož kalendářního dne. Zítřejší ranní běh musí soudit zítřek.
        instant = dt.datetime(2026, 10, 11, 9, 35, tzinfo=dt.timezone.utc)
        self.assertEqual(dt.date(2026, 10, 11), edition_guard.edition_day(instant))

    def test_late_utc_evening_is_already_the_next_prague_day(self):
        instant = dt.datetime(2026, 10, 10, 23, 30, tzinfo=dt.timezone.utc)
        self.assertEqual(dt.date(2026, 10, 11), edition_guard.edition_day(instant))

    def test_afternoon_push_clock_stays_on_10_october(self):
        # Selhaný běh 38062617265 začal v 15:11 UTC, v Praze 17:11.
        instant = dt.datetime(2026, 10, 10, 15, 11, tzinfo=dt.timezone.utc)
        self.assertEqual(self.DAY, edition_guard.edition_day(instant))

    def test_historical_quiz_fix_is_not_the_morning_signal(self):
        event = {"commits": [{"added": [], "modified": [
            "data/quizzes/2026-08-27-can-your-household-find-the-shutoffs.json",
            "data/quizzes/2026-10-03-can-you-separate-pitch-loudness-and-timbre.json",
        ], "removed": []}], "head_commit": {"added": [], "modified": [
            "data/quizzes/2026-10-03-can-you-separate-pitch-loudness-and-timbre.json",
        ]}}
        self.assertFalse(edition_guard.push_adds_todays_quiz(event, self.DAY))
        self.assertFalse(edition_guard.should_block("push", event, self.DAY))

    def test_added_quiz_for_the_edition_day_is_the_morning_signal(self):
        event = {"head_commit": {"added": [
            "data/quizzes/2026-10-10-can-you-read-a-map.json",
        ]}}
        self.assertTrue(edition_guard.push_adds_todays_quiz(event, self.DAY))
        self.assertTrue(edition_guard.should_block("push", event, self.DAY))

    def test_rewriting_todays_quiz_does_not_reopen_the_hard_gate(self):
        event = {"commits": [{"added": [], "modified": [
            "data/quizzes/2026-10-10-can-you-read-a-map.json",
        ]}]}
        self.assertFalse(edition_guard.push_adds_todays_quiz(event, self.DAY))

    def test_offplan_push_reports_gaps_and_exits_clean(self):
        event = {"commits": [{"modified": [
            "data/quizzes/2026-09-26-can-you-keep-mass-and-weight-apart.json",
        ]}]}
        with mock.patch.object(edition_guard, "inspect", return_value=self.GAPS):
            code = edition_guard.run(self.DAY, event_name="push", event=event)
        self.assertEqual(0, code)

    def test_workflow_dispatch_does_not_block(self):
        with mock.patch.object(edition_guard, "inspect", return_value=self.GAPS):
            code = edition_guard.run(self.DAY, event_name="workflow_dispatch", event={})
        self.assertEqual(0, code)

    def test_schedule_still_fails_a_thin_edition(self):
        with mock.patch.object(edition_guard, "inspect", return_value=self.GAPS):
            code = edition_guard.run(
                dt.date(2026, 10, 11), event_name="schedule", event={"schedule": "35 9 * * *"},
            )
        self.assertEqual(1, code)

    def test_schedule_passes_when_the_six_slots_are_present(self):
        with mock.patch.object(edition_guard, "inspect", return_value=([], [])):
            code = edition_guard.run(
                dt.date(2026, 10, 11), event_name="schedule", event={},
            )
        self.assertEqual(0, code)

    def test_local_run_without_github_event_still_blocks(self):
        cleaned = {key: value for key, value in os.environ.items()
                   if key not in {"GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH"}}
        with mock.patch.dict(os.environ, cleaned, clear=True):
            with mock.patch.object(edition_guard, "inspect", return_value=self.GAPS):
                code = edition_guard.run(self.DAY)
        self.assertEqual(1, code)

    def test_morning_job_stays_alive_when_the_guard_step_fails(self):
        # Krok smí skončit chybou. Celý ranní běh ne: continue-on-error
        # je vázané na schedule a zítřejší cron na tom stojí.
        text = Path(".github/workflows/2-redakce.yml").read_text(encoding="utf-8")
        executable = "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("#")
        )
        self.assertIn(
            "continue-on-error: ${{ github.event_name == 'schedule' }}",
            executable,
        )
        self.assertIn('- cron: "35 9 * * *"', executable)


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
