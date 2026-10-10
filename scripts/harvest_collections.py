#!/usr/bin/env python3
"""Harvest three explicitly defined collections without changing live website data.

Resumable raw queries retain source timestamps. Supplementary collections exclude
all core ISTC identifiers and may overlap with each other. Digital links are
unverified candidates: edition links are never attributed to a particular copy.
"""
import hashlib
import json
import re
import argparse
import time
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import fetch_mei_pilot as api
from build_corpus import SOURCE_FILES, read_source, split_istc_ids
from fetch_mei_corpus import validate_cached

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/collections'
CACHE = ROOT / 'data/cache/collection-harvest'
QUERIES = {
    'liturgy': 'data.hostItem.subject:"liturgy"',
    'devotional': 'data.hostItem.subject:"literature-devotional" OR data.hostItem.keywords:"literature-devotional"',
}


def terms(value):
    return [str(v).strip().lower() for v in (value if isinstance(value, list) else [value]) if v]


def matches(record, group):
    host = record.get('hostItem', {})
    subject = terms(host.get('subject'))
    if group == 'liturgy':
        return 'liturgy' in subject
    return 'literature-devotional' in subject + terms(host.get('keywords'))


def memberships(core, discovered):
    result = {i: ['core'] for i in core}
    for group, identifiers in discovered.items():
        for identifier in identifiers - core:
            result.setdefault(identifier, []).append(group)
    return result


def cached_query(query, endpoint, limiter, legacy=None):
    digest = hashlib.sha256((endpoint + '\n' + query).encode()).hexdigest()
    path = CACHE / (digest + '.json')
    for candidate in [path, legacy]:
        if candidate and candidate.exists():
            result = json.loads(candidate.read_text(encoding='utf-8'))
            old = api.API_ENDPOINT
            try:
                api.API_ENDPOINT = endpoint
                validate_cached(result, query)
            finally:
                api.API_ENDPOINT = old
            return result
    old = api.API_ENDPOINT
    try:
        api.API_ENDPOINT = endpoint
        result = api.fetch_complete_query(query, limiter)
    finally:
        api.API_ENDPOINT = old
    api.atomic_write_json(path, result)
    return result


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.active = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.active = {'url': dict(attrs).get('href', ''), 'label': ''}

    def handle_data(self, text):
        if self.active is not None:
            self.active['label'] += text

    def handle_endtag(self, tag):
        if tag == 'a' and self.active is not None:
            self.links.append(self.active)
            self.active = None


def gw_links(url, limiter):
    path = CACHE / ('gw-' + hashlib.sha256(url.encode()).hexdigest() + '.json')
    if path.exists():
        return json.loads(path.read_text())
    limiter.wait()
    with urlopen(Request(url, headers={'User-Agent': 'Prayer Books in Motion research data reuse'}), timeout=45) as response:
        raw = response.read().decode(response.headers.get_content_charset() or 'utf-8')
    if 'bn9-11' not in raw or 'Gesamtkatalog' not in raw:
        raise ValueError('Response is not a recognizable GW entry; not caching empty links')
    parser = Links()
    parser.feed(raw)
    result = {'source_url': url, 'retrieved_at': api.now_iso(), 'links': [
        {'url': urljoin(url, link['url']), 'label': ' '.join(link['label'].split())}
        for link in parser.links if 'digitalisat' in link['label'].lower()
    ]}
    api.atomic_write_json(path, result)
    return result


