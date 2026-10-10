# Locations heatmap, 10 October 2026

Locations now offers Circles and Heatmap. Circles use a translucent fill. Heatmap adds weighted screen-space density behind small clickable locality markers. Country/region/area records are excluded. Each copy contributes once at its last identifiable local location for the selected year, following existing timeline rules.

A Gaussian kernel has a 28 CSS-pixel support radius, evaluated on a four-pixel grid. Zooming therefore changes its geographical reach. Redraws occur after zooming, panning, resizing, time changes and selection changes. The overlay is hidden during map motion to avoid showing geographically displaced density.

The colour reference is independent of the current year: for each selected copy, each distinct recorded local point contributes once to a reference field. Its maximum in the visible viewport supplies a fixed upper envelope for that map view and selection. This is a relative display reference, NOT an estimate of simultaneous historical holdings or an absolute count legend. Timeline movement never changes this reference. Zooming, panning or changing the selection can change it. Small dots provide exact current counts.

No extra dependencies or catalogue requests are required. The full source data remain unchanged. The new asset version is 20261010-2.

Deployment: replace index.html, assets/app.js and assets/styles.css at their existing paths. The tests and documentation may also be copied to their respective directories. Do not upload the extracted folder as a new enclosing directory. Existing data/map files are reused.

Validation: tests/heatmap.cjs checks weighted density, time-invariant reference, zoom recalibration, empty selection and circle transparency with DOM/Leaflet/canvas stubs. The existing map-data and collections-map tests also pass. A real browser visual check was unavailable in this environment; appearance and performance should be checked on the deployed site.
