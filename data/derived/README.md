# Derived data

The files in this directory are generated from the source tables in
`data/corpus/`. They should not be edited manually.

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

## MEI sample tables

Transform the saved MEI JSON sample with:

```bash
python3 scripts/transform_mei_sample.py
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

GeoNames identifiers and coordinates are retained in `mei-places.csv`.
MEI owner identifiers and external agent identifiers (including CERL and GND
links where supplied by MEI) are retained in `mei-provenance.csv`. The
`agents_json` field preserves the associations between an agent's name, role,
type, dates, identifiers, and other attributes. Uncommon evidence fields are
kept in `additional_evidence_json` rather than silently discarded.

These CSV files are analytical views, not replacements for the source data.
The complete retrieved records remain in `data/sample/mei-api-sample.json`,
from which the tables can be regenerated after an intentional data refresh.
