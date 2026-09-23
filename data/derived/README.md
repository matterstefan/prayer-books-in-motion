# Derived data

The files in this directory are generated from the source tables and saved
snapshots in `data/`. They should not be edited manually.

Build the GW–ISTC corpus tables from the repository root:

```bash
python3 scripts/build_corpus.py
```

## Files

- `prayer-book-corpus.csv`: one row per GW edition from both source tables.
  The technical field `corpus_file` records the source filename without
  introducing a new scholarly category.
- `gw-istc-links.csv`: one row per GW–ISTC relationship. The table deliberately
  does not assume a one-to-one relationship between GW and ISTC identifiers.

The generated tables preserve the catalogue titles and identifiers supplied by
GW and ISTC. No new bibliographical records or titles are created.

## MEI tables

Transform the current 60-ISTC MEI pilot snapshot with:

```bash
python3 scripts/transform_mei.py
```

The generic transformer accepts another saved snapshot through `--input`.
For example, the initial six-ISTC test can still be transformed in a separate
temporary output directory with:

```bash
python3 scripts/transform_mei.py \
  --input data/sample/mei-api-sample.json \
  --output-dir tmp/initial-mei-test
```

This creates three linked research tables:

- `mei-copies.csv`: one row per retained MEI copy record;
- `mei-provenance.csv`: one row per provenance block, linked through `mei_id`;
- `mei-places.csv`: one row per place occurrence, linked through
  `provenance_id` and `mei_id`.

The additional technical table `mei-record-links.csv` preserves the exact
relationship between each requested ISTC identifier and the returned MEI
record. In particular, it distinguishes a direct match through `hostItemId`
from an indirect `bound_with` match.

In the current pilot, `mei-copies.csv` contains all retained MEI records: 74
direct prayer-book copy records and 12 records for other components connected
through `bound_with`. Use `mei-record-links.csv` when selecting the direct copy
population for itinerary generation.

Build the first visualisation-oriented station table with:

```bash
python3 scripts/build_itinerary_stations.py
```

This creates `mei-itinerary-stations.csv`. For each of the 74 direct copy
records it contains one printing-place station, every place occurrence from
the MEI provenance blocks, and one current-holding station. The current pilot
therefore contains 287 station rows: 74 printing places, 139 provenance places,
and 74 current holdings. The two endpoints are present even when no intermediate
provenance place is recorded.

Printing places and current holding institutions still need a reproducible
geocoding step. The table records this through `location_resolution_status`
rather than supplying guessed coordinates. Its time fields contain catalogue
evidence only; the year-by-year state used by a time slider is calculated in
the interface and is documented in `docs/itinerary-data-model.md`.

GeoNames identifiers and coordinates are retained in `mei-places.csv`.
MEI owner identifiers and external agent identifiers (including CERL and GND
links where supplied by MEI) are retained in `mei-provenance.csv`. The
`agents_json` field preserves the associations between an agent's name, role,
type, dates, identifiers, and other attributes. Uncommon evidence fields are
kept in `additional_evidence_json` rather than silently discarded.

These CSV files are analytical views, not replacements for the source data.
The current tables are generated from `data/sample/mei-pilot.json`. The
complete initial test remains available in `data/sample/mei-api-sample.json`.
The tables can be regenerated after an intentional data refresh.
