#!/usr/bin/env python3
"""Build full-corpus stations and resolve places from documented source evidence.

Standard library only. Does not change the pilot or website data.
Run after the complete harvest: python3 scripts/resolve_corpus_locations.py
"""
import csv
import json
import math
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path
import build_itinerary_stations as stations
import resolve_station_locations as pilot
from apply_place_review import apply_review, COLUMNS as REVIEW_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/expanded'
COUNTRIES = dict(zip(
    ['United Kingdom','Germany','Italy','France','Netherlands','Austria','Switzerland','United States','Belgium','Poland','Spain','Czech Republic','Czechia','Sweden','Lithuania','Latvia','Hungary','Slovenia','Russia','Malta','Greece','New Zealand','Vatican City','Denmark','Portugal'],
    ['GB','DE','IT','FR','NL','AT','CH','US','BE','PL','ES','CZ','CZ','SE','LT','LV','HU','SI','RU','MT','GR','NZ','VA','DK','PT']))


COUNTRIES['The Netherlands'] = 'NL'


def norm(value):
    return ' '.join(unicodedata.normalize('NFC', value or '').casefold().split())


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def valid_point(lat, lon):
    try:
        return math.isfinite(float(lat)) and math.isfinite(float(lon)) and -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
    except (ValueError, TypeError):
        return False


