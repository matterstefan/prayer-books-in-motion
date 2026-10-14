# Language filtering

Updated 11 October 2026 following Stefan Matter’s review.

GWGesamtliste-Oktober26.xlsx (Oliver Duntze) provides preferred language codes for exactly matched ISTC identifiers. data/map/edition-languages.json preserves the raw GW values and GW identifiers. Repeated codes are deduplicated; multiple matching GW records contribute their language codes. Without a GW language entry the existing copy language remains in use.

The language dropdown allows multiple choices and matches any selected language of a multilingual edition. French (fre) and Middle French (frm) share the French filter; original codes remain preserved. Low German (nds) has its own option. Detail and list labels show all preferred source languages. Printing places also allow multiple choices. Within either filter choices use OR; the two filters combine with AND. An empty selection means no restriction. Clear selection and the global reset restore this state.

The GW snapshot is independent of MEI refreshes. For an updated GW export, rebuild this lookup from its ISTC and Sprache columns; do not overwrite original copy language fields.

## Contextual filters (14 October 2026)

Printing-place options use existing preferred place identifications, with explicit English display aliases for remaining variants (e.g. Venedig → Venice, Gent → Ghent, Prag → Prague). Original station labels and map coordinates remain unchanged. Explicitly uncertain identifications retain a (?) label and remain distinct; unresolved alternatives are not assigned to one city.

Each facet counts unique copies within the selected collections and text search, applying the other facet but not its own selection. Counts do not depend on the year slider or individually checked copies. Zero-result unselected options are disabled; selected options always remain enabled for deselection. This preserves OR expansion within each facet and AND between facets. Canonical printing-place labels also participate in text search.
