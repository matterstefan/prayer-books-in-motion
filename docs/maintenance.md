# Maintenance and updating

## What is published

The static site needs index.html, assets/app.js, assets/styles.css and four files in data/map: copies.csv, stations.csv, digital-links.json and edition-languages.json. Preserve paths. No catalogue credentials are needed by visitors. Never copy an entire update folder as a nested project directory.

For a documentation-only change, upload only the changed Markdown files. No harvest or site-data rebuild is necessary. Keep private correspondence and the grant report outside the public repository.

## Retrieval and review

The manually triggered “Harvest three collections and digital links” workflow prepares membership and source results. The separate supplementary-link workflow retrieves GW/ISTC link candidates. They use the repository secret CERL_USER_AGENT and shared concurrency controls. Maintain the agreed maximum of 60 requests per minute across CERL requests; the established sequential workflow uses a two-second delay. Do not expose the secret value in output, errors or examples.

Preserve successful query caches so interrupted runs can resume. A partial artifact is not a complete replacement dataset: inspect summary counts and errors first. Distinguish zero results from blocked, malformed or failed responses. Retain source retrieval timestamps. An explicit refresh of completed queries is a separate decision; rerunning with caches does not refresh them.

After a changed corpus, recalculate membership and deduplicate direct copies, then review geographical assignments in staged collection tables. The active exporter scripts/build_collection_map_data.py reads data/collections/place-review/tables/mei-copies.csv and mei-itinerary-stations-final.csv. It does not itself perform the place review. Do not replace reviewed files with unreviewed harvest output.

The digitisation pipeline uses scripts/consolidate_digital_links.py followed by scripts/build_digital_map_links.py. Its input files must exist; retain source attribution and the distinction between copies and editions. Link retrieval failures do not prove that digital objects are absent.

The GW language lookup is independent. Preserve edition-languages.json during map exports. To update it, use the latest GW spreadsheet, match its ISTC field exactly against edition membership, collect the whitespace-separated Sprache codes, deduplicate codes and preserve each GW-Nr and raw language string. Do not change the source copy language column. No general-purpose importer for future spreadsheet versions is supplied yet.

## Before publishing an update

Review count changes, collection overlaps, direct/bound-with distinctions, and newly unresolved locations. Recheck any existing display override against the current source evidence. Update the About counts and dates where needed. Version query strings for changed frontend/data assets to prevent stale browser caches.

Current functional checks, run from the repository root:

```bash
node --check assets/app.js
node tests/collections-map.cjs
node tests/languages.cjs
node tests/digital-links.cjs
```

These checks use DOM/Leaflet stubs and do not replace a browser check. Some earlier tests retain fixed pilot counts; assess their intended dataset before treating failures as regressions. In a browser, check collection switching, filters and reset, selected zero-result options, timeline, connection-to-copy navigation, circles, heatmap, and digitisation attribution. A 13.3-inch screen is a useful layout check.

## Deferred work

Further owner-category filters, historical region classification, GW/ISTC-only holdings, broad corpus expansion, systematic digitisation verification and general refresh automation remain future work. Do not interpret these as completed features or required tasks for the current prototype.
