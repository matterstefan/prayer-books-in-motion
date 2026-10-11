# Language filtering

Updated 11 October 2026 following Stefan Matter’s review.

GWGesamtliste-Oktober26.xlsx (Oliver Duntze) provides preferred language codes for exactly matched ISTC identifiers. data/map/edition-languages.json preserves the raw GW values and GW identifiers. Repeated codes are deduplicated; multiple matching GW records contribute their language codes. Without a GW language entry the existing copy language remains in use.

The single-language dropdown matches any language of a multilingual edition. French (fre) and Middle French (frm) share the French filter; original codes remain preserved. Low German (nds) has its own option. Detail and list labels show all preferred source languages. No multi-select interface is added.

The GW snapshot is independent of MEI refreshes. For an updated GW export, rebuild this lookup from its ISTC and Sprache columns; do not overwrite original copy language fields.
