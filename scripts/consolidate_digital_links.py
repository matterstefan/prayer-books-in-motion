#!/usr/bin/env python3
"""Consolidate catalogue link evidence without claiming scan completeness."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/collections/digital-review'
FOOTER={'British Library','Mike Peel','www.mikepeel.net','CC-BY-SA-4.0'}
def classify(r,corroborated):
    url=r['url'].strip();host=(urlsplit(url).hostname or '').lower()
    field=r.get('source_field','');label=r.get('label','');context=' '.join(r.get('preceding_text','').split())
    if host=='watermark.kb.nl':return 'watermark_resource','watermark database URL'
    if 'provenanceImage' in field:return 'provenance_image','MEI provenanceImage field'
    if r['source']=='MEI' and 'electronicReproduction' in field:return 'digitisation_reference','MEI electronicReproduction field'
    if r['source']=='GW':return 'digitisation_reference','GW Digitalisat label'
    if r['source']=='ISTC':
        if label in FOOTER:return 'page_navigation','repeated footer label'
        if 'gesamtkatalogderwiegendrucke.de' in host or re.match(r'^(GW |BSB-Ink )',label):return 'catalogue_reference','bibliographic reference link'
        headings=list(re.finditer(r'Digital reproductions|Related resources|Watermarks|Reference works|Holdings',context,re.I))
        if headings and headings[-1][0].lower()=='digital reproductions':return 'digitisation_reference','ISTC Digital reproductions section in retained context'
        if re.search(r'electronic\s+facsimile|digitalisat|digital\s+reproduction',label,re.I):return 'digitisation_reference','explicit reproduction label'
        ids={x.strip() for x in r.get('istc_id','').split('|') if x.strip()}
        if any((i,url) in corroborated for i in ids):return 'digitisation_reference','same edition and exact URL corroborated by MEI/GW'
    return 'unresolved_resource','insufficient retained context'

def main():
    original=json.loads((ROOT/'data/collections/digital-link-candidates.json').read_text())
    supplement=json.loads((ROOT/'data/collections/digital-supplement/link-candidates.json').read_text())
    rows=original+supplement
    corroborated={(i.strip(),r['url'].strip()) for r in original if r['source']=='GW' or 'electronicReproduction' in r.get('source_field','') for i in r.get('istc_id','').split('|') if i.strip()}
    with (ROOT/'data/map/copies.csv').open() as f:copies=list(csv.DictReader(f))
    copyids={r['copy_id'] for r in copies}
    grouped={};seen=set()
    for r in rows:
        url=r['url'].strip()
        # Deduplicate a repeated anchor, retaining distinct field/source/copy evidence.
        key=(r['source'],r.get('istc_id'),r.get('mei_id'),r.get('source_url'),r.get('source_field'),url,r.get('label'),r.get('preceding_text'))
        if key in seen:continue
        seen.add(key)
        category,reason=classify(r,corroborated)
        item=grouped.setdefault(url,{'url':url,'references':[],'full_scan_verified':False})
        item['references'].append({**r,'category':category,'classification_basis':reason})
    counts=Counter()
    for url,item in grouped.items():
        refs=item['references'];item['categories']=sorted({r['category'] for r in refs})
        item['copy_ids']=sorted({r['mei_id'] for r in refs if r.get('level')=='copy' and r.get('mei_id') in copyids})
        item['other_mei_ids']=sorted({r['mei_id'] for r in refs if r.get('mei_id') and r['mei_id'] not in copyids})
        # Never promote a MEI-only reference to edition-wide display.
        item['edition_ids']=sorted({i.strip() for r in refs if r.get('level')=='edition' and r['category']=='digitisation_reference' for i in r.get('istc_id','').split('|') if i.strip()})
        item['digitisation_copy_ids']=sorted({r['mei_id'] for r in refs if r.get('level')=='copy' and r.get('mei_id') in copyids and r['category']=='digitisation_reference'})
        check=OUT/'checks'/(hashlib.sha256(url.encode()).hexdigest()+'.json')
        if check.exists():item['availability_check']=json.loads(check.read_text())
        counts.update(item['categories'])
    result=list(grouped.values())
    display=[x for x in result if x['digitisation_copy_ids'] or x['edition_ids']]
    summary={'raw_reference_count':len(rows),'distinct_evidence_references':len(seen),'unique_urls':len(result),'urls_by_category_overlapping':dict(counts),'digitisation_display_candidate_urls':len(display),'visualised_copies_with_direct_digitisation_reference':len({i for x in display for i in x['digitisation_copy_ids']}),'editions_with_digitisation_reference':len({i for x in display for i in x['edition_ids']}),'unresolved_url_count':sum('unresolved_resource' in x['categories'] for x in result),'full_scans_verified':0}
    OUT.mkdir(parents=True,exist_ok=True)
    for name,value in [('consolidated-links.json',result),('digitisation-display-candidates.json',display),('consolidation-summary.json',summary)]:
        (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
