import unittest
from engine.build import _related


def item(slug, title, dek, section='world', date='2026-10-01', tags=''):
    return dict(slug=slug, title=title, dek=dek, section=section, date=date, tags_csv=tags)


class RelatedArticlesTest(unittest.TestCase):
    def test_same_section_alone_does_not_prove_relevance(self):
        source = item('a', 'Rybáři chrání korálové útesy', 'Oceán a pobřežní rybolov')
        unrelated = item('b', 'Volby mění vládu', 'Parlament schválil rozpočet')
        self.assertEqual(_related(source, [source, unrelated], 3), [])

    def test_czech_diacritics_and_newest_tiebreak(self):
        source = item('a', 'Rybáři chrání korálové útesy', 'Oceán a pobřežní rybolov')
        old = item('b', 'Rybáři chrání korálové útesy', 'Oceán', date='2026-09-01')
        new = item('c', 'Rybáři chrání korálové útesy', 'Oceán', date='2026-10-02')
        self.assertEqual([x['slug'] for x in _related(source, [source,old,new], 3)], ['c','b'])

    def test_generic_word_and_article_type_do_not_create_relevance(self):
        source = item('a', 'How rivers recover', 'Fish return to clean water')
        other = item('b', 'How people recover', 'New research into sleep', section='science')
        other['type'] = 'daily'
        self.assertEqual(_related(source, [other], 3), [])
