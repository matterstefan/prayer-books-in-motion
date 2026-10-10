#!/usr/bin/env python3
"""Conservative, resumable URL audit. A reachable page is NOT a verified full scan."""
import argparse
import csv
import hashlib
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/collections/digital-review'

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    tmp.replace(path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()
    rows = json.loads((ROOT/'data/collections/digital-link-candidates.json').read_text())
    with (ROOT/"data/map/copies.csv").open() as source:
        visualised_ids = {row["copy_id"] for row in csv.DictReader(source)}
    links = {}
    for row in rows:
        url = row['url'].strip()
        entry = links.setdefault(url, {'url': url, 'source_references': [], 'full_scan_verified': False})
        # Preserve every original reference, including untrimmed source URLs.
        entry['source_references'].append(row)
    for url, item in links.items():
        refs = item['source_references']
        host = urlsplit(url).netloc.lower()
        fields = [r.get('source_field','') for r in refs]
        if host == 'watermark.kb.nl':
            kind = 'watermark_resource_candidate'
        elif fields and all('provenanceImage' in f for f in fields):
            kind = 'provenance_image_reference'
        else:
            kind = 'digitisation_candidate_unverified'
        item['source_based_classification'] = kind
        item['attribution'] = 'copy_reference_present' if any(r.get('level')=='copy' for r in refs) else 'edition_only'
        item['visualised_mei_ids'] = sorted({r.get('mei_id') for r in refs if r.get('mei_id') in visualised_ids})
        item['other_mei_ids'] = sorted({r.get('mei_id') for r in refs if r.get('mei_id') and r.get('mei_id') not in visualised_ids})
        item['check_id'] = hashlib.sha256(url.encode()).hexdigest()
    save(OUT/'link-inventory.json', list(links.values()))
    # Spread first checks over hosts. CERL requires separate authorized access:
    # do not request its protected sites or embed any access secret here.
    ordered = sorted(links.values(), key=lambda x: x['attribution']!='copy_reference_present')
    seen_hosts = set()
    priority, rest = [], []
    for item in ordered:
        host = urlsplit(item['url']).netloc.lower()
        (rest if host in seen_hosts else priority).append(item)
        seen_hosts.add(host)
    count = 0
    for item in priority + rest:
        url = item['url']; parts = urlsplit(url)
        path = OUT/'checks'/(item['check_id']+'.json')
        if path.exists() or parts.scheme not in ('http','https') or (parts.hostname or '').endswith('cerl.org'):
            continue
        if count >= args.limit: break
        result = {'url':url, 'checked_at':datetime.now(timezone.utc).isoformat(), 'full_scan_verified':False}
        try:
            request = Request(url,headers={'User-Agent':'Prayer Books in Motion research link audit'})
            with urlopen(request,timeout=12) as response:
                raw = response.read(262144)
                text = raw.decode(response.headers.get_content_charset() or 'utf-8',errors='replace')
                title = re.search(r'<title[^>]*>(.*?)</title>',text,re.I|re.S)
                result.update(http_status=response.status, final_url=response.geturl(), content_type=response.headers.get('Content-Type'), title=re.sub(r'\s+',' ',title.group(1)).strip() if title else None, sample_bytes=len(raw), status='reachable_unverified')
                if any(v in text.lower() for v in ["making sure you're not a bot",'just a moment...','verify you are human']):
                    result['status']='access_challenge'
        except HTTPError as error:
            result.update(http_status=error.code,status='http_error_requires_review')
        except Exception as error:
            result.update(status='environment_access_blocked' if 'Tunnel connection failed' in str(error) else 'request_failed_requires_review',error_type=type(error).__name__,error=str(error)[:300])
        save(path,result)
        count+=1
        print(f'{count}: {parts.netloc}: {result["status"]}',flush=True)
        time.sleep(1.1)
    checks = [json.loads(p.read_text()) for p in (OUT/'checks').glob('*.json')] if (OUT/'checks').exists() else []
    current_ids = {x['check_id'] for x in links.values()}
    checks = [x for x in checks if hashlib.sha256(x['url'].encode()).hexdigest() in current_ids]
    summary = {'candidate_references':len(rows),'unique_trimmed_urls':len(links),'source_references':dict(Counter(r['source'] for r in rows)), 'source_based_classification':dict(Counter(x['source_based_classification'] for x in links.values())), 'attribution':dict(Counter(x['attribution'] for x in links.values())), 'checked_urls':len(checks),'check_status':dict(Counter(x['status'] for x in checks)), 'remaining_unchecked':len(links)-len(checks),'full_scans_verified':0}
    save(OUT/'summary.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
