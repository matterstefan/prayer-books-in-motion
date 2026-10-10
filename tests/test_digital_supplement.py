import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from supplement_digital_links import parse_gw,parse_istc
FIX=Path(__file__).parent/'fixtures/digital-links'
class Parsing(unittest.TestCase):
    def test_real_gw_supplement(self):
        links,target=parse_gw((FIX/'GWXI427A.htm').read_text(),'https://gesamtkatalogderwiegendrucke.de/docs/GWXI427A.htm')
        self.assertEqual(links,[]);self.assertIsNone(target)
    def test_real_gw_referral(self):
        _,target=parse_gw((FIX/'M12471.htm').read_text(),'https://gesamtkatalogderwiegendrucke.de/docs/M12471.htm')
        self.assertEqual(target,'https://gesamtkatalogderwiegendrucke.de/docs/GW14405.htm')
    def test_not_empty_success_for_challenge(self):
        with self.assertRaises(ValueError):parse_gw('<title>Making sure you are not a bot</title>','https://example.org')
        with self.assertRaises(ValueError):parse_istc('anubis','https://data.cerl.org/istc/ia00041000','ia00041000')
    def test_istc_conservative_link_labels(self):
        raw='<title>Incunabula Short Title Catalogue ia00041000</title><a href="https://scan.example/1">Electronic <b>facsimile</b></a><a href="https://authority.example/2">Authority</a>'
        links=parse_istc(raw,'https://data.cerl.org/istc/ia00041000','ia00041000')
        self.assertEqual(len(links),2)
        self.assertEqual(links[0]['classification'],'digitisation_candidate')
        self.assertEqual(links[1]['classification'],'external_reference_requires_review')
if __name__=='__main__':unittest.main()
