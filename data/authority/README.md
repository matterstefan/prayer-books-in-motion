# Place-authority data

`place-authorities.csv` is the curated crosswalk between catalogue wording and
the city-level locations used by the map. It is an input to the visualisation
workflow and should not be overwritten automatically.

The table currently covers:

- every distinct printing-place statement in the 60-ISTC pilot;
- every present holding-institution identifier among direct MEI records;
- every MEI provenance-place occurrence that lacked coordinates in the source
  snapshot.

Resolved rows use GeoNames WGS84 point coordinates. Present holding
institutions are mapped to their cities, not to exact building coordinates.
This keeps their spatial precision comparable with MEI provenance places.

Rows marked `ambiguous`, `country_only`, `needs_review`, or `non_geographic`
deliberately have no point coordinates. They must not be sent to a generic
geocoder without bibliographical review.

Apply the current crosswalk from the repository root with:

```bash
python3 scripts/resolve_station_locations.py
```

This creates `data/derived/mei-itinerary-stations-resolved.csv`. When the source
corpus changes, add or revise crosswalk rows before running the script again.

