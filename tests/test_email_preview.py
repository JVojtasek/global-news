import datetime as dt
import unittest
from engine.email_preview import select_articles, render_preview

class EmailPreviewTest(unittest.TestCase):
    def test_topics_and_freshness(self):
        rows = [dict(u='/cs/test/', t='Test', d='Popis', dt='2026-10-29', g='space'),
                dict(u='/cs/old/', t='Starý', dt='2026-10-20', g='space'),
                dict(u='//evil.test/', t='Bad', dt='2026-10-29', g='space')]
        self.assertEqual([x['t'] for x in select_articles(rows, ['space'], 'cs', dt.date(2026,10,29))], ['Test'])
    def test_section_matches_untagged_article(self):
        row = dict(u='/cs/world/', t='Zpráva', dt='2026-10-29', s='world', g='')
        self.assertEqual(select_articles([row], [], 'cs', dt.date(2026,10,29), sections=['world']), [row])
        with self.assertRaises(ValueError):
            select_articles([row], [], 'cs', dt.date(2026,10,29), sections=['health'])

    def test_freshness_and_language_are_enforced(self):
        rows = [dict(u='/en/wrong/', t='Wrong', dt='2026-10-29', s='world'),
                dict(u='/cs/future/', t='Future', dt='2026-10-30', s='world'),
                dict(u='/cs/\\evil/', t='Escape', dt='2026-10-29', s='world'),
                dict(u='/cs/ok/', t='Good', dt='2026-10-29', s='world'),
                dict(u='/cs/ok/', t='Duplicate', dt='2026-10-29', s='world')]
        self.assertEqual([x['t'] for x in select_articles(rows, [], 'cs', dt.date(2026,10,29), sections=['world'])], ['Good'])

    def test_health_rejected(self):
        with self.assertRaises(ValueError):
            select_articles([], ['h_diabetes'], 'cs', dt.date(2026,10,29))
    def test_preview_escapes_html(self):
        row = dict(u='/cs/test/', t='<script>', d='A & B', dt='2026-10-29', g='space')
        result = render_preview([row], ['space'], 'cs', dt.date(2026,10,29))
        self.assertIn('&lt;script&gt;', result)
        self.assertIn('A &amp; B', result)
        self.assertNotIn('<script>', result)

if __name__ == '__main__': unittest.main()
