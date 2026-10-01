# Ortsauflösung des vollständigen Korpus

Stand: 1. Oktober 2026. Quellenabruf: 23.–30. September 2026.

## Ergebnis

484 direkt zugehörige MEI-Exemplare erhalten je eine Druckort- und eine heutige
Aufbewahrungsstation. Hinzu kommen 858 Provenienz-Ortsangaben dieser Exemplare.
Von den insgesamt 1’826 Stationen haben 1’726 Koordinaten:

| Stationstyp | Gesamt | Mit Koordinaten |
|---|---:|---:|
| Druckort | 484 | 460 |
| Provenienzort | 858 | 836 |
| Heutiger Aufbewahrungsort | 484 | 430 |

100 Stationszeilen (60 unterschiedliche Typ/Ort- bzw. Institutionsschlüssel)
bleiben offen oder bewusst ohne Kartenpunkt. 411 Exemplare haben Koordinaten
für beide Endstationen. Das bedeutet keine lückenlose Überlieferung ihres Weges.
Die 43 nur über Beibände verbundenen Datensätze bleiben im Ausgangssnapshot und
den vier MEI-Tabellen erhalten; ihre Provenienzen werden nicht auf andere
Exemplare übertragen. Daher unterscheiden sich die 858 hier berücksichtigten
Provenienzorte von den 918 Ortsangaben des gesamten abgerufenen Bestands.

## Dateien

- `data/expanded/mei-corpus.json`: vollständiger abgerufener Quellenbestand.
- `data/expanded/tables/mei-itinerary-stations.csv`: quellennahe Stationen.
- `data/expanded/tables/mei-itinerary-stations-resolved.csv`: Stationsdaten mit Ortsauflösung.
- `data/expanded/tables/location-review.csv`: alle 100 Zeilen ohne Kartenpunkt.
- `data/expanded/tables/location-decisions.csv`: Zuordnungen und offene Fälle; unverändert übernommene MEI-Koordinaten sind hier nicht wiederholt.
- `data/expanded/location-status.json`: maschinenlesbare Ergebniszahlen.
- `data/authority/corpus-city-points.json`: ergänzende, einzeln referenzierte Stadtpunkte.
- `scripts/resolve_corpus_locations.py`: reproduzierbare Verarbeitung.

## Verfahren und Grenzen

1. Die bereits dokumentierten Pilot-Zuordnungen werden wiederverwendet,
   einschliesslich ihrer Kontextbedingungen und bewusst ungelösten Fälle.
2. MEI-Koordinaten werden grundsätzlich übernommen. Ihre Übernahme ist keine
   unabhängige Prüfung jeder einzelnen Katalogangabe.
3. Fehlende Koordinaten können über dieselbe GeoNames-ID aus anderen
   Quellenangaben ergänzt werden. Widersprechende Punkte werden nicht gemittelt.
4. Für neue Druckorte und Bibliotheksorte werden genaue Namensübereinstimmungen
   bzw. vorhandene Namensvarianten zusammen mit dem Land verwendet. Mehrere
   Kandidaten bleiben offen, sofern kein dokumentierter Stadtpunkt vorliegt.
   Das ist eine nachvollziehbare technische Zuordnung, keine vollständige
   historische Überprüfung. Es werden keine unscharfen Namensähnlichkeiten benutzt.
5. Bibliotheken erhalten Stadtpunkte, keine vermeintlich exakten Gebäudepunkte.
   Bei US-Ortsangaben werden Bundesstaatkürzel nicht pauschal entfernt.
6. Länder, Platzhalter und ungeklärte Alternativen bleiben ohne Koordinaten.
   Insbesondere bleibt GW 13441 (Montserrat/Barcelona) ungelöst.
7. Originalnamen und ursprüngliche Koordinaten bleiben in separaten Spalten
   erhalten. Jede ergänzte Zuordnung nennt Methode und Quellenlink.
8. Unterschiedliche GW-Datierungen für dieselbe ISTC-Ausgabe werden nicht
   automatisch zu einer einzigen präzisen Datierung verschmolzen.

Die offenen Zeilen enthalten sowohl echte Unklarheiten als auch unkomplizierte,
aber noch nicht überprüfte Orte. Sie sind keine Fehlerliste und kein Ausschluss
von Exemplaren aus dem Korpus. Die Kartenoberfläche muss fehlende Stationen
sichtbar machen; diese Daten allein verändern die bestehende Webseite noch nicht.

Die zusätzlichen Stadtpunkte sind bei GeoNames dokumentiert, beispielsweise
Ulm (https://www.geonames.org/2820256/), Nürnberg
(https://www.geonames.org/2861650/), Bologna
(https://www.geonames.org/3181928/) und Venedig
(https://www.geonames.org/3164603/). Weitere Belege stehen direkt in der JSON-Datei.

## Wiederholung nach einem vollständigen Datenabruf

Im Hauptverzeichnis des Repositoriums:

```sh
python3 scripts/resolve_corpus_locations.py
```

Vorausgesetzt werden die bestehenden Skripte `build_itinerary_stations.py` und
`resolve_station_locations.py`, die Pilot-Zuordnungstabelle sowie die vier
MEI-Tabellen in `data/expanded/tables/`. Die abgeleitete Korpustabelle muss zum
verwendeten MEI-Abruf passen. Die Verarbeitung stellt keine neuen Netzwerkanfragen.

Geprüft wurden: Quelltabellenidentität mit dem Ergebnispaket, eindeutige
Stationskennungen, genau zwei Endstationen pro direkt zugehörigem Exemplar,
Koordinatenbereiche, punktlose offene Fälle, Beiband-Trennung, Erhaltung der
Montserrat-Alternative und identische Ausgabe bei wiederholtem Durchlauf.
