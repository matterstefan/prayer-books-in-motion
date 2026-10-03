# Prüfliste zum Datenbestand

Stand: 3. Oktober 2026. Fortlaufende Liste für Datenfragen und Nachbesserungen.
Ein Eintrag ist keine bereits vorgenommene Korrektur. Originalangaben bleiben
erhalten; bestätigte Änderungen werden in der Verarbeitung nachvollziehbar
dokumentiert. Korpusergänzungen stehen separat in `corpus-additions.md`.

| ID | Gegenstand | Beobachtung / Beleg | Nächster Schritt | Status |
|---|---|---|---|---|
| D01 | Venedig: doppelte Kartenposition | In der lokalen Stationstabelle erscheinen Venedig-Nachweise bei 45.43713, 12.33265 und 45.4389, 12.33092. Die Ortsansicht bündelt deshalb für 1935 zwei Gruppen mit 71 und 2 Exemplaren. | Herkunft und Orts-/Institutionspräzision der Koordinaten vergleichen; für die Stadtansicht eine gemeinsame Ortsidentität verwenden, ohne gegebenenfalls präzisere Institutionskoordinaten aus den Quelldaten zu löschen. Anschliessend ähnliche Fälle im übrigen Bestand suchen. | Erledigt für die Darstellung am 3. Oktober 2026; siehe unten |
| D02 | MEI 02128182: Fort-de-France, 1700–1800 | Der übernommene Datensatz enthält einen Ortsverweis mit Koordinaten auf Martinique, gleichzeitig den Gebietscode e-fr. Die vom Nutzer gezeigte MEI-Seite nennt France; Initialen R.D. und Exlibris-Erläuterung begründen Martinique nicht. | Widerspruch auf Quellenebene prüfen, gegebenenfalls an MEI melden. Eine nur auf Frankreich beschränkte Anzeige wäre eine mögliche dokumentierte Behandlung, ist aber noch nicht beschlossen. | Für die Darstellung entschieden und umgesetzt am 3. Oktober 2026; Originaldaten erhalten |
| D03 | Geklammerte Druckdatierungen | Angaben wie 14[74] können bei der bisherigen Jahresableitung unvollständig ausgewertet werden. Nutzerhinweis aus der Korpusprüfung. | Extraktion solcher Schreibweisen verbessern; Originaltext und Unsicherheitszeichen erhalten. Fragezeichen nicht als sichere Datierung weginterpretieren. | Zur späteren Bearbeitung vorgemerkt |

Bei Erledigung: Datum, betroffene IDs, Entscheidungsgrundlage, geänderte Datei
und Prüfung ergänzen. Ein Datenabruf darf dokumentierte Zuordnungen nicht
unbemerkt überschreiben.


## Beschlossene Darstellungszuordnungen – 3. Oktober 2026

Von Stefan Matter bestätigt und in `assets/app.js` umgesetzt. Keine Änderung
an Quelldatensätzen, Koordinatenfeldern, Ortsnamen oder Ortsreferenzen.
Die explizite Zuordnung wirkt auf Ortskreise und Verbindungen; es findet
keine automatische Zusammenführung beliebiger benachbarter Punkte statt.

| Ort | Bisheriger Punkt → gemeinsamer Darstellungspunkt |
|---|---|
| Venedig | 45.43890, 12.33092 → 45.43713, 12.33265 |
| Nürnberg | 49.45410, 11.07680 → 49.45421, 11.07752 |
| Mailand | 45.46416, 9.19199 → 45.46427, 9.18951 |
| Antwerpen | 51.22047, 4.40026 → 51.21989, 4.40346 |
| Den Haag | 52.06866, 4.28635 → 52.07667, 4.29861 |
| Amsterdam | 52.37302, 4.89856 → 52.37403, 4.88969 |
| Valletta | 35.89833, 14.51250 → 35.89968, 14.51480 |
| Vatikan | 41.90268, 12.45414 → 41.90225, 12.45330 |
| Yale / New Haven | 41.31121, -72.92649 → 41.30815, -72.92816 |
| Blickling Estate / Hall | 52.80900, 1.23100 → 52.81180, 1.23180 |