def main():
    snapshot = json.loads((OUT / 'mei-corpus.json').read_text())
    if not snapshot['metadata'].get('complete'):
        raise ValueError('A complete corpus snapshot is required')
    records = {r['id']: r for r in snapshot['records']}
    corpus = read(ROOT / 'data/derived/prayer-book-corpus.csv')
    grouped = defaultdict(list)
    for row in corpus:
        for ident in row['istc_id'].split(';'):
            if ident.strip(): grouped[ident.strip()].append(row)
    selection = []
    source_urls = {}
    for ident, rows in grouped.items():
        # Never collapse differing catalogue attributions into one precise date.
        places = sorted({r['print_place_gw'] for r in rows})
        dates = {(r['year_from'], r['year_to']) for r in rows}
        start, end = next(iter(dates)) if len(dates) == 1 else ('', '')
        selection.append(dict(istc_id=ident, gw_ids=' | '.join(r['gw_id'] for r in rows),
            print_places_gw=' | '.join(places), year_from=start, year_to=end,
            corpus_file=' | '.join(sorted({r['corpus_file'] for r in rows}))))
        source_urls[ident] = ' | '.join(r['gw_url'] for r in rows)
    tables = OUT / 'tables'
    copies, provenance, places, links = [read(tables / name) for name in
        ['mei-copies.csv','mei-provenance.csv','mei-places.csv','mei-record-links.csv']]
    raw = stations.build_rows(selection, copies, provenance, places, links)
    direct = {r['mei_id'] for r in links if r['relation_type'] == 'direct'}
    stations.validate_rows(raw, {r['place_occurrence_id'] for r in places if r['mei_id'] in direct})
    for row in raw:
        if row['station_type'] == 'print_place':
            row['source_url'] = source_urls[row['requested_istc_id']]
            row['source_snapshot'] = 'data/derived/prayer-book-corpus.csv'
    stations.write_csv(tables / 'mei-itinerary-stations.csv', raw)

    mappings = read(ROOT / 'data/authority/place-authorities.csv')
    # Gazetteer entries are source-derived, not new catalogue descriptions.
    by_id = defaultdict(list)
    by_name = defaultdict(set)
    def add(gid, name, country, lat, lon, aliases, url):
        if not gid or not valid_point(lat, lon): return
        gid = str(gid)
        point = dict(gid=gid, name=name, country=country, lat=str(lat), lon=str(lon), source=url)
        by_id[gid].append(point)
        for label in [name, *aliases]:
            if label: by_name[norm(label)].add(gid)
    for record in records.values():
        for block in record.get('provenance', []):
            for p in block.get('place', []):
                xy = str(p.get('location', '')).split(',')
                if len(xy) == 2:
                    country = p.get('country','')
                    country = COUNTRIES.get(country, country if len(country)==2 else '')
                    add(p.get('geonamesId'), p.get('preferredPlacename') or p.get('name',''),
                        country, *xy, [p.get('name',''), *p.get('variantPlacenames',[])],
                        'https://data.cerl.org/mei/' + record['id'])
    # Previously reviewed city points take precedence for the same authority ID.
    reviewed = {}
    for m in mappings:
        if m['resolution_status'] == 'resolved':
            gid = m['place_authority_id']
            add(gid,m['resolved_name'],m['country_code'],m['latitude'],m['longitude'],
                [m['source_key']] if m['station_type'] != 'current_holding' else [m['source_label'].split(',')[0].strip()],m['source_record_url'])
            reviewed[gid] = by_id[gid][-1]
    additions = json.loads((ROOT / 'data/authority/corpus-city-points.json').read_text())
    for point in additions:
        add(point['gid'],point['name'],point['country'],point['lat'],point['lon'],point['aliases'],point['source'])
        reviewed[point['gid']] = by_id[point['gid']][-1]
    gazetteer = {}
    for gid, pts in by_id.items():
        if gid in reviewed:
            gazetteer[gid] = reviewed[gid]; continue
        # Conflicting coordinates for one identifier remain unresolved.
        if max(float(p['lat']) for p in pts)-min(float(p['lat']) for p in pts) > .05 or max(float(p['lon']) for p in pts)-min(float(p['lon']) for p in pts) > .05:
            continue
        gazetteer[gid] = pts[0]

    extra = ['source_place_name','source_latitude','source_longitude',*pilot.ADDED_COLUMNS,'resolution_source_url']
    result = []
    for original in raw:
        row = dict(original)
        row.update({k:'' for k in extra})
        row.update(source_place_name=original['place_name'],source_latitude=original['latitude'],source_longitude=original['longitude'])
        key = pilot.station_key(row)
        candidates = [m for m in mappings if (m['station_type'],m['source_key']) == key
            and (not pilot.mapping_context(m) or row.get(m['match_context_field']) == m['match_context_key'])
            and (not (row['latitude'] and row['longitude']) or pilot.applies_to_existing_coordinates(m))]
        specific = [m for m in candidates if pilot.mapping_context(m)]
        chosen = specific or candidates
        if len(chosen)>1: raise ValueError('Ambiguous pilot crosswalk: '+row['station_id'])
        if chosen:
            m=chosen[0]
            row.update(location_mapping_id=m['mapping_id'],resolved_country_code=m['country_code'],
                place_wikidata_id=m['place_wikidata_id'],institution_wikidata_id=m['institution_wikidata_id'],
                location_resolution_method=m['resolution_method'],location_resolution_note=m['resolution_note'],
                resolution_source_url=m['source_record_url'])
            if m['resolution_status']=='resolved':
                row.update(place_name=m['resolved_name'],preferred_placename=m['resolved_name'],place_authority=m['place_authority'],
                    place_authority_id=m['place_authority_id'],place_authority_url=m['place_authority_url'],
                    latitude=m['latitude'],longitude=m['longitude'],location_resolution_status='coordinates_resolved')
            else:
                row.update(latitude='',longitude='',location_resolution_status=m['resolution_status'])
            result.append(row); continue
        if valid_point(row['latitude'],row['longitude']):
            row['location_resolution_method']='coordinates_supplied_by_mei'
            row['resolution_source_url']=row['source_url']
            result.append(row);continue
        point = None
        if row['station_type']=='provenance_place' and row['place_authority_id']:
            point=gazetteer.get(row['place_authority_id'])
            method='same_geonames_id_in_source'
        else:
            country = row['country']
            name = row['place_name']
            if row['station_type']=='current_holding':
                name=row['institution_name'].split(',')[0].strip()
            elif row['station_type']=='print_place':
                country=records[row['mei_id']].get('hostItem',{}).get('imprint_country_code','')
            ids=by_name.get(norm(name),set())
            points=[gazetteer[g] for g in ids if g in gazetteer and country and gazetteer[g]['country']==country]
            preferred = [p for p in points if p['gid'] in reviewed]
            if len(preferred) == 1:
                points = preferred
            # Ambiguous locality strings require edition-specific review.
            if len(points)==1 and name not in {'Vienne','Kirchheim','Hasselt'} and not any(x in name for x in ['?',' oder ',' | ']):
                point=points[0]
            method='source_name_and_country_match'
        if point:
            row.update(place_name=point['name'],preferred_placename=point['name'],place_authority='GeoNames',
                place_authority_id=point['gid'],place_authority_url='https://www.geonames.org/'+point['gid'],
                latitude=point['lat'],longitude=point['lon'],resolved_country_code=point['country'],
                location_resolution_status='coordinates_resolved',location_resolution_method=method,
                resolution_source_url=point['source'],location_resolution_note='Locality-level point reused from source data; no building location or arrival date inferred.')
        else:
            label=(row['place_name'] or row['institution_name']).strip()
            status='needs_review'
            if label in {'Italien','Italy'}:status='country_only'
            if label in {'Buchbinderwerkstätten (nicht lokalisiert)','Einbände (ohne Nachweis)','Historical Copy','Trade Copy'}:status='non_geographic'
            row.update(latitude='',longitude='',location_resolution_status=status,location_resolution_method='unresolved')
        result.append(row)
    result = apply_review(result, ROOT)
    columns=list(stations.STATION_COLUMNS)+extra+REVIEW_COLUMNS
    write(tables/'mei-itinerary-stations-resolved.csv',result,columns)
    unresolved=[r for r in result if not r['latitude'] or not r['longitude']]
    write(tables/'location-review.csv',unresolved,columns)
    write(tables/'location-decisions.csv',[r for r in result if r['location_resolution_method']!='coordinates_supplied_by_mei'],columns)
    summary={'direct_copies':len(direct),'stations':len(result),'with_coordinates':len(result)-len(unresolved),
        'by_type':{t:dict(total=sum(r['station_type']==t for r in result),with_coordinates=sum(r['station_type']==t and bool(r['latitude'] and r['longitude']) for r in result)) for t in ['print_place','provenance_place','current_holding','last_known']},
        'unresolved_statuses':dict(Counter(r['location_resolution_status'] for r in unresolved)),
        'complete_routes_with_endpoints':sum(any(r['station_type']=='current_holding' for r in result if r['mei_id']==mid) and all(r['latitude'] and r['longitude'] for r in result if r['mei_id']==mid and r['station_type'] in ['print_place','current_holding']) for mid in direct)}
    (OUT/'location-status.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
