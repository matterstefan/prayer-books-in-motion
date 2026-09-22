#!/usr/bin/env python3
"""Build the combined prayer-book corpus and its GW–ISTC link table.

The script uses only Python's standard library. Source CSV files remain
unchanged; generated files are written to data/derived/.
"""

from __future__ import annotations

import csv
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIRECTORY = REPOSITORY_ROOT / "data" / "corpus"
DERIVED_DIRECTORY = REPOSITORY_ROOT / "data" / "derived"

SOURCE_FILES = (
    "horae-gw-corpus.csv",
    "supplementary-gw-corpus.csv",
)

SOURCE_COLUMNS = (
    "gw_id",
    "gw_title",
    "gw_heading",
    "print_place_gw",
    "year_from",
    "year_to",
    "language_statement_gw_title",
    "istc_id",
    "gw_url",
    "istc_url",
    "technical_note",
)

COMBINED_COLUMNS = (*SOURCE_COLUMNS, "corpus_file")
LINK_COLUMNS = ("gw_id", "istc_id", "corpus_file", "gw_url", "istc_url")


def read_source(filename: str) -> list[dict[str, str]]:
    """Read and validate one source table."""
    path = CORPUS_DIRECTORY / filename
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != SOURCE_COLUMNS:
            raise ValueError(
                f"Unexpected columns in {path}: {reader.fieldnames!r}; "
                f"expected {list(SOURCE_COLUMNS)!r}"
            )

        rows: list[dict[str, str]] = []
        for line_number, row in enumerate(reader, start=2):
            cleaned = {column: (row[column] or "").strip() for column in SOURCE_COLUMNS}
            if not cleaned["gw_id"]:
                raise ValueError(f"Missing gw_id in {path}, line {line_number}")
            cleaned["corpus_file"] = filename
            rows.append(cleaned)
        return rows


def split_istc_ids(value: str) -> list[str]:
    """Return the semicolon-separated ISTC identifiers in one GW row."""
    return [identifier.strip() for identifier in value.split(";") if identifier.strip()]


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    """Write a stable UTF-8 CSV file with Unix line endings."""
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    combined_rows: list[dict[str, str]] = []
    for filename in SOURCE_FILES:
        combined_rows.extend(read_source(filename))

    seen_gw_ids: set[str] = set()
    for row in combined_rows:
        gw_id = row["gw_id"]
        if gw_id in seen_gw_ids:
            raise ValueError(f"Duplicate GW identifier across source files: {gw_id}")
        seen_gw_ids.add(gw_id)

    combined_rows.sort(key=lambda row: row["gw_id"].casefold())

    link_rows: list[dict[str, str]] = []
    seen_links: set[tuple[str, str]] = set()
    for row in combined_rows:
        for istc_id in split_istc_ids(row["istc_id"]):
            link = (row["gw_id"], istc_id)
            if link in seen_links:
                raise ValueError(f"Duplicate GW–ISTC relationship: {link}")
            seen_links.add(link)
            link_rows.append(
                {
                    "gw_id": row["gw_id"],
                    "istc_id": istc_id,
                    "corpus_file": row["corpus_file"],
                    "gw_url": row["gw_url"],
                    "istc_url": f"https://data.cerl.org/istc/{istc_id}",
                }
            )

    DERIVED_DIRECTORY.mkdir(parents=True, exist_ok=True)
    write_csv(
        DERIVED_DIRECTORY / "prayer-book-corpus.csv",
        COMBINED_COLUMNS,
        combined_rows,
    )
    write_csv(
        DERIVED_DIRECTORY / "gw-istc-links.csv",
        LINK_COLUMNS,
        link_rows,
    )

    distinct_istc_ids = {row["istc_id"] for row in link_rows}
    print(f"GW records: {len(combined_rows)}")
    print(f"GW–ISTC relationships: {len(link_rows)}")
    print(f"Distinct ISTC identifiers: {len(distinct_istc_ids)}")


if __name__ == "__main__":
    main()
