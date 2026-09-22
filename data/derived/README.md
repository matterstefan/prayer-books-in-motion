# Derived data

The files in this directory are generated from the source tables in
`data/corpus/`. They should not be edited manually.

Run the build from the repository root:

```bash
python3 scripts/build_corpus.py
```

## Files

- `prayer-book-corpus.csv`: one row per GW edition from both source tables.
  The technical field `corpus_file` records the source filename without
  introducing a new scholarly category.
- `gw-istc-links.csv`: one row per GW–ISTC relationship. The table deliberately
  does not assume a one-to-one relationship between GW and ISTC identifiers.

The generated tables preserve the catalogue titles and identifiers supplied by
GW and ISTC. No new bibliographical records or titles are created.
