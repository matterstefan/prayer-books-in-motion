# Exploratory MEI API test

## Purpose

This test examines how the ISTC identifiers in the prayer-book corpus can be
used to retrieve copy-specific records and provenance data from Material
Evidence in Incunabula (MEI). It is an experiment in reusing existing public
catalogue data; it does not create or correct bibliographical or provenance
records.

## Public endpoint

MEI exposes a documented REST API:

`https://data.cerl.org/mei/_api`

The search endpoint is:

`https://data.cerl.org/mei/_search`

An ISTC identifier can be supplied as the query term. JSON is requested with
the parameter `_format=json`. The test additionally uses `mode=unstored`, so
the automated request is not added to the search history maintained by the
MEI web interface.

## Test sample

The script `scripts/fetch_mei_sample.py` requests six ISTC identifiers. Three
represent small and larger ordinary result sets. The other three are all the
ISTC links currently recorded for GW 13403 and therefore test a GW edition
with multiple ISTC relationships.

Run the test from the repository root:

```bash
python3 scripts/fetch_mei_sample.py
```

It writes the unabridged response records, together with retrieval metadata,
to `data/sample/mei-api-sample.json`.

## Preliminary observations

- The search returns one record per copy, identified by MEI's `id` and
  `copyId` fields.
- `hostItemId` contains the ISTC identifier used to connect the copy to the
  edition-level corpus.
- MEI's general search may also find an ISTC identifier in a `boundWith`
  reference. These records must not be discarded: they document a current or
  historical material relationship between the requested print and another
  component. The generated relationship list distinguishes `direct` links
  through `hostItemId` from `bound_with` links.
- `holdingInstitution`, `holdingInstitutionId`, and `shelfmark` describe the
  copy's current location.
- The nested `hostItem` object contains ISTC-derived bibliographical data,
  including title, imprint, language, format, and references such as the GW
  number.
- `provenance` is an array. Individual provenance blocks may contain a time
  period, one or more places, geographic coordinates, areas, agents, roles,
  certainty statements, notes, and other copy-specific evidence.
- Not every provenance block contains all these elements. Missing places or
  dates must remain missing rather than being inferred automatically.
- A missing MEI search result means only that no MEI copy record was returned
  for that ISTC identifier at retrieval time. It does not mean that no copy of
  the edition survives.
- GW 13403 demonstrates that multiple ISTC links must be retained separately:
  at the time of this test, two linked ISTC identifiers return MEI records and
  one does not.

## Result of the first run (22 September 2026)

- The combined API query reported 21 records.
- Fifteen records are linked directly through `hostItemId`; six further
  records are connected through `boundWith`. All 21 records are retained.
- The six additional records belong to three composite-volume situations, not
  to six independent physical volumes.
- In two situations a direct MEI record for the requested print also exists.
  In one situation the requested print is attested only through `boundWith`.
- Provenance evidence in a related record cannot automatically be transferred
  to every component. Binding evidence and later volume-level movements may be
  shared, while annotations or other evidence on the leaves may apply only to
  the component described by the MEI record.
- The binding date, where available, is essential: evidence predating the
  formation of the composite volume must not automatically be assigned to the
  other components.
- The 21 retained records contain 78 provenance blocks. Of these, 54 contain a
  place, 53 contain coordinates, and 58 contain a time period.
- One `bound_with` relationship names the requested ISTC edition without a
  separate MEI copy identifier. This indirect evidence must remain visible.
- The sample includes copies currently held by eleven institutions in several
  countries and editions printed in present-day Belgium, Germany, and
  Switzerland.

## Next technical step

Before querying the complete corpus, the sample should be transformed into
three linked tables: copies, provenance events, and places. This will reveal
which fields require normalization and which uncertainties must be preserved
for the later visualizations.
