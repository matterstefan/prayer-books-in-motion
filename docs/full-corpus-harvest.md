# Complete-corpus MEI retrieval

This extends the 60-ISTC pilot to every ISTC identifier already present in
the agreed GW source tables. It adds no new scholarly categories or catalogue
records. Original titles, identifiers, dates and uncertainty remain unchanged.

## Scope checked on 26 September 2026

- 714 GW rows in the two source tables.
- 636 GW–ISTC relationships, representing 635 distinct ISTC identifiers.
- 86 GW rows have no ISTC link in these tables. They remain in the corpus;
  they cannot yet be queried through this particular linkage route.
- Three identifiers contain a comma suffix. They are queried exactly as
  supplied, without merging them into the unsuffixed identifier. Their results
  will need inspection; a zero result does not establish that no copy survives.

## Local use

Requires Python 3.10 or later; no third-party packages or API credentials.

```bash
python3 scripts/build_corpus.py
python3 scripts/fetch_mei_corpus.py --check
python3 scripts/fetch_mei_corpus.py --seed-pilot
```

Completed queries are saved atomically in `data/cache/mei-corpus/`, including
zero-result queries. Repeating the last command resumes missing queries.
The default interval between requests is two seconds. The pilot fetcher
handles pagination and bounded retries; three consecutive query failures stop
the corpus run. Ctrl-C compiles completed queries into an explicit partial
result. A hard process termination still leaves completed query checkpoints.

The optional `--seed-pilot` reuses the original retrieval dates from the saved
pilot. Of its 60 queries, 59 can currently be reconstructed completely. One
had unrelated full-text hits absent from the combined snapshot and therefore
must be queried again. This is a corpus expansion using a mixture of dated
responses, not a claim that every record was refreshed on the same day.

To inspect saved checkpoints without network access:

```bash
python3 scripts/fetch_mei_corpus.py --cache-only
```

For a deliberately bounded batch, add `--max-new-queries 20`. A partial run
returns exit code 2, so automation does not label it complete. Exit code 0
means every planned query has been retrieved and the result combined.

## Outputs

All new analytical outputs go to `data/expanded/`. The existing website data
remain in `data/derived/` until the expanded dataset has been reviewed and its
additional locations resolved.

- `harvest-status.json`: planned/completed queries, unresolved links, errors,
  counts of direct copies and indirect records, and a completion flag.
- `mei-corpus.json`: full source snapshot, only produced by a complete run.
- `mei-corpus-partial.json`: explicitly incomplete snapshot, when applicable.
- `tables/`: four CSV tables from a complete snapshot.
- `partial-tables/`: corresponding tables for an incomplete snapshot.

Direct and bound-with relationships remain distinct. Indirect records are
retained without automatically transferring their provenance to other
components. Query checkpoints preserve all returned search rows, including
unrelated hits that are excluded from the analytical snapshot.

If the same MEI ID occurs with different content in two query responses,
combination stops and records a `combine_error`; it does not silently choose
one version. The raw responses remain available for inspection. Existing
complete output files are not removed by a later partial run: always consult
the current `harvest-status.json` rather than treating an older file as new.

For an intentional fresh retrieval, use new cache and output directories and
omit `--seed-pilot`. Preserve the previous results for comparison.

## Run on GitHub

The file `.github/workflows/harvest-mei.yml` defines a manually triggered
workflow called **Harvest MEI corpus**. It must be committed to the default
branch before it appears in the Actions tab.

1. Open the repository's **Actions** tab.
2. Choose **Harvest MEI corpus**.
3. Choose **Run workflow**, select the default branch, and confirm.
4. Open the run to see its progress.
5. Download **mei-corpus-results** from the run's **Artifacts** section.

The workflow uses GitHub's hosted Linux runner and its installed Python. It
has read-only repository permissions and does not commit, publish or deploy
the resulting data. It prevents overlapping harvests and reuses checkpoints
from preceding runs. It also attempts to save checkpoints and outputs after
a failed/partial run. Download the artifact even if the run is red: the
status file explains whether it is partial or has a processing error.

The artifact includes `expanded/`, `cache/mei-corpus/`, and the source-derived
corpus/link tables under `derived/`. Artifact retention is set to 90 days;
download it for long-term preservation. GitHub's cache is temporary and is
not an archive. A cancelled job or platform outage may prevent upload;
resume from the latest available checkpoint.

This workflow is for continuing the initial harvest. A later deliberate
refresh requires a new cache generation and no pilot seeding.

## Validation and current limit

Local checks exercise existing pilot responses, continuation, incomplete
outputs and the direct/bound-with distinction. On 26 September the direct
CERL connection from the development environment timed out; no new MEI
records were obtained in that preparation step. GitHub execution remains to
be tested. Geographic resolution and publication of the expanded corpus are
subsequent steps.

References:
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://github.com/actions/cache
- https://github.com/actions/upload-artifact
