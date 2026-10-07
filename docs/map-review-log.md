# Prüfliste zur Darstellung und Zeitlogik

Stand: 2. Oktober 2026. Getrennt von Fehlern im Quelldatenbestand geführt.

## Festgehaltene Entscheidung: letzte bekannte Orte fortschreiben

Der zuletzt zuweisbare Ort bleibt die Darstellungsgrundlage bis zum nächsten
Provenienznachweis, auch wenn er der Druckort ist. Keine künstliche Lagerfrist
und kein angenommener Wegzug nach Ende des Druckzeitraums.
Ein späterer Nachweis ohne zuweisbaren Ort bleibt eine Informationslücke.

Eine Angabe wie „1868–“ wird in der vereinbarten Projektlogik bis zum nächsten
Provenienznachweis verwendet. Ein fehlendes Enddatum ist für sich genommen
kein Grund, den Ortsnachweis als schwächer einzustufen. Dies dokumentiert die
Projektentscheidung; eine allgemeine technische MEI-Regel wurde hier nicht
unabhängig geprüft. Quelldatierungen werden nicht um erfundene Endjahre ergänzt.

| ID | Gegenstand | Problem / Vorschlag | Status |
|---|---|---|---|
| V01 | Kreisfarben | Die aktuelle Einstufung verlangt Anfang und Ende für „im Quellenzeitraum“. Deshalb werden auch Nachweise wie 1868– weiss. Gold zeigt lediglich eine Mischung dieser technischen Einstufungen. Dies ist keine belastbare Abstufung der Nachweisqualität. Vorschlag: einheitliche Kreisfarbe, Anzahl über Kreisfläche, Datierungsangaben im Popup. Räumliche Unsicherheit separat behandeln. | Erledigt am 2. Oktober 2026 für die Ortsansicht: einheitliche Kreisfarbe; Einstufungszahlen aus Popup, Tooltip und Übersicht entfernt. Zeitlogik und Quelldaten unverändert |
| V02 | Hover und Auswahl gebündelter Linien | Bei einer gemeinsamen Verbindung werden alle vollständigen Wege der beteiligten Exemplare hervorgehoben. Das kann die einzelne Verbindung verdecken. Vorschlag: zunächst nur das Segment hervorheben; erst nach Auswahl eines Druckes dessen ganzen Weg. | Umgesetzt am 3. Oktober 2026: segmentbezogene Auswahl, feste Druckliste, Regler für Linienbreite und zoomabhängige Bündelung |

Die Ortsansicht bleibt vorläufig bestehen. Änderungen an Darstellung und
Zeitlogik werden separat umgesetzt und getestet; diese Liste ändert keinen Code.

Am 3. Oktober 2026 wurde die Rasterbündelung nach Nutzerrückmeldung durch gewichtete Ortsgruppen ersetzt. Beschreibung: `map-bundle-prototype.md`. 3D-Bögen bleiben eine spätere Idee.


## Navigation – 7. Oktober 2026

Rückmeldung: Auf dem 13.3-Zoll-MacBook ist die Darstellung gut lesbar.
Der Kopf der Exemplardetails bleibt jetzt beim Scrollen sichtbar.
Nach Öffnen eines Exemplars aus der Verbindungsliste führen Schliessen und
Escape zurück zur unveränderten Liste mit gespeicherter Scrollposition.
Die Exemplarhervorhebung bleibt erhalten, der Kartenausschnitt wird nicht verändert.
Filter-, Zeit-, Zoom- und Regleränderungen verwerfen den Rücksprung zur dann
überholten Verbindung. Details aus der Hauptliste erzeugen keinen Rücksprung.
Geprüft mit DOM-/Leaflet-Stubs; visuelle Kontrolle im Browser steht aus.

Weitere Rückmeldung vom 7. Oktober: «continuous residence» durch eine direkte
Formulierung zum Verbleib des Exemplars ersetzt; CSS-Pixel-Erklärung entfernt.
Jahresmarken proportional auf 1450–2026 positioniert (zuvor gleichmässig verteilt).
Slider-Daumen 16 px, Skala um dessen halbe Breite eingerückt.
Punktfarben, Hervorhebung und ausführliche Stationskommentare vorerst unverändert.
Kopfbereich: Platznutzung auf kleinen Bildschirmen als offener Gestaltungspunkt
vorgemerkt; möglicher Ansatz ist eine kompakte einzeilige Titelleiste.

## Feinere Zoomstufen – 7. Oktober 2026

Leaflet zoomSnap/zoomDelta auf 0.25; wheelPxPerZoomLevel auf 120.
Automatischer Kartenausschnitt passt weiterhin alle darstellbaren Punkte ein,
jetzt mit Viertelstufen und 24 statt 34 Pixel Rand. Keine feste Vergrösserung,
die entfernte Punkte abschneiden könnte. Startjahr, Bündelungsstärke und
Linienbreite bleiben unverändert. Bündelung mit gebrochenen Zoomwerten geprüft;
praktische Kontrolle von Trackpad-/Mausgefühl im Browser steht aus.
