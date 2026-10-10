#!/usr/bin/env python3
"""Apply reviewed locality matches to staged collection data, never live map inputs.

Inputs retain original catalogue labels. Coordinate choices have source references
and stable station IDs. Unknown/area-only locations do not become route vertices.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/collections/place-review'

def main():
    with (OUT / 'tables/mei-itinerary-stations-reviewed.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    by_id = {r['station_id']: r for r in rows}
    assert len(by_id) == len(rows)
    matches = json.loads((ROOT / 'data/authority/collection-locality-matches-20261010.json').read_text())['matches']
    decisions = json.loads((ROOT / 'data/authority/stefan-place-review-20261010.json').read_text())['decisions']
    for r in rows:
        r['geolocation_certainty'] = ''
        r['review_note'] = ''
    # Reuse existing display point of the SAME GeoNames locality to avoid duplicate city nodes.
    existing = defaultdict(Counter)
    for r in rows:
        if r['map_point_policy'] == 'locality' and r['display_latitude'] and r['place_authority_id']:
            existing[r['place_authority_id']][(r['display_latitude'], r['display_longitude'])] += 1
    touched = set()
    for m in matches:
        p = m['point']
        for sid in m['station_ids']:
            assert sid not in touched, f'Duplicate decision: {sid}'
            touched.add(sid)
            r = by_id[sid]
            label = r['source_location_label'] or r['location_label'] or '(ohne Ortsangabe)'
            assert ' '.join(label.casefold().split()) == ' '.join(m['source_label'].casefold().split()), f'Source changed: {sid}'
            assert not r['latitude'] and not r['longitude'], f'Existing coordinates must not be replaced: {sid}'
            r.update(preferred_placename=p['name'], place_name=p['name'], latitude=p['lat'], longitude=p['lon'],
                     resolved_country_code=p['country'], spatial_precision='locality',
                     place_authority='GeoNames' if p['gid'] else '', place_authority_id=p['gid'],
                     place_authority_url='https://www.geonames.org/' + p['gid'] if p['gid'] else '',
                     location_resolution_status='coordinates_resolved', location_resolution_method=m['method'],
                     location_resolution_note=m['note'], resolution_source_url=m['source'],
                     display_latitude=p['lat'], display_longitude=p['lon'], map_point_policy='locality',
                     geolocation_certainty='probable' if m['uncertain'] else 'identified')
            if existing.get(p['gid']):
                (r['display_latitude'], r['display_longitude']), _ = existing[p['gid']].most_common(1)[0]
    for d in decisions:
        for sid in d['station_ids'].split(' | '):
            r = by_id[sid]
            r['review_note'] = d['note']
            r['geolocation_certainty'] = d['status']
            if d['status'] in {'unresolved', 'country_only'}:
                assert not r['latitude']
                r['map_point_policy'] = 'no_locality_point'
            if d['status'] == 'country_only':
                r['resolved_country_code'] = 'UA'
                r['spatial_precision'] = 'country'
    areas = {'Central Italy?', 'Italy?', 'Southern Italy', 'e-fr', 'England', 'Europa', 'Germany?',
             'IJssel region', 'Inghilterra', 'Italia', 'Lombardy [?]', 'Netherlands', 'Northern Italy', 'Wiltshire'}
    with (OUT / 'Offene_Orte.csv').open(encoding='utf-8-sig', newline='') as f:
        original_groups = list(csv.DictReader(f, delimiter=';'))
    remaining = []
    for g in original_groups:
        ids = g['Station_IDs'].split(' | ')
        if all(sid in touched for sid in ids):
            continue
        assert not any(sid in touched for sid in ids), 'Partially matched group must be regrouped'
        label = g['Ortsangabe_Quelle']
        if label in areas:
            category = 'Nur Gebiet, kein Ortsmarker'
        elif label in {'(ohne Ortsangabe)', ' ', 'Anonymous', 'Anonymous annotator, Italy 1497 - ', 'ChL 945B', 'dispersed'}:
            category = 'Keine verwertbare Ortsangabe'
        elif label in {'Rouen or Paris', 'Venice or Milan?', 'Soncino and Casal Maggiore', 'Southern Germany (Constance?)'}:
            category = 'Mehrdeutige oder mehrteilige Druckangabe'
        else:
            category = 'Ortsidentifikation offen'
        for sid in ids:
            r = by_id[sid]
            if not r['latitude']:
                r['map_point_policy'] = 'no_locality_point'
                if label in areas:
                    r['spatial_precision'] = 'area'
        remaining.append({**g, 'Status': category})
    with (OUT / 'Verbleibende_Ortsangaben.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(original_groups[0]) + ['Status'], delimiter=';')
        w.writeheader(); w.writerows(remaining)
    destination = OUT / 'tables/mei-itinerary-stations-final.csv'
    with destination.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary = dict(stations=len(rows), copies=len({r['mei_id'] for r in rows}),
                   newly_located_stations=len(touched),
                   stations_with_coordinates=sum(bool(r['latitude'] and r['longitude']) for r in rows),
                   stations_without_coordinates=sum(not r['latitude'] for r in rows),
                   locality_route_points=sum(r['map_point_policy']=='locality' and bool(r['display_latitude']) for r in rows),
                   remaining_groups=len(remaining),
                   remaining_group_categories=dict(Counter(g['Status'] for g in remaining)),
                   live_website_changed=False)
    (OUT / 'final-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
