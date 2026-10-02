# Gebündelte Ortsverbindungen

Stand: 1. Oktober 2026, zweiter Schritt der Kartenüberarbeitung.

Gemeinsame geometrische Streckenabschnitte werden als eine Linie dargestellt.
Verglichen werden die Koordinaten der beiden Endpunkte, gerundet auf fünf
Nachkommastellen. Es findet keine unscharfe Zusammenführung unterschiedlicher
Stadt-, Institutions- oder Länderpunkte statt. Linienkreuzungen ohne gemeinsamen
Endpunkt werden nicht gebündelt. Gegenrichtungen teilen dieselbe Linie, werden
aber im Kontextfenster mit Richtungspfeilen getrennt beschrieben.

Die Breite richtet sich nach unterschiedlichen Exemplaren im Bündel, nicht nach
der Anzahl der Vorkommen. Wiederholt ein Exemplar einen Abschnitt, zählt es nur
einmal. Breite in Pixeln: 2 + 1,5 × log2(Exemplarzahl + 1). Die gedämpfte Skala
hält seltene und häufige Verbindungen gemeinsam lesbar. Die genaue Zahl steht
im Tooltip und im Popup. Sie ist abhängig von Jahr, Suche, Filtern und Auswahl.

Ein Bündel ist gestrichelt, sobald mindestens einer seiner Abschnitte nach den
vorhandenen Regeln als unsicher oder lückenhaft gilt. Die individuelle
Einstufung steht beim jeweiligen Exemplar. Die dargestellte Häufigkeit misst
Katalogbeziehungen und keine gemeinsam belegten Reisen oder Verkehrsströme.

Beim Mouseover werden die vollständigen Wege der beteiligten Exemplare
hervorgehoben. Eine feste Auswahl hat Vorrang. Beim Klick bleibt das Bündel
ausgewählt; das Popup enthält eine scrollbar angelegte Liste mit Titel,
Druckort, Druckjahr, heutiger Institution und Signatur. «Druck verfolgen»
wechselt zur Detailansicht und hebt nur noch dieses Exemplar hervor. Eine
farbige, nicht anklickbare Überlagerung zeigt dabei seine eigenen Linienarten
über dem aggregierten Netz. «Hervorhebung aufheben» oder die freie Karte
entfernen den Fokus. Jahres-/Filterwechsel lösen eine Bündelauswahl auf;
eine weiterhin sichtbare Einzelauswahl bleibt wie bisher erhalten.

## Upload

- index.html ins Stammverzeichnis
- app.js und styles.css nach assets
- map-data.cjs nach tests
- map-route-bundles.md nach docs

Commit: Bundle shared map segments and list associated copies

Die Daten und Abrufskripte bleiben unverändert. Die neue Versionskennung in
index.html fordert die aktualisierten JS-/CSS-Dateien an.

## Prüfung

JavaScript-Syntax und Funktionstests mit DOM-/Leaflet-Ersatzobjekten erfolgreich:
484 Detailansichten; Zeitschieber; Auswahl und Hervorhebung; Gruppeneindeutigkeit;
Exemplarzählung bei Hin- und Rückwegen und Wiederholungen; Einzelauswahl;
Popup-Einträge für sämtliche Gruppenmitglieder; keine Wege vor dem Druckjahr.
Eine visuelle Browserprüfung ist nach dem Upload noch erforderlich.
