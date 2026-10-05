# Gewichtete Ortsgruppen – Prototyp vom 3. Oktober 2026

Ersetzt das zunächst erprobte starre Raster. Daten und historische Stationen
werden nicht verändert. Gruppierung dient nur der lesbaren Übersicht.

## Bedienung

«Linien einstellen · Prototyp» enthält:
- Bündelungsstärke 0–2400 Bildschirmpixel, Start 32. 0 = exakte Ortsverbindungen.
  Grössere Werte erlauben gröbere Gruppierungen; Zoom verändert die geografische
  Reichweite. Die Reglerwerte gelten für die Sitzung.
- Linienbreite 0.5–4: Faktor × (2 + 2 × sqrt(Anzahl unterschiedlicher Exemplare)).

## Verfahren

Für die ausgewählten Drucke und das gewählte Jahr werden die darstellbaren
Routenstationen gesammelt. Gewicht = unterschiedliche Exemplare am Ort, nicht
Anzahl wiederholter Aufenthalte. Länder und Regionen sind keine Routenzentren.
Orte werden nach absteigendem Gewicht, bei Gleichstand nach Koordinatenschlüssel
geordnet. Ein Ort wird einem bereits bestehenden nahen Zentrum zugeordnet oder
bildet selbst ein Zentrum. Kein transitives Anwachsen durch Randorte.

Reichweite eines Zentrums für einen Kandidaten:
Reglerwert × (0.5 + 0.5 × sqrt(Zentrumsgewicht / Maximalgewicht))
× (1 − 0.5 × Kandidatengewicht / Zentrumsgewicht).

Distanz wird in Web-Mercator-Bildschirmpixeln gemessen; Weltumbruch wird beachtet.
Die Reichweite überschreitet nie den Reglerwert. Unter mehreren geeigneten
Zentren gewinnt die kleinste Distanz relativ zur jeweiligen Reichweite.
Starke Nachbarn werden damit schwerer absorbiert. Zentren behalten ihr eigenes
Exemplargewicht: bereits aufgenommene Nachbarn vergrössern den Radius nicht.
Das Verfahren ist deterministisch, aber ein explorativer Ansatz, kein Modell
historischer Einzugsgebiete. Auswahl, Jahr und Zoom können Gruppen verändern.

Linien enden an den wirklichen Koordinaten der Zentren. «Gruppe um …» kennzeichnet
Zusammenfassungen; das feste Kontextfenster nennt tatsächliche Orte und Richtungen.
Innerhalb einer Gruppe liegende Verbindungen sind ausgeblendet, Exemplare bleiben
über die linke Druckliste erreichbar. Keine Doppelzählung mehrfacher Durchgänge
im selben Linienbündel. Hover/Klick hebt nur die Verbindung hervor; «Druck verfolgen»
zeigt den exakten Exemplarweg. Zoom/Regler/Filter/Jahr schliessen die Segmentliste.

3D-Ansicht mit Bögen als mögliche spätere Entwicklung vorgemerkt, nicht umgesetzt.

Prüfung: node tests/map-data.cjs mit vollständigen Daten und Leaflet/DOM-Stubs;
unter anderem keine Gruppierung bei 0, gewichtete Zentren, Reihenfolgeunabhängigkeit,
feinere Auflösung beim Zoom, Segmentauswahl und unveränderte Quelldaten.
Visuelle Browserkontrolle ausstehend.

Erweiterung vom 3. Oktober, abends: Regler bis 2400 CSS-Pixel für extreme Tests.
CSS-Pixel sind logische Anzeigeeinheiten, keine physischen Gerätepixel.
Bei maximaler Zusammenfassung können sämtliche Linien verschwinden, weil
beide Enden in derselben Ortsgruppe liegen. «Ortsgruppe» und «Exemplare auf
dieser Verbindung» werden im Kontextfenster ausdrücklich unterschieden.

Update 5 October 2026: the active slider maximum is now 600 CSS pixels, following user testing. Earlier limits above describe superseded experiments. The public interface is now English; source wording is retained.
