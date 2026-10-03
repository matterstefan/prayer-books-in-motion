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
