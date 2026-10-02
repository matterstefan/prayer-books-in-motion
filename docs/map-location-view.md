# Aufenthaltsorte (2. Oktober 2026)

Über dem Zeitregler lässt sich zwischen Verbindungen und Aufenthaltsorten wechseln.
Jahr, Filter, Exemplarauswahl und Kartenausschnitt bleiben dabei erhalten.
Die Detailansicht eines Druckes ist weiterhin über die Liste und die Kartenpopups erreichbar.

In der Ortsansicht werden keine Verbindungs- oder Hervorhebungslinien gezeichnet.
Jedes Exemplar zählt im gewählten Jahr höchstens einmal. Die vorhandene zeitliche
Zuordnungslogik bleibt unverändert: Quellenreihenfolge, Fortschreibung des letzten
zuweisbaren Nachweises, keine Darstellung vor dem Druckdatum. Ein späterer
unverortbarer Nachweis unterbricht die Fortschreibung. Heutige Aufbewahrungsorte
werden nur für die Gegenwart verwendet; historische/Handelsexemplare behalten
ihren ausdrücklich als Annäherung markierten letzten bekannten Ort.

Gruppiert wird nach Koordinaten (fünf Dezimalstellen). Als Länderpunkte markierte
Stationen bleiben von lokalen Punkten getrennt. Dies ist eine Bündelung von
Kartenpunkten, keine neue Normierung von Ortsnamen oder Institutionen.

Die Kreisfläche ist proportional zur Zahl unterschiedlicher Exemplare
(Radius = 6 × Quadratwurzel der Anzahl). Alle Kreise sind einheitlich weinrot;
eine qualitative Einstufung anhand offener oder geschlossener Datierungen entfällt.
Gestrichelter Rand: Länderpunkt.
Quellenzeiträume können selbst ungefähr sein; keine Einstufung beweist einen
ununterbrochenen Aufenthalt. Die Zahlen beschreiben die ausgewählten
Katalognachweise, keine historische Gesamtverteilung.

Popups nennen die Gesamtanzahl und für jedes Exemplar Titel,
Druckort/-jahr, heutige Bibliothek/Signatur, zugewiesene Station und deren
Datierung. «Druck verfolgen» öffnet die vorhandene Detailansicht.

Unveränderte Datenbasis; bekannte fragliche Ortsangaben bleiben zur gesonderten
Prüfung erhalten. Das bisherige Verhalten der Linienbündel wurde nicht geändert.

Prüfung: `node tests/map-data.cjs` (DOM-/Leaflet-Stubs), inklusive Aggregation,
gemischter Einstufung, Länderpunkttrennung, leerer Auswahl und Ansichtswechsel.
Die Tests ersetzen keine visuelle Kontrolle im Browser.
