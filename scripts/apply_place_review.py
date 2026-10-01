"""Apply the dated human review without changing catalogue source files."""
import json

COLUMNS = ['source_location_label', 'review_id', 'spatial_precision', 'display_uncertainty', 'date_warning']


def apply_review(rows, root):
    review = json.loads((root/'data/authority/stefan-place-review.json').read_text())
    points = json.loads((root/'data/authority/reviewed-city-points.json').read_text())
    decisions = {sid:d for d in review['decisions'] for sid in d['station_ids']}
    special = {'00201166':('Wien','1905'), '00201167':('Rom','1681'),
               '00201576':('Pforzheim','2024'), '02125950':('London','2018')}
    for row in rows:
        row.update({key:'' for key in COLUMNS})
        row['source_location_label'] = row['location_label']
        row['spatial_precision'] = 'locality' if row['latitude'] else ''
        if row['time_start'] and row['time_end'] and int(row['time_start']) > int(row['time_end']):
            row['date_warning'] = 'Widersprüchliche Datierung in der Quelle; nicht zur zeitlichen Verortung verwendet.'
        if row['place_name']=='Bologna' and row['place_authority_id']=='3181927':
            point=points['Bologna']
            row.update(latitude=point['lat'],longitude=point['lon'],place_authority_id='3181928',
                       place_authority_url='https://www.geonames.org/3181928',
                       location_resolution_method='city_not_province',resolution_source_url=point['source'],
                       location_resolution_note='Stadtpunkt Bologna statt des zuvor verwendeten Provinzpunkts; ursprüngliche Koordinaten bleiben gespeichert.')
        d = decisions.get(row['station_id'])
        if not d or not d['chosen_name']: continue
        expected = '' if d['label']=='(ohne Ortsbezeichnung)' else d['label'].strip()
        if row['source_location_label'].strip() != expected:
            raise ValueError('Source label changed; review required before reapplying '+d['review_id']+' to '+row['station_id'])
        row['review_id'] = d['review_id']
        if row['station_type']=='current_holding' and row['mei_id'] in special:
            name, year = special[row['mei_id']]
            previous = [s for s in rows if s['mei_id']==row['mei_id'] and s['station_type']=='provenance_place' and s['latitude']]
            previous.sort(key=lambda s:int(s['source_order']))
            last = previous[-1]
            for k in ['latitude','longitude','place_authority','place_authority_id','place_authority_url','resolved_country_code']:
                row[k]=last[k]
            row.update(station_type='last_known',station_role='last_known_location', location_label=name,
                       place_name=name,preferred_placename=name,time_start=year,time_end=year,observation_date='',
                       location_resolution_status='coordinates_resolved',location_resolution_method='last_known_source_event',
                       location_resolution_note='Letzter bekannter Nachweis; heutiger Aufenthaltsort unbekannt.',
                       resolution_source_url=row['source_url'],spatial_precision='locality',display_uncertainty='Heutiger Aufenthaltsort unbekannt')
            continue
        p = points.get(d['chosen_name'])
        if not p: raise ValueError('Reviewed place lacks coordinates: '+d['chosen_name'])
        row.update(place_name=p['name'],preferred_placename=p['name'],latitude=p['lat'],longitude=p['lon'],
                   place_authority='GeoNames' if p['gid'] else '',place_authority_id=p['gid'],
                   place_authority_url='https://www.geonames.org/'+p['gid'] if p['gid'] else '',
                   resolved_country_code=p['country'],location_resolution_status='coordinates_resolved',
                   location_resolution_method='human_review_2026_10_01',resolution_source_url=p['source'],
                   location_resolution_note='Ortszuweisung nach Prüfung durch Stefan Matter (01.10.2026); Kartenpunkt auf Ortsebene.',spatial_precision='locality')
        if row['station_type']!='current_holding': row['location_label']=p['name']
        if d['chosen_name']=='Italien':
            row.update(spatial_precision='country',display_uncertainty='Nur Land bekannt',location_resolution_note='Repräsentativer Länderpunkt aus GeoNames; kein genauer Aufenthaltsort und kein berechneter Flächenschwerpunkt.')
        elif d['label'] in ['Montserrat','Paris oder Rouen','Paris(?)','Venedig(?)','Schwarzau am Steinfeld (Vienna)?']:
            row['display_uncertainty']='Unsichere Ortszuweisung; für die Karte gewählt'
            row['location_resolution_note'] += ' Quellenangabe: '+d['label']+'. Alternative bzw. Unsicherheit bleibt bestehen.'
        elif d['chosen_name']=='Kiel':
            row['display_uncertainty']='Ortszuweisung über Besitzerangabe'
            row['location_resolution_note']='Kiel nach manueller Zuordnung zum Besitzer (CERL owners/2820); kein eigenständiger Aufenthaltsbeleg.'
        if d['label']=='Montserrat': row['location_resolution_note']+=' GW: Montserrat, 1499; ISTC: Barcelona, 1494.'
    return rows
