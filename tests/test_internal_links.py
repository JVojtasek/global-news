"""Odkazy z článků na stálé stránky — země a velké problémy.

Ty dvě rubriky jsou to nejužitečnější, co web má, a dlouho na ně
z článků nevedl jediný odkaz. Nedostal se k nim tedy ani čtenář, ani
vyhledávač. Testy hlídají obojí: že odkaz vznikne, když má, a hlavně
že nevznikne, když nemá — řádek nalepený pod každý článek by přestal
něco znamenat.
"""
import unittest

from engine import build, config, problems


ART = ("Antibiotics stopped working in three wards", "")


class ProblemMatchTests(unittest.TestCase):
    def test_one_passing_mention_is_not_enough(self):
        meta = {"title": "The budget in one page", "dek": "", "lang": "en"}
        body = "The minister mentioned housing once and moved on."

        self.assertEqual([], problems.match(meta, body, "en"))

    def test_a_real_subject_matches(self):
        meta = {"title": "Rent control returns", "dek": "", "lang": "en"}
        body = ("Rent control is back on the table. Social housing waiting "
                "lists grew again, and renters are paying more of their pay "
                "than at any point since the housing crash.")

        self.assertIn("housing", problems.match(meta, body, "en"))

    def test_czech_endings_are_matched(self):
        meta = {"title": "Dezinformace před volbami", "dek": "", "lang": "cs"}
        body = ("Dezinformací přibylo. Ověřování faktů nestíhá a propaganda "
                "se šíří rychleji, než ji dezinformační týmy stačí značit.")

        self.assertIn("disinformation", problems.match(meta, body, "cs"))

    def test_never_more_than_two_links(self):
        meta = {"title": "Everything at once", "dek": "", "lang": "en"}
        body = (("housing homeless rent control drought water supply reservoir "
                 "teacher classroom curriculum plastic landfill microplastic ")
                * 3)

        self.assertLessEqual(len(problems.match(meta, body, "en")), 2)

    def test_unfinished_pages_are_never_linked(self):
        # Odkaz na rozepsanou stránku by skončil na 404.
        ready = {p["id"] for p in problems.load("en")}
        meta = {"title": "Rent control returns", "dek": "", "lang": "en"}
        body = "Rent control, social housing and homeless counts, all housing." * 2

        for pid in problems.match(meta, body, "en"):
            self.assertIn(pid, ready)

    def test_every_configured_problem_has_words_in_both_languages(self):
        block = (config.site().get("problems") or {}).get("match") or {}
        for pid in {p["id"] for p in problems.load("en")}:
            self.assertIn(pid, block, f"{pid} nemá v site.yml žádná slova")
            for lang in ("en", "cs"):
                self.assertTrue(block[pid].get(lang),
                                f"{pid} nemá slova pro jazyk {lang}")


class ShareImageTests(unittest.TestCase):
    def test_article_without_a_photo_gets_the_paper_image(self):
        site = config.site()
        shared = build._share_image({}, site)

        self.assertTrue(shared.startswith("http"), shared)
        self.assertTrue(shared.endswith(".jpg"), shared)

    def test_a_real_photo_always_wins(self):
        site = config.site()

        self.assertIn("/covers/x.jpg", build._share_image({"image": "/covers/x.jpg"}, site))


class StringsTests(unittest.TestCase):
    def test_both_languages_know_the_same_words(self):
        self.assertEqual(set(build.STRINGS["en"]), set(build.STRINGS["cs"]))

    def test_the_new_row_is_translated(self):
        for lang in ("en", "cs"):
            for key in ("row_where", "row_problem"):
                self.assertTrue(build.STRINGS[lang][key].strip())


if __name__ == "__main__":
    unittest.main()
