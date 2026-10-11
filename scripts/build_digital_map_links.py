"""Export compact, separately attributed catalogue links for the static site."""
import json
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
def main():
 rows=json.loads((ROOT/'data/collections/digital-review/digitisation-display-candidates.json').read_text())
 out={'copies':{},'editions':{},'completeness':'not_verified'}
 for row in rows:
  if urlsplit(row['url']).scheme not in ('http','https'):continue
  for kind,key in [('copies','digitisation_copy_ids'),('editions','edition_ids')]:
   for identifier in row[key]:
    refs=[r for r in row['references'] if r['category']=='digitisation_reference' and ((kind=='copies' and r.get('mei_id')==identifier and r.get('level')=='copy') or (kind=='editions' and r.get('level')=='edition' and identifier in [i.strip() for i in r.get('istc_id','').split('|')]))]
    labels=[r.get('label') or (r.get('note') if r['source']=='GW' else '') for r in refs]
    label=next((x for x in labels if x),'Digital resource · '+urlsplit(row['url']).netloc)
    sources=sorted({(r['source'],r['source_url']) for r in refs})
    out[kind].setdefault(identifier,[]).append({'url':row['url'],'label':label,'sources':[{'catalogue':s,'url':u} for s,u in sources]})
 (ROOT/'data/map/digital-links.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
 print('copy entries',len(out['copies']),'edition entries',len(out['editions']))
if __name__=='__main__':main()
