# Itinerary data model

## Purpose

The itinerary layer brings together three kinds of location evidence for each
direct MEI copy record:

1. the printing place recorded for the edition in GW;
2. place occurrences contained in the copy's MEI provenance blocks;
3. the present holding institution recorded in MEI.

The generated table is `data/derived/mei-itinerary-stations.csv`. It can be
rebuilt with:

```bash
python3 scripts/build_itinerary_stations.py
```

This layer does not create new historical evidence. It makes existing catalogue
statements available in one structure for experimental visualisation.

## Population and endpoints

Only MEI records linked through a `direct` relationship in
`mei-record-links.csv` receive a default itinerary. Records found only through
`bound_with` remain available in the relationship table but are not silently
treated as independent copies of the requested prayer-book edition.

Every direct itinerary has exactly one first and one last station:

- `print_place`: the edition-level printing statement, repeated for each
  surviving copy of that edition;
- `current_holding`: the holding institution observed in the current MEI
  snapshot.

MEI provenance places are inserted between those endpoints. A copy without a
place-bearing provenance block therefore still has two known locations. It has
no documented intermediate location.

The present holding statement proves where the copy was recorded when the MEI
data were retrieved. It does not by itself prove when the copy arrived there.
The `observation_date` therefore records the retrieval date while `time_start`
and `time_end` remain empty unless a separate dated acquisition statement is
available.

## Ordering

`source_order` preserves the structural order needed to inspect the assembled
data:

- printing place: `0`;
- provenance place: the containing MEI provenance block's sequence number;
- present holding: one number after the last place-bearing provenance block.

This is not automatically a verified historical chronology. Broad and
overlapping dates, undated evidence, and the source order of provenance blocks
may prevent a single unambiguous sequence. `place_order_within_source` retains
the order of several places within one provenance block.

## Time-slider states

The interface should calculate a display state for a selected year rather than
generate one asserted location for every year in the CSV.

| Condition at selected year | Display state | Map treatment |
|---|---|---|
| Year precedes the printing date or range | `not_yet_printed` | Do not show the copy as circulating |
| Year falls within one dated station | `documented` | Show that station as the evidenced location |
| Year falls within several incompatible or overlapping stations | `ambiguous` | Show the alternatives or an explicit ambiguity marker |
| No station covers the year, but an earlier station is known | `last_documented_uncertain` | Keep the marker at the last evidenced place and label the current location as uncertain |
| Selected year is the snapshot year | `current_holding_observed` | Show the present holding institution |

The final state must not imply that the copy reached its present institution
only in the snapshot year. If a dated accession or institutional provenance is
later available, it can provide an earlier evidenced start for the present
holding.

## Route lines

Lines connect the known or selected stations as a visual aid. They are
schematic connections between catalogue evidence, not reconstructed travel
routes. At a selected year, the interface may emphasise the known route up to
that point and render later known stations more faintly. Gaps must remain
visibly uncertain.

## Location resolution

MEI provenance places retain their supplied GeoNames identifiers and
coordinates. Printing places currently retain the GW wording but still need
geocoding. Present holdings retain their MEI institution identifiers and names
but likewise still need to be resolved to map coordinates. The field
`location_resolution_status` makes these open tasks explicit.

Geocoding should be added as a reproducible authority-mapping step. Coordinates
must not be guessed from free-text strings in the browser.

## Composite volumes

The itinerary table currently excludes records found only through
`bound_with`. This does not declare their provenance evidence irrelevant. It
prevents evidence attached to the host volume from being applied automatically
to every component. Such cases can later be included with an explicit evidence
scope such as component-specific, binding-level, or uncertain.

