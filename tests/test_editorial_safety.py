import unittest

from engine import safety


class TranslationSafetyTests(unittest.TestCase):
    def test_no_derivatives_article_cannot_be_translated(self):
        meta = {
            "syndicated": {
                "source": "Example",
                "license": "CC BY-ND 4.0",
                "may_translate": False,
            }
        }
        self.assertFalse(safety.translation_allowed(meta))

    def test_ordinary_and_permitted_articles_can_be_translated(self):
        self.assertTrue(safety.translation_allowed({"type": "news"}))
        self.assertTrue(safety.translation_allowed({
            "syndicated": {"license": "CC BY 3.0", "may_translate": True}
        }))

    def test_translation_preserves_licence_author_and_origin(self):
        source = {
            "type": "syndicated",
            "section": "world",
            "sources": [{"name": "Example", "url": "https://example.com/story"}],
            "syndicated": {
                "source": "Example",
                "author": "Jane Reporter",
                "url": "https://example.com/story",
                "license": "CC BY 3.0",
                "attribution": "By Jane Reporter.",
                "may_translate": True,
            },
        }
        translated = {"title": "Přeložený titulek"}

        safety.copy_provenance(source, translated, source_lang="en")

        self.assertEqual(translated["syndicated"], source["syndicated"])
        self.assertEqual(translated["sources"], source["sources"])
        self.assertEqual(translated["translated_from"], "en")


class HumanReviewTests(unittest.TestCase):
    def test_children_health_and_finance_are_sensitive(self):
        enabled = {"medical", "financial", "children"}
        self.assertTrue(safety.is_sensitive("A new treatment for diabetes", enabled))
        self.assertTrue(safety.is_sensitive("How AI affects children at school", enabled))
        self.assertTrue(safety.is_sensitive("Should investors buy this stock?", enabled))

    def test_low_risk_topic_is_not_forced_to_review(self):
        enabled = {"medical", "financial", "children"}
        self.assertFalse(safety.is_sensitive("A museum opens a Roman pottery exhibition", enabled))


if __name__ == "__main__":
    unittest.main()
