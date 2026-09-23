# Analysis of the 60-ISTC MEI pilot

## Scope

This document records the first structured assessment of the MEI pilot
retrieved on 23 September 2026. The pilot was designed to test the data model
and later visualisation workflow. It is deliberately heterogeneous and is not
a statistically representative sample of incunable prayer books or of MEI.

The source snapshot is `data/sample/mei-pilot.json`. The four derived tables
were generated with `scripts/transform_mei.py`.

## Query results

| Measure | Count |
|---|---:|
| Selected ISTC identifiers | 60 |
| ISTC identifiers with at least one retained MEI relationship | 26 |
| ISTC identifiers without a current MEI hit | 34 |
| API hits reported across all queries | 88 |
| Unrelated full-text search results discarded | 2 |
| Retained MEI records | 86 |
| Direct ISTC–MEI relationships | 74 |
| `bound_with` ISTC–MEI relationships | 12 |

A zero-result query means only that no MEI relationship was returned at the
time of retrieval. It does not mean that no copy of the edition survives.

## What the 86 MEI records represent

The 86 retained records must not all be counted as copies of prayer books in
the selected corpus:

- 74 records directly describe a copy whose `hostItemId` matches the selected
  ISTC identifier;
- 12 records describe another component in a composite volume and mention the
  selected ISTC identifier under `boundWith`.

The twelve `bound_with` records remain important evidence for the material
history of composite volumes. They must not automatically generate twelve
additional prayer-book itineraries. Eleven of the twelve relationships supply
a linked copy identifier that corresponds to a direct record retained in the
pilot. One relationship does not supply a linked copy identifier. Every
selected ISTC identifier represented by a `bound_with` relationship also has
at least one direct MEI record in this pilot.

The default itinerary population should therefore consist of the 74 direct
copy records. `bound_with` records should be retained as a separate material-
relationship layer. Evidence may be transferred between components only when
the source and the binding history support that interpretation.

## Derived table sizes

| Table | Rows | Unit represented by one row |
|---|---:|---|
| `mei-copies.csv` | 86 | Retained MEI record |
| `mei-record-links.csv` | 86 | ISTC–MEI relationship |
| `mei-provenance.csv` | 250 | MEI provenance block |
| `mei-places.csv` | 163 | Place occurrence within a provenance block |

All primary identifiers are unique. Every provenance row points to a retained
MEI record, every place row points to a retained provenance block, and every
relationship points to a retained MEI record.

## Copy-record coverage

| Field or condition | Records | Share of 86 records |
|---|---:|---:|
| Copy ID | 86 | 100.0% |
| Host ISTC identifier | 86 | 100.0% |
| Holding institution identifier and name | 86 | 100.0% |
| Current shelfmark | 86 | 100.0% |
| Title, imprint, language, format, subject, and GW reference | 86 | 100.0% |
| Holding-country code | 83 | 96.5% |
| Description language | 79 | 91.9% |
| At least one provenance block | 70 | 81.4% |
| General notes | 36 | 41.9% |
| Author statement | 21 | 24.4% |

The low author coverage is not a problem for the intended visualisation. Title,
imprint, language, GW reference, present institution, and shelfmark are much
more important for identifying and filtering the printed prayer books.

## Provenance-block coverage

| Field or condition | Blocks | Share of 250 blocks |
|---|---:|---:|
| Agent | 224 | 89.6% |
| Time period | 188 | 75.2% |
| Place | 163 | 65.2% |
| Certainty code | 163 | 65.2% |
| Free-text note | 148 | 59.2% |
| Source code | 132 | 52.8% |
| Acquisition-method code | 97 | 38.8% |
| At least one separately extracted material-evidence field | 109 | 43.6% |

The relationship between dates and places is especially important:

| Combination | Provenance blocks |
|---|---:|
| Both time period and place | 132 |
| Time period but no place | 56 |
| Place but no time period | 31 |
| Neither time period nor place | 31 |

Only the 132 blocks containing both a place and a time period can immediately
support a time-sensitive map. The other blocks remain relevant evidence but
require different display treatment. Missing dates or places must not be
inferred from neighbouring blocks.

