# Three collections: frontend update, 10 October 2026

The map starts with the GW core collection (531 copies). Optional additions contain 1,778 liturgical copies and 3,041 devotional copies. Both exclude core editions. The two additions overlap by 53 copies; the combined display contains 5,297 unique MEI copies.

Collection controls apply to the list, both map views, search, place/language filters, and matching-copy selection actions. Switching a collection preserves the map viewport and individual checkbox selections but clears the previous route/detail focus. Reset restores the core-only collection choice. No selection produces an empty view, not an automatic fallback to the core.

The static map loads data/map/copies.csv and stations.csv, exported by scripts/build_collection_map_data.py from the staged, reviewed tables. Full provenance source data remain separate. The About panel explains collection scope and copy coverage. Digital scan candidates are not yet integrated.

Deployment: merge the ZIP contents into the repository at their existing paths. Replace index.html, assets/app.js and assets/styles.css. Add data/map/ and the included preparation files under their indicated directories. Do not nest the entire extracted folder inside the repository. No harvest run is required. The asset/data query version is 20261010-1.

Validation: node tests/map-data.cjs passed against the prior 484-copy fixture. node tests/collections-map.cjs passed against the new 5,297-copy data for all eight collection combinations, deduplication, search/language filtering, location policies, details and both map modes. These tests use Leaflet and DOM stubs; actual browser layout and MacBook performance still require practical review.
