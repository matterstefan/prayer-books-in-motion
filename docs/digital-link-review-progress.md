# Digital-link review: resumable first pass

## Scope

This is a checkpoint, not a completed digitisation catalogue. No links have yet been added to the website. No full scan has been certified from HTTP availability alone.

The harvested 4,120 references contain 3,882 distinct URLs after trimming surrounding whitespace (original URLs and all source references retained). Sources: 878 MEI references and 3,242 GW references. The inventory flags 199 URLs whose source references are exclusively provenanceImage fields, and 128 watermark.kb.nl URLs. These are source-based distinctions, not a visual examination of the destinations.

725 unique URLs have a copy-level MEI reference; 3,157 have edition-level references only. MEI references concern 530 visualised copies and 97 other MEI records. link-inventory.json explicitly records visualised_mei_ids and other_mei_ids, so ancillary records must not silently transfer their links to copies on the map. A source copy reference is not independent confirmation of the destination's identity.

## Checks and continuation

Run `python3 scripts/audit_digital_links.py --limit 20` from the repository root for the next small batch, or `--limit 0` to rebuild the inventory and summary without network requests. Each URL check is saved immediately under data/collections/digital-review/checks using a stable hash. Existing checks are skipped, including failures; retrying failures must be a separate deliberate pass. Keep the checks directory to resume. Never treat an access challenge, timeout or environment proxy denial as proof of a dead link. Protected CERL destinations are skipped; this script contains no access credential.

First inspected responses include redirects from SNK's former onk address to DIKDA, and a Wrocław publication page with title Agenda sive Exsequiale sacramentorum. A BEIC address returns a page titled Leggenda di sant'Alessio. These are reachable catalogue/viewer pages, not yet verified complete scans. The e-rara DOI request encountered an environment proxy denial, so its actual availability has not been tested here.

## Remaining source extraction work

The candidates currently contain no ISTC URL entries. In 2,372 cached ISTC search records, 1,334 have reproduction text; only eight mention electronic/digital reproductions explicitly. Search-result text is not sufficient evidence that the full ISTC records have no links. Inspect full-record export or HTML using authorized CERL access before claiming coverage. Preserve edition-level attribution.

87 GW harvest errors remain (85 recognition errors and two HTTP errors in the previous run). The current GW page validator is too restrictive for some legitimate supplement or referral records. Review/refine it and retry only these records, rather than repeating the MEI harvest.

## Next steps

1. Inspect a representative sample of actual viewers for full/partial scans and copy identity.
2. Repair missing source extraction and retain clear failure states.
3. Consolidate safe display labels: copy-linked digitisation, edition-level digitisation, provenance images, other resources. No inferred transfer of shelfmarks.
4. Integrate reviewed links in copy detail, then perform website tests.

Pending separate UI decision: next frontend update should fix the heat radius at 200 km and remove its slider. No frontend change is included in this checkpoint.