The MEI array order is source order, not a guaranteed chronological sequence.
Date ranges may overlap, be open-ended, or appear in an order that cannot be
converted mechanically into a single exact route.

## Place and coordinate coverage

| Field or condition | Place occurrences | Share of 163 occurrences |
|---|---:|---:|
| GeoNames identifier | 157 | 96.3% |
| Preferred place name | 155 | 95.1% |
| Latitude and longitude | 155 | 95.1% |
| Country name | 153 | 93.9% |

The 163 occurrences contain 49 distinct GeoNames identifiers. Eight place
occurrences lack coordinates. Six of these are free-text or otherwise
unnormalised place statements. Two London occurrences contain a GeoNames
identifier but no coordinates in the MEI place object. These cases should stay
visible for review rather than being silently removed.

Coordinates identify the referenced settlement or geographic entity. They do
not necessarily locate a historical building or the precise place where the
material evidence was created.

## Agent and authority-data coverage

The 250 provenance blocks contain 236 agent occurrences.

| Field or condition | Agent occurrences | Share of 236 occurrences |
|---|---:|---:|
| MEI owner identifier | 228 | 96.6% |
| Role code | 204 | 86.4% |
| Agent dates | 158 | 66.9% |
| At least one external identifier or link | 144 | 61.0% |

The agent objects contain 202 external links in total. These include 119 CERL
Thesaurus links and six direct GND links, alongside links to other authority,
library, biographical, and project resources. The 228 supplied owner
identifiers represent 157 distinct MEI owner IDs.

Agent types are not completely normalised in the source data: the pilot uses
both `person` and `per`, as well as `corporate`. These source values must be
preserved. A later convenience mapping may group documented equivalents for
filtering, but it must remain separate from the source columns.

Codes for certainty, provenance type, acquisition method, agent roles, and
binding characteristics are also preserved without expansion until the
relevant MEI/CERL controlled vocabularies have been checked.

## Suitability for itinerary visualisation

The 74 direct copy records provide the relevant initial population for
prayer-book itineraries.

| Condition among direct copy records | Copies |
|---|---:|
| At least one provenance block | 58 |
| At least one provenance place | 57 |
| At least two provenance places | 36 |
| At least one dated provenance place | 35 |
| At least two dated provenance places | 29 |
| No provenance place | 17 |

All 74 direct records can be connected with an extracted GW printing place
through the selected ISTC identifier. Sixty-eight also have a currently
extracted printing year; six require further work on the GW date statement.

The present holding institution and shelfmark are available for all direct
records. The holding-institution object does not itself supply map coordinates,
however. The present endpoint must therefore be connected with an existing
authority or place record, or cautiously matched to an appropriate MEI place
statement. This is a data-reuse task, not an invitation to create unsupported
coordinates.

The 29 direct copies with at least two dated provenance places form the
strongest initial subset for testing animated or time-slider routes. The 28
copies with one dated place or with undated places can still be displayed, but
their uncertainty must be visible. The 17 copies without a provenance place
can show printing place and present holding location once those endpoints have
been resolved, but not a documented intermediate route.

## Decisions implemented in the itinerary layer

The first itinerary station table follows these rules:

1. Create default itineraries only for direct MEI copy records.
2. Keep `bound_with` evidence as a separate relationship layer.
3. Add the printing place as an edition-level starting event with a GW/ISTC
   source reference.
4. Preserve provenance date ranges and missing values rather than selecting an
   invented exact year.
5. Treat MEI source order and chronological order as different properties.
6. Add the present holding institution as a distinct observed endpoint, while
   leaving its coordinates empty until the location is resolved through
   existing catalogue or authority data.
7. Retain every itinerary event's link to the source snapshot, MEI record, and
   provenance block from which it was derived.
8. Keep copies with sparse data in the interface and explain why their routes
   contain fewer stations.

These rules are implemented in `data/derived/mei-itinerary-stations.csv` and
documented in `docs/itinerary-data-model.md`. The reviewed place crosswalk and
map-ready table now resolve 276 of 287 station rows to point coordinates. The
pilot is therefore large enough to proceed to a first map prototype. It also
shows that a visually complete route cannot be produced for every copy without
making unsupported assumptions.
