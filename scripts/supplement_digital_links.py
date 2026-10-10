#!/usr/bin/env python3
"""Targeted, resumable GW repair and ISTC full-record link extraction."""
import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/collections/digital-supplement'
PLAN=ROOT/'data/collections/digital-review/supplement-plan.json'

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.active=None; self.text=[]; self.refresh=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='meta' and attrs.get('http-equiv','').lower()=='refresh':
            m=re.search(r'url\s*=\s*(.*)',attrs.get('content',''),re.I)
            if m:self.refresh=m.group(1).strip(' \'"')
        if tag=='a':self.active={'url':attrs.get('href',''),'label':'','preceding_text':' '.join(self.text)[-300:]}
    def handle_data(self,text):
        self.text.append(text)
        if self.active is not None:self.active['label']+=text
    def handle_endtag(self,tag):
        if tag=='a' and self.active is not None:
            self.active['label']=' '.join(self.active['label'].split());self.links.append(self.active);self.active=None

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temp.replace(path)

def parse_gw(raw,url):
    if not re.search(r'<title>\s*GW\. Incunable\s+',raw,re.I):raise ValueError('Unrecognized GW page')
    page=Page();page.feed(raw)
    if page.refresh:
        target=urljoin(url,page.refresh)
        if urlsplit(target).hostname not in ('gesamtkatalogderwiegendrucke.de','www.gesamtkatalogderwiegendrucke.de') or not urlsplit(target).path.startswith('/docs/'):
            raise ValueError('Unexpected GW referral target')
        return [],target
    if 'Gesamtkatalog' not in raw:raise ValueError('GW footer missing')
    return [dict(url=urljoin(url,x['url']),label=x['label']) for x in page.links if 'digitalisat' in x['label'].lower()],None

def parse_istc(raw,url,identifier):
    page=Page();page.feed(raw)
    if 'making sure' in raw.lower() or 'anubis' in raw.lower():raise ValueError('CERL access challenge')
    if identifier.lower() not in raw.lower() or 'incunabula short title' not in raw.lower():raise ValueError('Unrecognized ISTC record page')
    links=[]
    for x in page.links:
        target=urljoin(url,x['url']);host=urlsplit(target).hostname or ''
        if urlsplit(target).scheme not in ('http','https') or host=='cerl.org' or host.endswith('.cerl.org'):continue
        # Retain all external references, but do NOT label unrelated references as scans.
        explicit=bool(re.search(r'facsimile|digit(al|isat)|reproduction',x['label'],re.I))
        links.append(dict(url=target,label=x['label'],preceding_text=x['preceding_text'],classification='digitisation_candidate' if explicit else 'external_reference_requires_review'))
    return links

last_request=0

def fetch(url,agent):
    global last_request
    time.sleep(max(0,2-(time.monotonic()-last_request)));last_request=time.monotonic()
    with urlopen(Request(url,headers={'User-Agent':agent,'Accept':'text/html'}),timeout=30) as response:
        raw=response.read().decode(response.headers.get_content_charset() or 'utf-8',errors='replace')
        return raw,response.geturl()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',choices=['GW','ISTC','all'],default='all');ap.add_argument('--limit',type=int,default=10000);args=ap.parse_args()
    plan=json.loads(PLAN.read_text());items=[]
    if args.source in ('all','GW'):items += [dict(source='GW',**x) for x in plan['gw']]
    if args.source in ('all','ISTC'):items += [dict(source='ISTC',url='https://data.cerl.org/istc/'+quote(i,safe=''),istc_ids=[i]) for i in plan['istc_ids']]
    agent=os.environ.get('CERL_USER_AGENT','').strip()
    if args.source in ('all','ISTC') and not agent:raise SystemExit('CERL_USER_AGENT secret is required; never put its value in source code.')
    count=0;errors=0;blocked=0
    try:
        for item in items:
            key=hashlib.sha256(item['url'].encode()).hexdigest();path=OUT/'records'/(key+'.json')
            if path.exists():continue
            if count>=args.limit:break
            count+=1
            result={**item,'retrieved_at':datetime.now(timezone.utc).isoformat(),'level':'edition','mei_id':''}
            try:
                url=item['url'];chain=[]
                for _ in range(6):
                    raw,final=fetch(url,agent if item['source']=='ISTC' else 'Prayer Books in Motion research data reuse')
                    if item['source']=='ISTC':links=parse_istc(raw,final,item['istc_ids'][0]);break
                    links,target=parse_gw(raw,final)
                    if not target:break
                    if target in chain:raise ValueError('GW referral loop')
                    chain.append(url);url=target
                else:raise ValueError('Too many GW referrals')
                result.update(status='extracted',final_url=final,referral_chain=chain,links=links)
                save(path,result);blocked=0
                (OUT/'errors'/(key+'.json')).unlink(missing_ok=True)
            except Exception as error:
                errors+=1;blocked+=1
                result.update(status='error',error_type=type(error).__name__,http_status=getattr(error,'code',None))
                # No raw headers or exception text: keep the CERL credential out of logs.
                save(OUT/'errors'/(key+'.json'),result)
                if item['source']=='ISTC' and blocked>=3:break
            print(f'{item["source"]} {count}: {result["status"]}',flush=True)
    finally:
        records=[json.loads(p.read_text()) for p in (OUT/'records').glob('*.json')]
        candidates=[]
        for row in records:
            for link in row['links']:
                candidates.append(dict(source=row['source'],level='edition',mei_id='',istc_id=' | '.join(row['istc_ids']),source_url=row['url'],resolved_source_url=row['final_url'],source_field='Digitalisat' if row['source']=='GW' else 'full_record_html_external_link',**link))
        save(OUT/'link-candidates.json',candidates)
        save(OUT/'summary.json',dict(expected_gw=len(plan['gw']),expected_istc=len(plan['istc_ids']),completed_gw=sum(x['source']=='GW' for x in records),completed_istc=sum(x['source']=='ISTC' for x in records),candidate_references=len(candidates),errors_this_run=errors))
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
