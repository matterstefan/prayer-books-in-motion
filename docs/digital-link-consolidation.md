# Consolidated catalogue links

Run `python3 scripts/consolidate_digital_links.py` against the original candidates and the imported digital-supplement results. The script produces consolidated-links.json, digitisation-display-candidates.json and consolidation-summary.json under data/collections/digital-review.

All original references are retained alongside categories and the evidence for each classification. URL whitespace is trimmed; HTTP/HTTPS variants and different viewer URLs are not silently merged, since equivalence has not been verified. Repeated anchors are deduplicated while separate source, field and copy evidence remain distinct.

MEI electronicReproduction and GW Digitalisat are source assertions of digitisation, not proof of a complete scan. ISTC is classified using the last visible section heading in its saved preceding text, explicit facsimile labels, or the exact same URL for the same edition corroborated by MEI/GW. Missing or truncated context stays unresolved. Watermark links and provenance images remain separate. Catalogue references and repeated footer links are retained in the audit but omitted from digitisation display candidates.

Copy-level links are attached only to the MEI identifier stated in the source and only if that identifier is among visualised copies. Edition-level links stay edition-level; shared URLs do not transfer links between copies. The display-candidates file is preparation for later UI integration, not a verified whitelist of complete scans. Source text and context must be escaped when displayed in HTML.

Results: 22,874 input references; 8,031 unique trimmed URLs. Category counts overlap where distinct source references differ. 4,590 URLs have digitisation references associated with either visualised copies or identified editions. 337 visualised copies have direct references; 2,101 editions have edition-level references. These are not counts of distinct complete digitised volumes. Fifteen URLs remain unresolved from available context. Full scan verification is still zero. The five source-fetch 404s remain documented in digital-supplement/errors.

Next: inspect representative actual digital viewers and decide display labels for full/partial/unspecified resources. Integrate copy and edition links separately into the detail view. Pending frontend change: fixed 200 km heat radius with no slider. No frontend files are changed in this package.
