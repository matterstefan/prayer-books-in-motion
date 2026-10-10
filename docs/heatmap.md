# Geographic heatmap (20261010-4)

Locations offers Circles and Heatmap. The heat radius control spans 20–300 km in 10 km steps, initially 100 km. Each selected copy contributes once at its last identifiable local point for the selected year. Countries and regions are excluded.

The smoothing radius is converted to screen pixels using Web Mercator scale at the latitude of each point. Its geographic extent is approximate (projection distortion over the kernel), but it grows with zoom rather than staying a fixed screen size. Contributions sum before colouring, and fade continuously to zero at the edge. Nearby places therefore form shared zones; these do not imply additional provenance observations between places.

The colour reference is the maximum potential density evaluated at all recorded localities of selected copies, using great-circle distances. A copy counts once per distinct candidate locality in this reference, regardless of year. The reference is stable across years, zoom levels and panning; changing the selected copies or radius recomputes it. It is a relative exploratory scale, not an absolute count legend. Strong values are clipped at its maximum. Clickable dots provide counts and copy details.

The canvas is in a Leaflet pane above tiles and below interactive markers and popups. It realigns and redraws after movement, zoom and resize. Location markers have no outline. No data harvest or new dependencies are required.

Validation: tests/heatmap.cjs verifies summed contributions, populated canvas, pane placement, stable reference across time and zoom, radius changes, empty selections and circle switching. tests/collections-map.cjs verifies collection combinations and other map behaviour. Visual browser verification remains to be done after deployment.
