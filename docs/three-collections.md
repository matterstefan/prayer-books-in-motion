# Three collections: decision and retrieval, 9 October 2026

## Selection

1. **GW (Horae and selected editions)**: the union of both existing GW source
   tables, including the feedback additions. This is the default active set.
2. **Additional liturgical editions — MEI**: editions with `liturgy` in
   `hostItem.subject`, excluding every core ISTC identifier.
3. **Additional devotional literature — MEI**: editions with
   `literature-devotional` in `hostItem.subject` OR `hostItem.keywords`, excluding
   every core ISTC identifier.

The supplements may overlap. Copies are deduplicated by MEI ID. Switching off
the core must not make its editions reappear through a supplement. Membership
is recalculated after core changes. These are source-based selection rules,
not newly assigned genres or claims about liturgy and para-liturgy.

The explanation of MEI coverage belongs in **About the project**, not a warning
on the map: an edition can belong to the selection without a surviving copy
being represented in MEI. The supplements alone are not complete subject searches,
because core editions have been subtracted.

## Feedback additions

- Salicetus: all 29 Antidotarius/Antidotarium entries in GW article SALINIC.
- Petrarca: nine entries headed Psalmi poenitentiales in article PETRFRA;
  general collected works containing the text are not added automatically.
- Fridolin: Schatzbehalter, GW 10329 / ISTC is00306000.

39 GW entries provide 30 distinct ISTC identifiers. GW entries without an ISTC
link remain in the selection, and GW post-1500 reattributions are not removed.
Source HTML snapshots are retained under data/sources/gw-additions-20261009.
The GW year 1404 corrected to 1494 in M39512 is represented as 1494;
M39491's 1500/01 dating is represented as 1500–1501. Original headings remain.

## Feedback items already represented at edition level

- Augsburg 1492, Cursus hinc inde collecti: GW 12947 / ic00992000.
- Urach around 1482, Die sieben Zeiten: GW 12996 / ih00433350.
- Valencia 1486: GW 13442 / ih00357880.
- Zaragoza 1500, Coci and partners: GW 13446 / ih00406500.

These matches do not establish an MEI record for the Hungarian or Madrid copy.
The 8-leaf De septem horis item and the three Paris links still require exact
edition identification; no new rows have been invented for them. The Cologne
1518 suggestion is excluded according to Stefan's explicit decision.

## Retrieval

Run **Harvest three collections and digital links** manually in GitHub Actions.
It reads the existing CERL_USER_AGENT secret and uses a shared two-second delay.
The workflow shares a concurrency group with the other harvest workflows.
Completed queries are cached. It writes to data/collections and a new cache,
and does not deploy or overwrite live expanded tables.

The downloadable artifact is **prayer-books-three-collections**. Its membership
file, raw MEI snapshot and digital-link candidates are the input to the next
integration step. Raw MEI query caches preserve bound-with relationships;
only direct records become displayed copies, following the existing model.

Digital link candidates retain MEI copy IDs where explicitly supplied. GW and
ISTC edition-level links are not assigned to a specific MEI copy. They require
inspection before being labelled as full digitizations. MEI image links and
unclassified ISTC links can include partial images or catalogue pages.
GW extraction currently selects anchors explicitly labelled Digitalisat;
it does not claim to discover every external digitization on the web.

Inspect harvest-status.json even after downloading an artifact. A failed run
can contain useful completed MEI data and checkpoints, but incomplete link
retrieval. Only completed queries are cached; another run resumes these.

## Remaining integration after retrieval

Build new station tables and assess unresolved locations; preserve existing
place-review decisions. Add three checkboxes, counts and About text, then test
deduplication and performance with actual data. Inspect digital-link candidates
and distinguish copy-level scans from other-copy and partial-image links.

Owner-context filters, English place-name aliases and region filters remain
future suggestions, not commitments for this update.
