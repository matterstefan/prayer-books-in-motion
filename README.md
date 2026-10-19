# Prayer Books in Motion

An experimental visualisation of printed prayer-book copies, developed by Stefan Matter in the context of [PRAYTICIPATE](https://prayticipate.eu/) (COST Action CA23143), particularly WG1 and the material dimensions of prayer.

[Explore the website](https://matterstefan.github.io/prayer-books-in-motion/) · [Documentation](docs/README.md)

## Scope and current status

The October 2026 prototype brings together GW edition selection, ISTC identifiers and MEI copy histories. It displays 5,297 distinct MEI copies in a GW core and two optional additions based on MEI bibliographic subject and keyword fields. It is a data-reuse experiment, not a new catalogue or a census of all surviving prayer books. Source records remain unchanged; geographical display decisions are recorded separately.

The interface offers a timeline, schematic connections with adjustable clustering, circles and a heatmap, copy details, digitisation links, and contextual multi-select printing-place and language filters. The default collection is the GW core. Catalogue coverage and uncertain chronology limit what can be inferred from the map.

## Data sources

- [Gesamtkatalog der Wiegendrucke](https://www.gesamtkatalogderwiegendrucke.de/)
- [Incunabula Short Title Catalogue](https://data.cerl.org/istc/)
- [Material Evidence in Incunabula](https://data.cerl.org/mei/)
- [GeoNames](https://www.geonames.org/) for supplementary locality coordinates

The website is an independent project, not a CERL service. See the documentation and the website’s About panel for source attribution and acknowledgements. Public accessibility does not imply a blanket licence covering every linked resource.

## Running the site

The site is static HTML, CSS and JavaScript. It reads `data/map/copies.csv`, `stations.csv`, `digital-links.json` and `edition-languages.json`. It does not query the catalogues when a visitor opens the map.

From the repository root, run:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. Opening index.html directly as a local file does not support the data requests. GitHub Pages serves the same files without a database server. Leaflet assets and the background map require network access.

## Maintenance

Catalogue retrieval is a separate, manually triggered workflow. Preserve caches and review new data before publishing. The CERL access value is held only in the GitHub repository secret `CERL_USER_AGENT`; never put its value in source files or documentation. See [maintenance](docs/maintenance.md).

Current documentation baseline: 15 October 2026. Earlier dated notes remain as a record of development, not as current deployment instructions.

Further development is tracked in the [roadmap](docs/roadmap.md), including the session selection added after grant submission.
