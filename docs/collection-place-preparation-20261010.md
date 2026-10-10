# Ortsaufbereitung der drei Teilkorpora, 10. Oktober 2026

## Ergebnis

5.297 Exemplare, 20.498 Stationen. Gegenüber dem ersten aufbereiteten Stand wurden 900 weitere Stationen lokalisiert. 20.279 Stationen verfügen über Koordinaten; 219 bleiben ohne Koordinaten. Koordinaten bedeuten nicht automatisch einen lokalen Wegpunkt: Länder und Regionen werden weiter separat behandelt. Der finale Stand enthält 19.993 lokale Wegpunkte.

Die genaue Lage einer Bibliothek innerhalb eines Ortes ist für den Piloten nicht erforderlich. Quellenangaben, Datierungen und Identifikatoren bleiben erhalten. Neue Zuordnungen sind mit GeoNames-Referenzen und Kontextbegründungen dokumentiert. Die veröffentlichten Webseitendateien wurden nicht geändert.

## Entscheidungen von Stefan Matter

Burgdorf wird der Schweiz zugeordnet, Bassano dem Ort Bassano del Grappa. Vorpillière wird auf Ortsebene bei Massongex verortet; die abweichende ursprüngliche Länderangabe bleibt dokumentiert. Siebeneich bei Bretzfeld bleibt eine wahrscheinliche Zuordnung. Graflingen und Monte Leone bleiben ohne Punkt. Okno wird der Ukraine zugeordnet, ohne eine konkrete Ortschaft zu erfinden.

## Verbleibende Angaben

Die Restliste enthält 54 Gruppen: 27 ohne verwertbare Ortsangabe, 14 reine Gebietsangaben, vier mehrdeutige oder mehrteilige Druckangaben und neun offene Ortsidentifikationen. Hinzu kommen die bereits separat geführten elf Gruppen nicht lokal verortbarer Angaben.

Die neun offenen Ortsidentifikationen sind Anna C. Hoyt, St Charles Borromeo Seminary Library, St Francis College, Feldkirch, Graflingen, Hartwood, Königsbrück, Monte Leone und Okno. Die technischen und institutionengeschichtlichen Restfälle sind keine erneute Prüfliste für den Benutzer. St Charles Borromeo Seminary ist zwischenzeitlich umgezogen; der Bezug des knappen MEI-Nachweises zum aktuellen Standort soll nicht ungeprüft angenommen werden. Bei Feldkirch und Königsbrück bleibt der historische institutionelle Kontext zu sichern.

## Reproduktion

Die vorgelagerten Skripte prepare_collection_places.py und build_collection_place_review.py erzeugen die Stationsgrundlage. finalize_collection_places.py wendet die gespeicherten Zuordnungen auf mei-itinerary-stations-reviewed.csv an und schreibt mei-itinerary-stations-final.csv. Es greift nicht auf Webseiten zu. Die Zuordnungen stehen in data/authority/collection-locality-matches-20261010.json; Nutzerentscheidungen in stefan-place-review-20261010.json. Stabile Stations-IDs und Prüfungen der Quellenbezeichnungen verhindern ein stilles Übertragen auf veränderte Einträge.

GeoNames: https://www.geonames.org/, CC BY 4.0. Verwendet wurden Auszüge aus den am 10. Oktober 2026 abgerufenen GeoNames-Exporten. Originale externe Geokoordinaten werden nicht als neu ermittelte bibliographische Provenienzen ausgegeben.

## Prüfung

Stationsanzahl und IDs bleiben unverändert. Alle source_-Felder, ursprüngliche Länderangaben, Provenienz- und Institutions-IDs sowie Zeitgrenzen wurden mit dem vorherigen Stand verglichen. Koordinatenbereiche, die sieben Nutzerentscheidungen und die bestehende Fort-de-France-Anzeigeregel wurden geprüft. Eine Prüfung sämtlicher bereits zuvor vorhandener MEI-Koordinaten war nicht Gegenstand dieses Schritts.
