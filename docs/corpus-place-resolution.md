# Ortsauflösung und erweiterte Kartenansicht

Stand: 1. Oktober 2026. Quellenabrufe: 23.–30. September 2026.

## Ergebnis

Die Karte verwendet 484 direkt mit den ausgewählten ISTC-Ausgaben verknüpfte
MEI-Exemplarnachweise. Von 1’826 Stationen haben 1’823 Koordinaten:

| Stationstyp | Gesamt | Mit Koordinaten |
|---|---:|---:|
| Druckort | 484 | 484 |
| Provenienzort | 858 | 855 |
| Heutiger Aufbewahrungsort | 480 | 480 |
| Letzter bekannter Ort, heutiger Ort unbekannt | 4 | 4 |

Drei nicht lokalisierte Einband-/Werkstattangaben bleiben ohne Punkt. Viele
Provenienzblöcke enthalten überhaupt keinen Ort; die Stationszahl zählt
Ortsangaben, nicht sämtliche Provenienzblöcke. Die Karte behauptet daher keine
vollständigen Wege. 43 indirekt über Beibände verbundene Datensätze bleiben im
Quellenbestand und in den MEI-Tabellen erhalten, ohne automatisch übertragene
Provenienzwege. Die Zuordnung ist keine Aussage darüber, ob jedes historische
Exemplar heute noch identifizierbar oder erhalten ist.

## Nachvollziehbare Ortsentscheidungen

`data/authority/stefan-place-review.json` hält die 67 Fragen der manuell
bearbeiteten Prüfliste fest, darunter 64 ausgefüllte Entscheidungen für 97
Stationszeilen. Die drei nicht geografischen Angaben wurden nicht zugewiesen.
`reviewed-city-points.json` ergänzt dazu referenzierte Kartenpunkte. Bibliotheken
werden grundsätzlich auf Ortsebene verortet, nicht durch vermutete Gebäude.

Die Verarbeitung übernimmt vorhandene MEI-Koordinaten und Pilot-Zuordnungen,
ergänzt eindeutige Namens-/Land- oder GeoNames-Verbindungen und wendet zuletzt
die stationsbezogene Prüfung an. Bologna verwendet den Stadtpunkt 3181928
anstelle des Provinzpunkts 3181927. Ursprüngliche Namen, Labels und Koordinaten
bleiben in separaten Spalten erhalten. Neue Kartenpunkte sind technische
Darstellungszuweisungen, keine neuen Katalog- oder Provenienznachweise.

Besondere Entscheidungen:

- Montserrat bei GW 13441 wird für die Karte gewählt; die abweichende
  ISTC-Zuweisung Barcelona/1494 und die GW-Zuweisung Montserrat/1499 bleiben
  ausdrücklich erläutert. Vergleichbar bleiben Paris/Rouen und fragliche
  Paris-/Venedig-Zuweisungen als unsicher gekennzeichnet.
- Gripsholm wird mit dem Ort Mariefred verbunden, nicht mit einem behaupteten
  Standort der Druckerei im Schloss.
- Italien erhält einen repräsentativen GeoNames-Länderpunkt. Dieser ist kein
  rechnerisch erzeugter Flächenschwerpunkt. `spatial_precision=country` und ein
  grösserer gestrichelter Kreis kennzeichnen die geringe Genauigkeit.
- Kiel ist eine manuelle Zuordnung über den Besitzer Vollbehr, ausdrücklich
  ohne eigenständigen Aufenthaltsbeleg.
- Titusville ist im Scheide-Kontext Pennsylvania. Kontextbeleg:
  https://www.princeton.edu/news/2015/02/16/scheide-donates-rare-books-library-princeton-collection-largest-gift-universitys
- Die Quelle nennt für Grenville Kane in Tuxedo Park 1921–1850. Diese
  widersprüchliche Datierung bleibt unverändert gespeichert, wird markiert und
  für die historische Zeitzuordnung nicht verwendet.

## Historische und Handelsnachweise

Die Platzhalter HistCopy und TradeCopy sind keine heutigen Bibliotheken.
Ihre vier Datensätze wurden einzeln anhand des Quellenbestands behandelt:

| MEI | Letzter bekannter Ort | Datum |
|---|---|---:|
| 00201166 | Wien, Auktionsnachweis | 1905 |
| 00201167 | Rom, Barberini-Katalog | 1681 |
| 00201576 | Pforzheim, Kiefer-Angebot | 2024 |
| 02125950 | London, Quaritch-Angabe in der Signatur | 2018 |

Für diese Endstationen gilt `station_type=last_known`; der heutige Ort bleibt
unbekannt. London 2018 stammt aus der Signatur, während der letzte
Provenienzblock einen offenen Zeitraum ab 2017 enthält. Keine neue
Besitzdauer wird daraus abgeleitet.

## Karte und Zeitregler

Die Seite lädt die erweiterten Tabellen in `data/expanded/tables/`. Alle 484
Exemplare sind initial ausgewählt, das Jahr steht auf 2026. Suchfeld,
Druckort-/Sprachfilter, Auswahl und Details sind weiterhin verfügbar.
Öffnen und Schliessen der Details sowie Verändern des Jahres erhalten den
Kartenausschnitt; Filter und Zurücksetzen passen ihn bewusst an.

Linien sind schematische Verbindungen in Quellenreihenfolge und können Lücken
überbrücken. Im Gesamtbild bleiben undatierte Stationen sichtbar. In
historischen Ansichten werden nur zeitlich einordbare Stationen verwendet;
vor dem frühesten Druckjahr erscheint kein Weg. Offene Zeiträume und
Fortschreibungen erhalten einen offenen Punkt, ebenso unsichere Zuordnungen.
Eine spätere datierte Station ohne Kartenpunkt unterbricht die Fortschreibung
statt einen früheren Ort weiterhin anzuzeigen. Unbekannte Ankunftsdaten bei
heutigen Bibliotheken werden nicht aus dem Abrufdatum zurückgerechnet.

## Dateien und erneute Verarbeitung

Die Quellen (`mei-corpus.json` und die vier ursprünglichen MEI-Tabellen) werden
nicht umgeschrieben. Die abgeleiteten Tabellen sind:

- `mei-itinerary-stations.csv`: quellennahe Stationen;
- `mei-itinerary-stations-resolved.csv`: Kartenpunkte und Prüfhinweise;
- `location-review.csv`: drei verbleibende nicht geografische Stationen;
- `location-decisions.csv`: ergänzte, korrigierte oder offene Ortszuweisungen;
- `data/expanded/location-status.json`: Ergebniszahlen.

Nach einem vollständigen erneuten Abruf im Projektverzeichnis ausführen:

```sh
python3 scripts/resolve_corpus_locations.py
```

Erforderlich sind der vollständige Snapshot, die MEI-Tabellen, die aktuelle
Korpustabelle, die bestehenden Stations-/Pilot-Skripte und die vier
Authority-Dateien. Es entstehen keine Netzwerkanfragen. Die manuellen
Entscheidungen sind an Stationskennungen gebunden. Wenn sich das Original-Label
an einer Kennung ändert, hält die Verarbeitung zur erneuten Prüfung an.
Geänderte oder neu eingefügte Provenienzblöcke können eine erneute Prüfung der
Stationszuordnung erfordern; die gespeicherte Prüfung ist keine automatische
Garantie für künftige Katalogstände.

## Validierung

Geprüft: deterministischer Wiederaufbau, 97 angewandte Entscheidungen,
eindeutige Stationskennungen, Koordinatenbereiche, fünf Länderpunkte,
Bologna-Korrektur, vier historische Endstationen und erhaltene Quellenangaben.
`node tests/map-data.cjs` prüft die Kartenlogik mit DOM-/Leaflet-Ersatzobjekten:
484 Detailansichten, sechs Zeitpunkte, Suchfilter, keine Anzeige vor dem Druck,
Widerspruchsmarkierung und Erhaltung des Kartenausschnitts. Ein visueller
Browsertest konnte in dieser Umgebung mangels installiertem Browser nicht
laufen; die tatsächliche Kartendarstellung ist nach dem GitHub-Upload zu prüfen.
