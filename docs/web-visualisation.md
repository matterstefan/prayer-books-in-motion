# Web visualisation

## Technical scope

The first prototype is a static site intended for GitHub Pages. It consists of
`index.html`, `assets/styles.css`, and `assets/app.js`. It needs no application
server, database, package installation, or build step.

At page load, the browser reads:

- `data/derived/mei-copies.csv` for copy-level descriptions and filters;
- `data/derived/mei-itinerary-stations-resolved.csv` for the ordered stations.

An intentional refresh of the derived CSV files therefore updates the website
after the changed files are committed. The site does not use a separate frozen
JSON export.

Leaflet is loaded from the unpkg CDN. The base map uses OpenStreetMap tiles and
displays the required attribution.

## Initial interface

The map opens at 2026 with all 74 direct MEI copy records selected. Users can:

- move the time slider from 1450 to 2026;
- search by title, shelfmark, MEI ID, ISTC ID, or GW reference;
- filter by printing place and language;
- select or deselect individual copies;
- click a route or location marker for a compact summary;
- open the persistent `Einen Druck verfolgen` panel without losing the map
  extent and filter state.

## Time-slider rule

A station is treated as directly evidenced when the selected year lies within
its supplied time interval. In a gap after a dated station, the interface keeps
showing the last known mapped place with a hollow marker. This is an explicitly
labelled approximation, not a new provenance assertion.

The 2026 view uses the present holding institution observed in the MEI
snapshot. A non-geographic present-holding value such as `Historical Copy` or
`Trade Copy` does not receive an invented location.

Undated stations remain visible in the copy details. They are not assigned an
arbitrary year for the current-location marker.

When the last provenance-place station and the current holding institution
have identical coordinates, the interface combines them into one displayed
final station. Any supplied historical date remains attached to the combined
entry. The two source rows remain unchanged in the derived CSV table.

## Spatial rule

Straight lines connect mapped stations in source order. They show the sequence
of recorded places, not an actual historical travel route. Ambiguous,
country-level, review-required, and non-geographic statements remain in the
details but do not generate map points.

For GW 13441, the coupled alternatives Barcelona + `[1498?]` and Montserrat +
`circa 1499` remain unresolved; the prototype does not combine either place
with the other catalogue's date.