def all_urls(value, path=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from all_urls(child, path + '.' + key)
    elif isinstance(value, list):
        for n, child in enumerate(value):
            yield from all_urls(child, path + f'[{n}]')
    elif isinstance(value, str) and value.startswith(('https://', 'http://')):
        yield path, value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gw-minutes', type=float, default=80,
                        help='Time budget for new GW requests; completed queries remain cached')
    args = parser.parse_args()
    if args.gw_minutes <= 0:
        parser.error('--gw-minutes must be positive')
    api.access_user_agent()
    OUT.mkdir(parents=True, exist_ok=True)
    limiter = api.RateLimiter(2)
    core_rows = [row for filename in SOURCE_FILES for row in read_source(filename)]
    core = {i for row in core_rows for i in split_istc_ids(row['istc_id'])}
    discovered = {}
    status = {'started_at': api.now_iso(), 'complete': False, 'digital_link_errors': [],
              'istc_unresolved_identifiers': []}
    api.atomic_write_json(OUT / 'harvest-status.json', status)
    for group, query in QUERIES.items():
        print('Discovering', group, flush=True)
        result = cached_query(query, api.API_ENDPOINT, limiter)
        exact = [r for r in result['rows'] if matches(r, group)]
        if any(not r.get('hostItemId') for r in exact):
            raise ValueError('Matching MEI record lacks its edition identifier')
        discovered[group] = {r['hostItemId'] for r in exact}
        print(group, len(exact), 'matching records;', len(discovered[group]), 'editions', flush=True)
    groups = memberships(core, discovered)
    identifiers = sorted(groups)
    api.atomic_write_json(OUT / 'edition-membership.json', {'compiled_at': api.now_iso(), 'queries': QUERIES,
        'core_sources': list(SOURCE_FILES), 'edition_membership': groups})
    results = []
    for n, identifier in enumerate(identifiers, 1):
        print(f'MEI {n}/{len(identifiers)}: {identifier}', flush=True)
        result = cached_query(identifier, api.API_ENDPOINT, limiter,
                              ROOT / 'data/cache/mei-corpus' / (identifier + '.json'))
        results.append(result)
    # Use the most recently retrieved representation when records recur across
    # queries. Keep each raw response in the cache and report version differences.
    latest = {}
    conflicts = set()
    for result in sorted(results, key=lambda r: r['retrieved_at']):
        for record in result['rows']:
            identifier = str(record['id'])
            if identifier in latest and latest[identifier] != record:
                conflicts.add(identifier)
            latest[identifier] = record
    normalized = []
    for result in results:
        normalized.append(({**result, 'rows': [latest[str(r['id'])] for r in result['rows']]}, True))
    combined = api.combine_queries(identifiers, normalized)
    combined['metadata'].update(purpose='Core plus additional liturgical and devotional editions',
        selection_file='data/collections/edition-membership.json', complete=True,
        version_differences=sorted(conflicts), version_policy='Latest retrieved representation; raw versions retained in query cache')
    # loaded_from_cache in combine_queries is not meaningful after normalization.
    for meta in combined['metadata']['query_results'].values():
        meta.pop('loaded_from_cache', None)
    api.atomic_write_json(OUT / 'mei-collections.json', combined)
    status.update(mei_complete=True, editions=len(groups),
        direct_mei_records=len({r['mei_id'] for r in combined['relationships'] if r['relation_type']=='direct'}))
    api.atomic_write_json(OUT / 'harvest-status.json', status)
    candidates = []
    direct = {r['mei_id'] for r in combined['relationships'] if r['relation_type'] == 'direct'}
    for record in combined['records']:
        for field in ['electronicReproduction', 'provenance']:
            for path, url in all_urls(record.get(field, []), field):
                if field == 'provenance' and 'provenanceImage' not in path:
                    continue
                candidates.append(dict(source='MEI', level='copy', mei_id=record['id'],
                    istc_id=record.get('hostItemId', ''), url=url, source_field=path,
                    note='Unverified: may be full scan, selected images or catalogue page',
                    source_url='https://data.cerl.org/mei/' + str(record['id'])))
    api.atomic_write_json(OUT / 'digital-link-candidates.json', candidates)
    istc_records = {}
    consecutive_istc_errors = 0
    for n, identifier in enumerate(identifiers, 1):
        print(f'ISTC {n}/{len(identifiers)}: {identifier}', flush=True)
        try:
            result = cached_query('_id:' + identifier, 'https://data.cerl.org/istc/_search', limiter)
            exact = [r for r in result['rows'] if str(r.get('id', r.get('_id', ''))) == identifier]
            if result['reported_hits'] == 0:
                status['istc_unresolved_identifiers'].append(identifier)
                consecutive_istc_errors = 0
                continue
            if len(exact) != 1:
                raise ValueError('ISTC exact record not found')
            istc_records[identifier] = exact[0]
            consecutive_istc_errors = 0
            for path, url in all_urls(exact[0]):
                # Retain all ISTC URLs for inspection instead of assuming a schema
                # or mistaking an edition-level link for a copy-level facsimile.
                candidates.append(dict(source='ISTC', level='edition', mei_id='', istc_id=identifier,
                    url=url, source_field=path, note='Unclassified edition-level external link',
                    source_url='https://data.cerl.org/istc/' + identifier))
        except Exception as error:
            consecutive_istc_errors += 1
            status['digital_link_errors'].append({'source': 'ISTC', 'id': identifier, 'error_type': type(error).__name__})
            # Stop repeated blocked requests. Do not silently present a complete harvest.
            if consecutive_istc_errors >= 3:
                break
    api.atomic_write_json(OUT / 'istc-records.json', istc_records)
    api.atomic_write_json(OUT / 'harvest-status.json', status)
    gw_to_istc = defaultdict(set)
    for row in core_rows:
        gw_to_istc[row['gw_url']].update(split_istc_ids(row['istc_id']))
    for record in combined['records']:
        for ref in record.get('hostItem', {}).get('references', []):
            match = re.match(r'^GW\s+(M?\d+(?:N)?)\b', ref)
            if match:
                gid = match[1] if match[1].startswith('M') else 'GW' + match[1].zfill(5)
                gw_to_istc['https://gesamtkatalogderwiegendrucke.de/docs/' + gid + '.htm'].add(record.get('hostItemId', ''))
    deadline = time.monotonic() + args.gw_minutes * 60
    pending = []
    completed_gw = 0
    for n, (url, ids) in enumerate(sorted(gw_to_istc.items()), 1):
        cache_path = CACHE / ('gw-' + hashlib.sha256(url.encode()).hexdigest() + '.json')
        if not cache_path.exists() and time.monotonic() >= deadline:
            pending.append(url)
            continue
        print(f'GW links {n}/{len(gw_to_istc)}', flush=True)
        try:
            result = gw_links(url, limiter)
            completed_gw += 1
            for link in result['links']:
                candidates.append(dict(source='GW', level='edition', mei_id='', istc_id=' | '.join(sorted(ids)),
                    url=link['url'], source_field='Digitalisat', note=link['label'], source_url=url))
        except Exception as error:
            status['digital_link_errors'].append({'source': 'GW', 'url': url, 'error_type': type(error).__name__})
        if n % 25 == 0:
            api.atomic_write_json(OUT / 'digital-link-candidates.json', candidates)
            status.update(gw_completed=completed_gw, gw_expected=len(gw_to_istc))
            api.atomic_write_json(OUT / 'harvest-status.json', status)
    api.atomic_write_json(OUT / 'digital-link-candidates.json', candidates)
    status.update(complete=not status['digital_link_errors'] and not pending and not status['istc_unresolved_identifiers'], mei_complete=True,
        gw_completed=completed_gw, gw_expected=len(gw_to_istc), gw_pending=pending,
        needs_resume=bool(pending),
        finished_at=api.now_iso(), editions=len(groups), direct_mei_records=len(direct),
        group_editions={g: sum(g in v for v in groups.values()) for g in ['core','liturgy','devotional']},
        digital_link_candidates=len(candidates), istc_records_retrieved=len(istc_records),
        istc_records_expected=len(identifiers))
    api.atomic_write_json(OUT / 'harvest-status.json', status)
    print(json.dumps({**status, 'gw_pending': len(pending)}, ensure_ascii=False, indent=2))
    if pending:
        print('Planned checkpoint reached. Run this workflow again to continue remaining GW pages; cached requests are reused.')
    if status['digital_link_errors']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
