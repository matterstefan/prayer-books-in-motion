# Digitisation links in copy detail

Build data/map/digital-links.json with scripts/build_digital_map_links.py after consolidation. The detail view separates This copy (MEI's explicit copy reference) from This edition (GW/ISTC edition references). Exact duplicate URLs are suppressed in the edition section when already shown for the selected copy. Labels and URLs are escaped; only HTTP(S) links are rendered. Source catalogue links remain visible. No scan is represented as verified complete.

337 visualised copies have direct digitisation references. Edition-level data cover 2,101 identifiers. The UI has expandable lists to preserve space on small screens. Data are static; opening the site does not query catalogues.

Verification: attribution and duplicate/unsafe URL handling tests; existing collection and heatmap tests. Prior HTTP samples confirmed several catalogue/viewer pages reachable, but the follow-up reading tool could not access the three selected GNM, BEIC and Wrocław target pages. No claim of visually verified scan completeness is made. A browser visual check of the UI remains for deployment.

This combined package supersedes prayer-books-consolidated-digital-links.zip; upload its contents preserving directories. It also sets the heat radius to 200 km and removes its slider. No new catalogue harvest is needed.
