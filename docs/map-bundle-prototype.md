# Linienbündel: einstellbarer Prototyp (3. Oktober 2026)

Unter dem Zeitregler: «Linien einstellen · Prototyp» aufklappen.
- Bündelungsstärke 0–100 Pixel, Start 32: 0 verwendet exakte Darstellungspunkte.
  Sonst werden Endpunkte auf einem Web-Mercator-Raster beim aktuellen Zoom
  zusammengefasst. Bei gleichem Reglerwert trennt Hineinzoomen mehr Orte.
  Kein pauschales Zusammenlegen historisch verschiedener Ortsidentitäten.
- Linienbreite 0.5–4, Start 1.5: Breite = Faktor × (2 + 2 × sqrt(Exemplarzahl)).
  Zählung pro Bündel: unterschiedliche Exemplare, nicht Zahl der Durchgänge.
- Verbindungen innerhalb derselben Rasterzelle werden in der Übersicht
  ausgeblendet. Die Exemplare bleiben über die Druckliste zugänglich.
- Linien zwischen Gruppen verbinden Mittelwerte ihrer unterschiedlichen
  Ortskoordinaten. Titel nennen beteiligte Orte; die Liste enthält die
  tatsächlichen Richtungen und Stationen je Druck. Dies sind Übersichtslinien,
  keine neu ermittelten Reiserouten.

Hover und Klick betreffen nur das Segment. Nach «Druck verfolgen» wird der
exakte Weg des Exemplars hervorgehoben. Die Druckliste sitzt am rechten Rand,
scrollt bei geringem Platz und verschiebt die Karte nicht. Auf schmalen
Bildschirmen ist sie unten angebracht. Zoom, Filter, Jahr und Regleränderungen
schliessen die Segmentliste, da ihre Zusammensetzung dann neu berechnet wird.
Regler gelten für die Sitzung; Neuladen stellt die Startwerte wieder her.

Prüfung: node tests/map-data.cjs, mit vollständigem Korpus und DOM/Leaflet-Stubs.
Geprüft: feinere Auflösung beim Hineinzoomen, eindeutige Exemplarzählung,
segmentbezogene Auswahl auch bei geteilten Exemplaren, Übergang zum Detail,
kein automatisches Verschieben beim Öffnen. Visuelle Browserkontrolle ausstehend.
