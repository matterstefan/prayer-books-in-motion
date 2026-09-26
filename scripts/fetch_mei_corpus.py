#!/usr/bin/env python3
"""Retrieve the complete agreed corpus, with durable per-query checkpoints.

Uses the tested pilot pagination and relationship logic. The website's pilot
tables are never overwritten. Only a complete harvest produces mei-corpus.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import fetch_mei_pilot as api
from transform_mei import transform

ROOT = Path(__file__).resolve().parents[1]


def read_plan():
    with (ROOT / 'data/derived/gw-istc-links.csv').open(encoding='utf-8-sig', newline='') as f:
        links = list(csv.DictReader(f))
    with (ROOT / 'data/derived/prayer-book-corpus.csv').open(encoding='utf-8-sig', newline='') as f:
        editions = list(csv.DictReader(f))
    identifiers = sorted({row['istc_id'].strip() for row in links})
    if not identifiers or any(not re.fullmatch(r'i[a-z]\d{8}(?:,\d+)?', i) for i in identifiers):
        raise ValueError('Invalid or empty ISTC selection')
    linked_gw = {row['gw_id'] for row in links}
    return identifiers, {
        'gw_records': len(editions),
        'gw_istc_links': len(links),
        'istc_queries': len(identifiers),
        'istc_identifiers_with_suffix': [i for i in identifiers if ',' in i],
        'gw_without_istc': [row['gw_id'] for row in editions if row['gw_id'] not in linked_gw],
        'selection_sha256': hashlib.sha256('\n'.join(identifiers).encode()).hexdigest(),
    }


def validate_cached(result, identifier):
    rows = result.get('rows')
    if result.get('query') != identifier or not isinstance(rows, list):
        raise ValueError(f'Invalid query cache: {identifier}')
    ids = [str(r.get('id', '')) for r in rows]
    if '' in ids or len(ids) != len(set(ids)) or len(ids) != result.get('reported_hits'):
        raise ValueError(f'Incomplete query cache: {identifier}')
    if not result.get('retrieved_at') or result.get('endpoint') != api.API_ENDPOINT:
        raise ValueError(f'Missing source metadata: {identifier}')


def seed_from_pilot(cache, identifiers):
    """Reuse only pilot queries whose complete raw result is recoverable.

    Search hits discarded as unrelated are absent from the combined snapshot;
    those queries must be fetched again instead of claiming a complete cache.
    """
    path = ROOT / 'data/sample/mei-pilot.json'
    if not path.exists():
        return
    pilot = json.loads(path.read_text(encoding='utf-8'))
    for identifier, meta in pilot['metadata'].get('query_results', {}).items():
        target = cache / f'{identifier}.json'
        if identifier not in identifiers or target.exists():
            continue
        rows = [r for r in pilot['records'] if api.relationship_rows(r, identifier)]
        if len(rows) != meta['api_hits_reported'] or meta.get('unrelated_records_discarded', 0):
            continue
        result = {'query': identifier, 'retrieved_at': meta['retrieved_at'],
                  'endpoint': api.API_ENDPOINT, 'page_size': 100,
                  'reported_hits': len(rows), 'rows': rows,
                  'seed_source': 'data/sample/mei-pilot.json'}
        validate_cached(result, identifier)
        api.atomic_write_json(target, result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Inspect selection without fetching or writing')
    parser.add_argument('--cache-only', action='store_true', help='Compile available checkpoints without network requests')
    parser.add_argument('--cache-dir', type=Path, default=ROOT / 'data/cache/mei-corpus')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/expanded')
    parser.add_argument('--delay', type=float, default=2.0)
    parser.add_argument('--max-new-queries', type=int, default=0, help='0 means unlimited')
    parser.add_argument('--seed-pilot', action='store_true', help='Reuse complete pilot queries, retaining their original dates')
    args = parser.parse_args()
    if args.delay < 1 or args.max_new_queries < 0:
        parser.error('Use a delay of at least one second and a non-negative query limit')
    identifiers, plan = read_plan()
    print(json.dumps(plan, ensure_ascii=False, indent=2), flush=True)
    if args.check:
        return 0
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.seed_pilot:
        seed_from_pilot(args.cache_dir, set(identifiers))
    limiter = api.RateLimiter(args.delay)
    results, completed, errors = [], [], []
    fetched = 0
    consecutive_errors = 0
    interrupted = False
    try:
        for position, identifier in enumerate(identifiers, 1):
            path = args.cache_dir / f'{identifier}.json'
            from_cache = path.exists()
            if not from_cache and (args.cache_only or (args.max_new_queries and fetched >= args.max_new_queries)):
                continue
            print(f'[{position}/{len(identifiers)}] {identifier}: ' + ('cache' if from_cache else 'fetch'), flush=True)
            try:
                if from_cache:
                    result = json.loads(path.read_text(encoding='utf-8'))
                else:
                    fetched += 1
                    result = api.fetch_complete_query(identifier, limiter)
                validate_cached(result, identifier)
                if not from_cache:
                    api.atomic_write_json(path, result)
                results.append((result, from_cache))
                completed.append(identifier)
                consecutive_errors = 0
            except Exception as error:
                errors.append({'istc_id': identifier, 'error': str(error)})
                print(f'ERROR {identifier}: {error}', file=sys.stderr, flush=True)
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    print('Stopping after three consecutive errors; checkpoints retained.', flush=True)
                    break
    except KeyboardInterrupt:
        interrupted = True
        print('Interrupted; compiling completed checkpoints.', flush=True)

    missing = sorted(set(identifiers) - set(completed))
    report = {**plan, 'compiled_at': api.now_iso(), 'complete': False,
              'retrieval_complete': not missing,
              'completed_queries': len(completed), 'pending_queries': missing,
              'errors': errors, 'interrupted': interrupted,
              'new_queries_attempted': fetched}
    # Save the audit first, including when combining detects conflicting versions.
    report_path = args.output_dir / 'harvest-status.json'
    api.atomic_write_json(report_path, report)
    try:
        combined = api.combine_queries(completed, results)
    except Exception as error:
        report['complete'] = False
        report['combine_error'] = str(error)
        api.atomic_write_json(report_path, report)
        raise
    combined['metadata'].update({
        'purpose': 'Complete agreed prayer-book corpus retrieval',
        'selection_file': 'data/derived/gw-istc-links.csv',
        'complete': not missing,
        'corpus_requested_istc_count': len(identifiers),
        'pending_istc_ids': missing,
        'selection_sha256': plan['selection_sha256'],
    })
    name = 'mei-corpus.json' if not missing else 'mei-corpus-partial.json'
    snapshot = args.output_dir / name
    api.atomic_write_json(snapshot, combined)
    tables = args.output_dir / ('tables' if not missing else 'partial-tables')
    counts = transform(snapshot, tables)
    relationships = combined['relationships']
    direct_ids = {r['mei_id'] for r in relationships if r['relation_type'] == 'direct'}
    report.update(counts)
    report.update({
        'complete': not missing,
        'direct_copy_records': len(direct_ids),
        'indirect_only_records': len(combined['records']) - len(direct_ids),
        'direct_relationships': sum(r['relation_type'] == 'direct' for r in relationships),
        'bound_with_relationships': sum(r['relation_type'] == 'bound_with' for r in relationships),
        'queries_with_relationships': sum(m['related_records_retained'] > 0 for m in combined['metadata']['query_results'].values()),
        'queries_without_relationships': sum(m['related_records_retained'] == 0 for m in combined['metadata']['query_results'].values()),
        'snapshot': name,
    })
    api.atomic_write_json(report_path, report)
    print(json.dumps({k: v for k, v in report.items() if k not in {'pending_queries', 'gw_without_istc'}}, indent=2))
    return 0 if not missing else 2


if __name__ == '__main__':
    sys.exit(main())
