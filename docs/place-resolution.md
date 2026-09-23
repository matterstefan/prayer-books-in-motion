# Place resolution

## Principle

Place resolution is a controlled interpretative layer. Catalogue wording is
retained in the evidence-level station table; the map uses a separate authority
crosswalk. A name string is never treated as sufficient evidence on its own.

The project uses city- or locality-level points. Present libraries are not
located at their exact buildings because the MEI provenance places normally
refer to cities. Using comparable spatial precision avoids implying movements
within a city that the catalogue data do not document.

## Workflow

1. `data/derived/mei-itinerary-stations.csv` retains the catalogue-derived
   station data.
2. `data/authority/place-authorities.csv` records reviewed mappings and
   unresolved cases.
3. `scripts/resolve_station_locations.py` applies the crosswalk.
4. `data/derived/mei-itinerary-stations-resolved.csv` is the map-ready result.
5. `scripts/validate_place_resolution.py` checks mapping counts, coordinate
   ranges, required authority fields, and conflicting points for the same
   preferred place name.

The join script never assigns coordinates to mappings whose status is not
`resolved`.

Mappings normally match a station type and a source label or institution ID.
Where a label is ambiguous, the optional `match_context_field` and
`match_context_key` columns restrict the mapping to one source record. A
context-specific mapping takes precedence over a generic mapping. This permits
the same wording to denote different places in different editions without a
global replacement.

By default, mappings for provenance places only fill records that lack point
coordinates. A reviewed row with `apply_to_existing_coordinates=true` may
correct or normalise an MEI-supplied point in the analytical map layer. The
source snapshot remains unchanged and the reason is recorded in
`resolution_note`.

## Resolution statuses

| Status | Meaning | Map treatment |
|---|---|---|
| `resolved` | A city or locality has been linked to a GeoNames point | Show the station |
| `ambiguous` | The catalogue offers more than one possible place | Do not choose one point automatically |
| `country_only` | The evidence reaches only country level | Retain the statement without a point |
| `needs_review` | Bibliographical or semantic evidence is insufficient | Exclude from point display until reviewed |
| `non_geographic` | The MEI/CERL value is a placeholder rather than a place | Do not display as a location |

## Current pilot result

The crosswalk contains 63 mappings: 56 resolved and seven intentionally left
without a point. After the join, 276 of 287 station rows have coordinates.

The eleven station rows without point coordinates derive from seven mappings:

| Context | Source wording | Status | Reason |
|---|---|---|---|
| Printing place | `Italien` | `country_only` | No city supplied |
| Printing place | `Paris oder Rouen` | `ambiguous` | Two alternatives supplied |
| Printing place | `Montserrat` | `ambiguous` | The unsigned edition is attributed through its type. Barcelona + [1498?] (ISTC/MEI) and Montserrat + circa 1499 (GW) are two historically coherent, coupled hypotheses that the surviving evidence does not decide between |
| Provenance place | `Italien` | `country_only` | No city supplied |
| Provenance place | `Schwarzau am Steinfeld (Vienna)?` | `needs_review` | The MEI wording is explicitly uncertain and combines two references |
| Present holding | `Historical Copy` | `non_geographic` | CERL/MEI placeholder |
| Present holding | `Trade Copy` | `non_geographic` | CERL/MEI placeholder |

During review, two inherited authority inconsistencies were corrected in the
analytical map layer, without altering the MEI source snapshot. Ferrara
now uses the GeoNames populated-place record `3177090`; the earlier
MEI-derived identifier `6299592` denotes a bus-terminal/airport feature. Paris
holdings and Paris provenance places now consistently use the capital record
`2988507`.

## Homonyms and translated place names

A future value such as `Vienne` must be resolved at edition level. The string
may name Vienne in France, but in a French-language historical catalogue it may
also represent Vienna. Printer, date, ISTC/GW attribution, and the provenance
of the catalogue wording must therefore be checked together. In such cases the
crosswalk combines the source label with the edition's `source_record_id`.

This rule also applies to other homonyms, translated names, and changing
historical jurisdictions. A global replacement from a name string to one point
is not permitted when the corpus contains conflicting senses.

Place and date must also remain coupled where an attribution depends on their
combination. For GW 13441, the map must not silently combine Barcelona with the
GW date or Montserrat with the ISTC date. If alternative hypotheses are later
shown in the interface, each must therefore be represented as a complete
place-and-date alternative with its own catalogue source.
