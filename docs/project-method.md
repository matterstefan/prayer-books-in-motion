# Method and limitations

## Purpose

Prayer Books in Motion tests what existing catalogue data can reveal about the material circulation of printed prayer books. It offers leads for investigation in the source catalogues. It does not establish complete itineraries, actual travel routes, devotional use, or representative geographical distributions.

## Corpus and counts

The edition selection uses GW and ISTC identifiers. The additions use MEI’s edition-level bibliographic fields, not independently assigned genres.

| Collection | Displayed copies | Rule |
|---|---:|---|
| GW Horae and selected editions | 531 | GW Horae plus selected separately titled works |
| Additional liturgical editions | 1,778 | MEI hostItem.subject includes liturgy; core excluded |
| Additional devotional literature | 3,041 | MEI hostItem.subject or keywords includes literature-devotional; core excluded |

The additions overlap by 53 copies. Their union with the core contains 5,297 distinct MEI copy records. The map tables contain 20,498 station rows, including printing and holding stations and potentially multiple places for one source event; this is not a count of independently documented journeys. There are 2,375 selected ISTC identifiers; not every selected edition yields a displayed copy.

GW entries remain in the corpus even when later dating or bibliographical reassessment places them outside a strict pre-1501 boundary. This does not amount to an unrestricted extension to sixteenth-century printing.

## Editions and copies

GW and ISTC identify editions; MEI identifies copies and provenance evidence. Only direct edition–copy relationships are displayed. Bound-with relationships are retained in working data, but evidence from one constituent is not automatically assigned to another. Modern bindings do not define the historical unit being traced.

Library holdings mentioned only in GW or ISTC are not converted into new copy records. An absent library or locality is not evidence of absent holdings. It may reflect corpus selection, MEI coverage, missing coordinates or the retrieval date.

## Place and time

An identifiable printing place starts the sequence; recorded provenance stations follow; the current holding location ends it where known. Four records without a known current holding retain their last known location. Between records the last identifiable location is carried forward, including open dates. This is a display convention, not evidence of continuous presence. Undated stations may appear in the full present-day sequence without being assignable to earlier years.

Localities are mapped at city level. Reviewed coordinate aliases unify identified duplicate points, while original source values remain available. Broad areas do not become precise route vertices. The disputed Fort-de-France assignment is documented as a display decision, not a correction made in MEI. Remaining ambiguities are retained.

## Visual encoding

Connections are schematic. Solid and dashed lines distinguish dated sequences without an apparent gap from gaps and uncertainty; neither establishes a route. Wider lines represent more copies. Clustering groups nearby points around frequent locations, without claiming historical territorial boundaries.

Circles count distinct copies at the same display point and spatial precision for the selected year. The heatmap uses approximate 200 km kernels, excludes broad areas and holds its colour reference fixed across years and map views for the selected copies. Smoothed zones are not additional evidence between recorded places; colour is not an absolute count scale.

## Filters and languages

Printing-place variants use existing locality identifications and English display aliases. Explicit uncertainty remains labelled. Multiple options within a filter use OR; places and languages combine with AND. Facet counts respect collections, text search and the other filter; they ignore their own selection, the timeline and individual copy checkboxes. Zero-result unselected options are disabled; selected options remain removable.

The GW October 2026 export supplies preferred language sets where an exact ISTC match exists. Existing copy language is the fallback. Multilingual editions match every listed language. French and Middle French share a filter; Low German remains distinct. Original language strings and GW identifiers are retained in edition-languages.json. This file is a separate source snapshot, not refreshed by a MEI harvest.

## Digitisation and source links

The compact link file contains copy-level links for 337 MEI identifiers and edition-level links for 2,101 ISTC identifiers; these are link-availability counts, not verified complete digital copies. Copy links and edition links are displayed separately. Provenance images, watermarks and generic catalogue links were distinguished during preparation. Completeness and continuing availability are not systematically verified.

## Interpretation and sustainability

The visualisation includes modern collecting and antiquarian trade as well as earlier circulation. Uneven cataloguing, survival and institutional participation shape all patterns. Source records remain authoritative. Data retrieval is repeatable but not continuous: cached dated responses and documented manual display reviews support traceability, not a guarantee of identical results from changing catalogues.
