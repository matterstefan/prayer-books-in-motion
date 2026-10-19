# Further development

Updated 19 October 2026. The grant-funded prototype is complete and the report has been submitted. This roadmap records subsequent improvements and exploratory ideas, not commitments or outstanding grant deliverables.

## Implemented after submission: combine search results

Following feedback from Björn Klaus Buschbeck, copies can be collected across repeated searches using **Add checked matches**, then displayed together using **Show selection**. For example, users can combine Strasbourg copies of the Antidotarius animae and Hortulus animae.

The session selection uses copy identifiers, deduplicates additions and remains independent of search and collection filters. Returning to search preserves those filters. Individual copies can be removed in the selection view. Resetting filters preserves the selection; Clear selection empties it. Reloading or closing the page loses it.

Possible follow-up: persist a selection in the browser or export/import identifiers. This requires handling records missing from a later dataset and explaining storage limits.

## Possible extensions

| Idea | Purpose | Main question before implementation |
| --- | --- | --- |
| Holdings from GW and ISTC without MEI records | Show the wider distribution of surviving copies using printing and holding places | Reconcile institutional names and overlapping or multiple holdings without inventing unique copy identities or intermediate provenance |
| Further corpus additions | Include relevant editions suggested by specialists | Retain catalogue titles, explicit selection criteria and traceable links to MEI; keep candidates without MEI records documented |
| More date expressions | Extract usable years from forms such as 14[74] | Preserve source wording and distinguish inferred dates, ranges and uncertainty |
| Additional digitisation references | Evaluate remaining links in Oliver Duntze's GW export | Distinguish copy-level and edition-level resources, duplicates and partial images; lower priority |
| Clearer collection membership | Explain the relationship between the core and supplementary collections | Avoid implying that the liturgical supplement contains all liturgical editions; consider overlapping facets |
| Alternative spatial displays | Experiment with tilted maps and elevated arcs | Test whether additional visual complexity improves interpretation; no implementation commitment |

## Ongoing maintenance

- Refresh catalogue exports deliberately, observing CERL's access conditions and request limit.
- Review new unresolved places and retain source values separately from display decisions.
- Maintain links, attribution, methodological explanations and a dated record of dataset changes.

Historical regions or modern countries should not silently replace locality-level evidence. Earlier discussion of country aggregation remains a methodological question, not an agreed feature.

## Priority

The session selection is the first post-grant improvement. Further work should respond to actual research use; the order of the remaining items is not a delivery schedule.
