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

The join script never assigns coordinates to mappings whose status is not
`resolved`.

## Resolution statuses

| Status | Meaning | Map treatment |
|---|---|---|
| `resolved` | A city or locality has been linked to a GeoNames point | Show the station |
| `ambiguous` | The catalogue offers more than one possible place | Do not choose one point automatically |
| `country_only` | The evidence reaches only country level | Retain the statement without a point |
| `needs_review` | Bibliographical or semantic evidence is insufficient | Exclude from point display until reviewed |
| `non_geographic` | The MEI/CERL value is a placeholder rather than a place | Do not display as a location |

## Current pilot result

The crosswalk contains 61 mappings: 54 resolved and seven intentionally left
without a point. After the join, 276 of 287 station rows have coordinates.

The eleven station rows without point coordinates derive from seven mappings:

| Context | Source wording | Status | Reason |
|---|---|---|---|
| Printing place | `Italien` | `country_only` | No city supplied |
| Printing place | `Paris oder Rouen` | `ambiguous` | Two alternatives supplied |
| Printing place | `Montserrat` | `needs_review` | The extracted GW place must be compared with the edition-level ISTC and printer attribution before choosing the abbey, Monistrol, or Barcelona |
| Provenance place | `Italien` | `country_only` | No city supplied |
| Provenance place | `Schwarzau am Steinfeld (Vienna)?` | `needs_review` | The MEI wording is explicitly uncertain and combines two references |
| Present holding | `Historical Copy` | `non_geographic` | CERL/MEI placeholder |
| Present holding | `Trade Copy` | `non_geographic` | CERL/MEI placeholder |

## Homonyms and translated place names

A future value such as `Vienne` must be resolved at edition level. The string
may name Vienne in France, but in a French-language historical catalogue it may
also represent Vienna. Printer, date, ISTC/GW attribution, and the provenance
of the catalogue wording must therefore be checked together. The crosswalk key
may need to combine the source label with an edition identifier when the same
wording refers to different places.

This rule also applies to other homonyms, translated names, and changing
historical jurisdictions. A global replacement from a name string to one point
is not permitted when the corpus contains conflicting senses.

