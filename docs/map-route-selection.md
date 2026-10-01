# Kartenüberarbeitung, Schritt 1 — 1. Oktober 2026

Die angeklickte Route bleibt hervorgehoben, andere Routen und Marker werden
abgeblendet. Der Fokus bleibt beim Wechsel zur Detailansicht, beim Schliessen
des Fensters und beim Verstellen des Jahres erhalten. Ein Klick auf die freie
Karte oder «Hervorhebung aufheben» entfernt ihn. Wenn Filter oder Abwahl das
Exemplar aus der Darstellung entfernen, wird auch die Hervorhebung entfernt.
Popups verschieben die Karte nicht automatisch.

Abschnitte werden einzeln bewertet. Gestrichelt sind Verbindungen mit
ausdrücklich markierter Ortsunsicherheit, Länderpunkten, widersprüchlichen
Datierungen, übersprungenen Stationen oder Quellenblöcken, fehlender End-/
Anfangsdatierung, zeitlichen Lücken über ein Jahr oder unklarer Reihenfolge.
Zwei Orte desselben Provenienzblocks erzeugen ebenfalls keine gesicherte Folge.
Die übrigen Abschnitte sind durchgezogen. Die Regel beschreibt Eigenschaften
der vorhandenen Daten, keine unabhängig geprüfte historische Gewissheit.
Auch durchgezogene Linien sind schematische Verbindungen und kein Nachweis
einer direkten Reise. Der jeweilige Grund steht im Popup.

Die Gesamtfolge und die Zuordnung zum Jahr bleiben wie bisher. Bündelung und
die drei vereinbarten Kartenansichten folgen in weiteren Schritten.

Upload: index.html ins Stammverzeichnis; app.js und styles.css nach assets;
map-data.cjs nach tests; diese Datei nach docs. Bestehende Dateien ersetzen.
Die Datentabellen und Abrufskripte müssen nicht erneut hochgeladen werden.

Commit: Keep selected routes highlighted and distinguish uncertain segments

Prüfung: JavaScript-Syntax und vollständiger Datentest mit DOM-/Leaflet-Stubs,
einschliesslich dauerhaftem Fokus, Abblenden, Zeitwechsel und Einstufungsregeln.
Eine visuelle Browserprüfung ist in dieser Umgebung weiterhin nicht erfolgt.
