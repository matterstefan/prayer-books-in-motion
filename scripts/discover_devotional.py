#!/usr/bin/env python3
"""Read-only discovery of MEI devotional editions outside the existing GW corpus."""
import csv
import io
import os
from pathlib import Path

from build_corpus import SOURCE_FILES, read_source, split_istc_ids
from fetch_mei_pilot import RateLimiter, fetch_complete_query, atomic_write_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'discovery'
QUERY = 'data.hostItem.subject:"literature-devotional" OR data.hostItem.keywords:"literature-devotional"'


def values(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def new_editions(records, existing):
    editions = {}
    rejected = 0
    for record in records:
        host = record.get('hostItem', {})
        tags = values(host.get('subject')) + values(host.get('keywords'))
        if 'literature-devotional' not in [str(v).strip().lower() for v in tags]:
            rejected += 1
            continue
        identifier = record.get('hostItemId')
        if not identifier:
            raise ValueError('Matching record has no hostItemId; cannot compare editions')
        if identifier in existing:
            continue
        edition = editions.setdefault(identifier, {'copies': set(), 'fields': {}})
        edition['copies'].add(str(record['id']))
        for field in ('title', 'author', 'imprint', 'language', 'subject', 'keywords', 'references'):
            edition['fields'].setdefault(field, set()).update(str(v) for v in values(host.get(field)) if v)
    return editions, rejected


def safe_write(path, text):
    secret = os.environ.get('CERL_USER_AGENT', '').strip()
    if secret and secret in text:
        raise ValueError('Access identifier detected; refusing to write')
    path.write_text(text, encoding='utf-8-sig' if path.suffix == '.csv' else 'utf-8')


def main():
    existing = {i for filename in SOURCE_FILES for row in read_source(filename)
                for i in split_istc_ids(row['istc_id'])}
    print('Searching MEI subject and keyword fields; existing selection:', len(existing), 'ISTC identifiers', flush=True)
    result = fetch_complete_query(QUERY, RateLimiter(1.5))
    editions, rejected = new_editions(result['rows'], existing)
    OUT.mkdir(parents=True, exist_ok=True)
    atomic_write_json(OUT / 'devotional-query.json', result)
    rows = []
    for identifier, edition in editions.items():
        row = {'istc_id': identifier}
        row.update({k: ' | '.join(sorted(v)) for k, v in edition['fields'].items()})
        row.update(mei_copies=len(edition['copies']), mei_ids=' | '.join(sorted(edition['copies'])),
                   istc_url='https://data.cerl.org/istc/' + identifier)
        rows.append(row)
    rows.sort(key=lambda r: (r['title'].casefold(), r['author'].casefold(), r['istc_id']))
    columns = ['istc_id', 'title', 'author', 'imprint', 'language', 'subject', 'keywords', 'references', 'mei_copies', 'mei_ids', 'istc_url']
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    safe_write(OUT / 'additional-devotional-editions.csv', stream.getvalue())
    lines = ['# Additional devotional editions in MEI', '',
             'Retrieved: ' + result['retrieved_at'], '',
             f'{len(rows)} additional editions, represented by {sum(r["mei_copies"] for r in rows)} MEI records.', '',
             'Selection: literature-devotional in subject OR keywords. All ISTC identifiers in both existing GW seed tables are excluded. Titles retain MEI bibliographic wording; no new work titles are assigned. Counts refer to directly linked MEI records, not all surviving copies. Bound-with references are not counted as additional copies. Bibliographic variants within an edition are separated by |.', '',
             f'Search hits: {result["reported_hits"]}; hits without an exact matching host-item tag: {rejected}.', '']
    for n, row in enumerate(rows, 1):
        lines.extend([f'## {n}. ' + row['title'], '',
                      f'- Author: {row["author"] or "—"}',
                      f'- Imprint: {row["imprint"] or "—"}',
                      f'- Language: {row["language"] or "—"}',
                      f'- Subject: {row["subject"]}; keywords: {row["keywords"]}',
                      f'- ISTC: [{row["istc_id"]}]({row["istc_url"]}); MEI records: {row["mei_copies"]}', ''])
    safe_write(OUT / 'additional-devotional-editions.md', '\n'.join(lines))
    print(f'Finished: {len(rows)} additional editions. Existing corpus and website unchanged.')


if __name__ == '__main__':
    main()
