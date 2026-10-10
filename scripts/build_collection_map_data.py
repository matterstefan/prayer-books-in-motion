#!/usr/bin/env python3
"""Export the reviewed three-collection data for the static map."""
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/collections/place-review/tables'
OUT=ROOT/'data/map'
def read(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
 with (OUT/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 membership=json.loads((ROOT/'data/collections/edition-membership.json').read_text())['edition_membership']
 copies=[r for r in read(SOURCE/'mei-copies.csv') if 'direct' in r['relationship_types'].split(' | ') and r['host_istc_id'] in membership]
 assert len({r['copy_id'] for r in copies})==len(copies)
 for c in copies:
  groups=membership[c['host_istc_id']]
  assert not ('core' in groups and len(groups)>1)
  c['collection_groups']=' | '.join(groups)
 ids={c['copy_id'] for c in copies}
 stations=[s for s in read(SOURCE/'mei-itinerary-stations-final.csv') if s['copy_id'] in ids]
 # Keep fields consumed by the frontend; the full source tables remain separate.
 app=(ROOT/'assets/app.js').read_text()
 def slim(rows,extra):
  keys=[k for k in rows[0] if k in extra or re.search(r'\b'+re.escape(k)+r'\b',app)]
  return [{k:r[k] for k in keys} for r in rows]
 write('copies.csv',slim(copies,{'copy_id','collection_groups'}))
 write('stations.csv',slim(stations,{'copy_id','station_id'}))
 counts={g:sum(g in c['collection_groups'].split(' | ') for c in copies) for g in ['core','liturgy','devotional']}
 (OUT/'summary.json').write_text(json.dumps({'copies':len(copies),'stations':len(stations),'collection_copies':counts,'place_review_date':'2026-10-10'},indent=2)+'\n')
 print(len(copies),'copies;',len(stations),'stations;',counts)
if __name__=='__main__':main()
