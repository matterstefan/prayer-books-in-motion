# Supplement GW and ISTC digital links

Upload this package into the repository, preserving directories. It includes the earlier digital-review checkpoint, so that ZIP need not be uploaded separately. No frontend files are changed.

In GitHub Actions select **Supplement GW and ISTC digital links**, then **Run workflow** on main. The workflow uses the existing CERL_USER_AGENT repository secret without printing its value. Requests are sequential, at least two seconds apart; the concurrency group prevents overlap with the existing harvest jobs. No MEI queries run.

The plan lists all 87 failed GW references and all 2,375 selected ISTC identifiers. GW parsing accepts genuine supplement pages whose formatting differs from main entries, and follows explicit GW HTML refresh referrals within the catalogue. Original and resolved source URLs remain separate. Some original GW records have no ISTC identifier: retain them under their GW source URL, do not invent a match.

ISTC uses full public record HTML, rather than search-result JSON. Because the protected live endpoint cannot be tested without the GitHub secret here, the parser validates the returned page and stops after three successive ISTC errors. All external anchors are retained with labels and preceding text; only explicit digital/facsimile labels are flagged as digitisation candidates. Others require review and must not automatically become website digitisation links. These are edition references, never automatically assigned to specific copies. HTML extraction is not proof of complete coverage of dynamically generated links.

Completed records are saved individually and cached. A rerun skips them and retries failures. Timeout/interruption writes the aggregate results in a finally block; cache/artifact steps run even after failure. The six-hour job limit permits a substantially longer run than the original 80-minute cap. Actual duration depends on catalogue response times. Download the artifact **prayer-books-digital-supplement** and return it for consolidation with existing candidates. The script does not alter digital-link-candidates.json or the live map.

A red job may still have useful results: errors and summary remain in the artifact. In particular, obsolete GW URLs may still return 404; those should not be hidden as successful empty records. No repeated full MEI harvest is needed.

Validation: four parser tests, including actual GWXI427A and M12471 HTML retrieved on this work session, supplement acceptance, redirect recognition, challenge rejection, and conservative external-link classification. Live ISTC validation awaits this authorized workflow.
