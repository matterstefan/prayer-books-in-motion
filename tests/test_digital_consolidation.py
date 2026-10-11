import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from consolidate_digital_links import classify,OUT
class Evidence(unittest.TestCase):
 def test_section_boundaries(self):
  base={'source':'ISTC','url':'https://example.org/item','label':'Library','preceding_text':'Digital reproductions'}
  self.assertEqual(classify(base,set())[0],'digitisation_reference')
  self.assertEqual(classify({**base,'preceding_text':'Digital reproductions Library Related resources'},set())[0],'unresolved_resource')
 def test_provenance_not_scan(self):
  self.assertEqual(classify({'source':'MEI','url':'https://example.org/image','source_field':'provenance[0].provenanceImage[0].url'},set())[0],'provenance_image')
 def test_actual_output(self):
  rows=json.loads((OUT/'consolidated-links.json').read_text())
  self.assertEqual(len(rows),len({r['url'] for r in rows}))
  for r in rows:
   self.assertFalse(r['full_scan_verified'])
   for i in r['digitisation_copy_ids']:
    self.assertTrue(any(x.get('mei_id')==i and x.get('level')=='copy' and x['category']=='digitisation_reference' for x in r['references']))
   for i in r['edition_ids']:
    self.assertTrue(any(x.get('level')=='edition' and x['category']=='digitisation_reference' and i in [v.strip() for v in x.get('istc_id','').split('|')] for x in r['references']))
if __name__=='__main__':unittest.main()