Venedig, Nürnberg, Mailand und Valletta: gleich benannte Orte mit unterschiedlichen
Ortsreferenzen. Antwerpen: gleiche GeoNames-ID, verschiedene Koordinaten.
Den Haag und Amsterdam: Stadt-/Gemeindebezeichnungen auf Stadtebene gebündelt.
Vatikan bleibt von Rom getrennt. Yale und Blickling sind ausdrücklich beschlossene
Vereinfachungen der räumlichen Darstellung; keine Gleichsetzung der Institutionen.

Weitere Entscheidungen:

- **Europe (MEI 02020083, GeoNames 6255148): erledigt.** Kein lokaler Kartenpunkt;
  die Station bleibt mit Erklärung in den Details. Ein solcher Nachweis unterbricht
  weiterhin die Fortschreibung eines früheren Ortes; Routen können die Lücke
  gestrichelt überbrücken.
- **Turin: erledigt.** GeoNames 3165525 bezeichnet die Gemeinde, 3165524 den städtischen Ort. Geprüft anhand https://www.geonames.org/3165525/torino.html und https://www.geonames.org/3165524/turin.html. Darstellung: 45.05, 7.66667 → 45.07049, 7.68682.
- **Benannte Teilorte bleiben getrennt:** unter anderem Murano, Westminster,
  Hradčany und Brooklyn. Keine Zusammenführung allein aufgrund geringer Distanz.
- **Fort-de-France: Darstellung korrigiert**, siehe unten. Eine Korrektur im Quellkatalog ist damit nicht erfolgt.

Prüfung: `node tests/map-data.cjs`, unter anderem Venedig 1935: ein gemeinsamer
Punkt mit 73 Exemplaren statt 71 + 2; Erhalt aller Quellangaben, Ausschluss des
Europa-Punkts, Erhalt der ausdrücklich getrennten Orte und bisherige Kartentests.


## Abschliessende Entscheidungen dieser Runde

- **MEI 02128182, Station 02128182-p003-loc01, 1700–1800:** Stefan Matter hat
  den MEI-Nachweis erneut geprüft. Kein Anhaltspunkt für Martinique; Gebietscode
  e-fr ist vorhanden. Anzeige: «Frankreich, genauer Ort unbekannt», Länderpunkt
  46, 2. Der Originaldatensatz und die CSV bleiben unverändert. Die eng begrenzte
  Darstellungsregel in `reviewedStation` greift nur bei derselben Stations-ID,
  Ortsreferenz 3570675 und Datierung. Ursprüngliche Ortsreferenz und Koordinaten
  sind in den Quellen weiterhin nachvollziehbar; die Details erklären den Eingriff.
- **Länder:** GeoNames 3017382 Frankreich, 2921044 Deutschland, 3175395 Italien,
  798544 Polen, 2658434 Schweiz, 6252001 USA, 6269131 England. Einheitliche
  Behandlung als Gebietsangaben statt lokale Aufenthaltsorte.
- **Regionen:** 2951839 Bayern, 2655856 Berkshire, 3174618 Lombardei,
  6254927 Pennsylvania, 3164604 Veneto.
- **Europe und Western Europe:** 6255148 bzw. 9408659, kein Kartenpunkt.

Länder und Regionen behalten repräsentative Kreise in der Ortsansicht, mit
Hinweis im Popup/Tooltip und gestricheltem Rand. Sie sind keine Haltepunkte
von Linien. Zwischen den verbleibenden konkreten Orten werden solche Lücken
nur gestrichelt überbrückt; die Linienerklärung nennt dazwischenliegende Gebiete.
Bei einem aktuell nur auf Gebietsebene zuweisbaren Exemplar zeigt die
Verbindungsansicht keinen lokalen Aufenthaltsmarker. Die Fortschreibung wird
nicht auf einen älteren konkreten Ort zurückgesetzt.

Diese Regeln werden beim Laden der vorhandenen Stationstabelle angewandt und
bleiben damit auch bei erneuter Erzeugung der Tabelle wirksam. Neue Normdaten-IDs
oder geänderte Quellenangaben erfordern eine erneute Prüfung. Die bereinigte
Darstellung ist keine Behauptung einer vollständig geprüften Quelldatenbasis.
