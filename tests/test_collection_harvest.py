"""Offline checks for catalogue selection and link scope; no network requests."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import harvest_collections as h


class CollectionChecks(unittest.TestCase):
    def test_core_excluded_from_both_supplements_and_overlap_retained(self):
        groups = h.memberships({'a', 'b'}, {'liturgy': {'a', 'c', 'd'}, 'devotional': {'b', 'c', 'e'}})
        self.assertEqual(groups['a'], ['core'])
        self.assertEqual(groups['b'], ['core'])
        self.assertEqual(set(groups['c']), {'liturgy', 'devotional'})
        self.assertEqual(len(groups), 5)

    def test_exact_subject_or_keyword_and_no_bound_with_inference(self):
        self.assertTrue(h.matches({'hostItem': {'subject': 'Literature-devotional'}}, 'devotional'))
        self.assertTrue(h.matches({'hostItem': {'keywords': ['literature-devotional']}}, 'devotional'))
        self.assertFalse(h.matches({'hostItem': {'keywords': ['liturgy']}}, 'liturgy'))
        self.assertFalse(h.matches({'boundWith': [{'subject': 'literature-devotional'}]}, 'devotional'))

    def test_source_link_parser_and_nested_url_fields(self):
        parser = h.Links()
        parser.feed('<a href="https://example.org/scan"><span>Basel</span> UB (Digitalisat)</a>')
        self.assertEqual(parser.links[0]['label'], 'Basel UB (Digitalisat)')
        links = list(h.all_urls({'electronicReproduction': [{'url': 'https://example.org/scan'}]}))
        self.assertEqual(links, [('.electronicReproduction[0].url', 'https://example.org/scan')])

    def test_core_tables_have_new_identifiers_without_duplicates(self):
        rows = [r for filename in h.SOURCE_FILES for r in h.read_source(filename)]
        ids = [r['gw_id'] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        istc = {i for row in rows for i in h.split_istc_ids(row['istc_id'])}
        self.assertTrue({'is00306000', 'is00035000', 'ip00412500'} <= istc)


if __name__ == '__main__':
    unittest.main()
