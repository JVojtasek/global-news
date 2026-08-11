import unittest

from engine import article, config


LENS_BODY = """## BRIEFLY

One calm summary with enough words to stand on its own for a reader who stops here today.

## FACTS

The factual account contains enough words for validation and attributes every material claim to the supplied original sources.

## EVIDENCE

Independent sources agree on the central event. One numerical claim still comes from a single primary document and remains qualified.

## PERSPECTIVES

Two documented interpretations explain different parts of the event. Neither is presented as equal where the supporting evidence is not equal.

## CONTEXT

The background explains the mechanism, history and uncertainty in language a general reader can follow without specialist knowledge or invented detail.

## DEEPER

The deeper story asks what the event reveals about human judgement, responsibility and the limits of certainty without preaching a conclusion.
"""


class WiderLensStructureTests(unittest.TestCase):
    def test_public_standard_explains_when_the_label_is_earned(self):
        lens = config.site()["wider_lens"]
        self.assertIn("evidence audit", lens["qualification_en"])
        self.assertIn("audit důkazů", lens["qualification_cs"])

    def test_new_layers_are_parsed_in_editorial_order(self):
        parsed = article.sections(LENS_BODY)
        self.assertIn("EVIDENCE", parsed)
        self.assertIn("PERSPECTIVES", parsed)
        self.assertLess(article.LAYERS.index("EVIDENCE"), article.LAYERS.index("CONTEXT"))

    def test_daily_analysis_requires_evidence_and_perspectives(self):
        meta = {"title": "A deeper test", "section": "world", "type": "daily", "lang": "en"}
        self.assertFalse(any("The Wider Lens" in p for p in article.validate(meta, LENS_BODY)))

        missing = LENS_BODY.replace("## PERSPECTIVES", "## OTHER")
        self.assertTrue(any("PERSPECTIVES" in p for p in article.validate(meta, missing)))

    def test_regular_news_keeps_existing_required_layers(self):
        body = LENS_BODY.replace(
            "## EVIDENCE\n\nIndependent sources agree on the central event. One numerical claim still comes from a single primary document and remains qualified.\n\n",
            "",
        ).replace(
            "## PERSPECTIVES\n\nTwo documented interpretations explain different parts of the event. Neither is presented as equal where the supporting evidence is not equal.\n\n",
            "",
        )
        meta = {
            "title": "A news test", "section": "world", "type": "news", "lang": "en",
            "sources": [{"name": "Example", "url": "https://example.com"}],
        }
        self.assertFalse(any("The Wider Lens" in p for p in article.validate(meta, body)))


if __name__ == "__main__":
    unittest.main()
