#!/usr/bin/env python3
"""Select a reproducible, deliberately heterogeneous 60-ISTC MEI pilot.

The pilot is a data-model stress test, not a statistically representative
sample. It retains the six identifiers used in the first API test and balances
the remaining selection by corpus group and broad date band. Within each band,
the deterministic selection favours language and printing-place coverage.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = REPOSITORY_ROOT / "data" / "derived" / "prayer-book-corpus.csv"
LINKS_PATH = REPOSITORY_ROOT / "data" / "derived" / "gw-istc-links.csv"
OUTPUT_PATH = REPOSITORY_ROOT / "data" / "sample" / "mei-pilot-istc.csv"

EXISTING_TEST_IDS = (
    "ib00512000",
    "ib00503000",
    "ib00506000",
    "ih00370100",
    "ih00427000",
    "ih00427100",
)

# This ISTC identifier is deliberately retained because the present GW link
# table connects it with two GW identifiers.
MULTIPLE_GW_LINK_ID = "ih00373800"

SOURCE_LABELS = {
    "horae-gw-corpus.csv": "horae",
    "supplementary-gw-corpus.csv": "supplementary",
}

DATE_BAND_ORDER = (
    "through_1479",
    "1480s",
    "1490s",
    "1500_or_later",
    "unknown",
)

DATE_BAND_LABELS = {
    "through_1479": "through 1479",
    "1480s": "1480s",
    "1490s": "1490s",
    "1500_or_later": "1500 or later",
    "unknown": "date not extracted",
}

# These totals include the seven mandatory identifiers above.
TARGETS = {
    "horae-gw-corpus.csv": {
        "through_1479": 6,
        "1480s": 10,
        "1490s": 20,
        "1500_or_later": 7,
        "unknown": 2,
    },
    "supplementary-gw-corpus.csv": {
        "through_1479": 3,
        "1480s": 3,
        "1490s": 5,
        "1500_or_later": 2,
        "unknown": 2,
    },
}

OUTPUT_COLUMNS = (
    "sample_order",
    "istc_id",
    "gw_ids",
    "corpus_group",
    "corpus_file",
    "gw_titles",
    "print_places_gw",
    "year_from",
    "year_to",
    "date_band",
    "language_statements_gw",
    "istc_url",
    "selection_note",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def split_istc_ids(value: str) -> list[str]:
    return [identifier.strip() for identifier in value.split(";") if identifier.strip()]


def unique_join(values: list[str]) -> str:
    return " | ".join(dict.fromkeys(value.strip() for value in values if value.strip()))


def date_band(year_value: str) -> str:
    if not year_value.isdigit():
        return "unknown"
    year = int(year_value)
    if year <= 1479:
        return "through_1479"
    if year <= 1489:
        return "1480s"
    if year <= 1499:
        return "1490s"
    return "1500_or_later"


def stable_hash(identifier: str) -> str:
    return hashlib.sha256(f"CA23143:{identifier}".encode()).hexdigest()


def build_candidates() -> dict[str, dict[str, Any]]:
    corpus_rows = read_csv(CORPUS_PATH)
    link_rows = read_csv(LINKS_PATH)
    corpus_by_key = {
        (row["gw_id"], row["corpus_file"]): row for row in corpus_rows
    }

    grouped_links: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in link_rows:
        grouped_links[row["istc_id"]].append(row)

    candidates: dict[str, dict[str, Any]] = {}
    for istc_id, links in grouped_links.items():
        rows = [
            corpus_by_key[(link["gw_id"], link["corpus_file"])] for link in links
        ]
        corpus_files = {row["corpus_file"] for row in rows}
        if len(corpus_files) != 1:
            raise ValueError(
                f"ISTC identifier {istc_id} occurs in multiple corpus groups: "
                f"{sorted(corpus_files)}"
            )
        corpus_file = next(iter(corpus_files))
        years_from = [row["year_from"] for row in rows if row["year_from"].isdigit()]
        years_to = [row["year_to"] for row in rows if row["year_to"].isdigit()]
        representative_year = min(years_from) if years_from else ""
        candidates[istc_id] = {
            "istc_id": istc_id,
            "gw_ids": unique_join([row["gw_id"] for row in rows]),
            "corpus_group": SOURCE_LABELS[corpus_file],
            "corpus_file": corpus_file,
            "gw_titles": unique_join([row["gw_title"] for row in rows]),
            "print_places_gw": unique_join([row["print_place_gw"] for row in rows]),
            "year_from": min(years_from) if years_from else "",
            "year_to": max(years_to) if years_to else "",
            "date_band": date_band(representative_year),
            "language_statements_gw": unique_join(
                [row["language_statement_gw_title"] for row in rows]
            ),
            "istc_url": f"https://data.cerl.org/istc/{istc_id}",
            "gw_link_count": len(links),
        }
    return candidates


def select_candidates(candidates: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    mandatory_ids = (*EXISTING_TEST_IDS, MULTIPLE_GW_LINK_ID)
    missing = [identifier for identifier in mandatory_ids if identifier not in candidates]
    if missing:
        raise ValueError(f"Mandatory pilot identifiers missing from corpus: {missing}")

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    selected_places: Counter[str] = Counter()
    selected_languages: set[str] = set()

    def add(candidate: dict[str, Any], note: str) -> None:
        if candidate["istc_id"] in selected_ids:
            return
        row = dict(candidate)
        row["selection_note"] = note
        selected.append(row)
        selected_ids.add(row["istc_id"])
        selected_places[row["print_places_gw"] or "[not extracted]"] += 1
        if row["language_statements_gw"]:
            selected_languages.add(row["language_statements_gw"])

    for identifier in EXISTING_TEST_IDS:
        add(candidates[identifier], "Retained from the initial six-ISTC API test")
    add(
        candidates[MULTIPLE_GW_LINK_ID],
        "Retained to test one ISTC identifier linked to multiple GW records",
    )

    place_frequencies: Counter[tuple[str, str]] = Counter(
        (candidate["corpus_file"], candidate["print_places_gw"] or "[not extracted]")
        for candidate in candidates.values()
    )

    for corpus_file, band_targets in TARGETS.items():
        for band in DATE_BAND_ORDER:
            target = band_targets[band]
            already_selected = sum(
                row["corpus_file"] == corpus_file and row["date_band"] == band
                for row in selected
            )
            needed = target - already_selected
            if needed < 0:
                raise ValueError(
                    f"Mandatory identifiers exceed target for {corpus_file}, {band}"
                )

            pool = [
                candidate
                for candidate in candidates.values()
                if candidate["corpus_file"] == corpus_file
                and candidate["date_band"] == band
                and candidate["istc_id"] not in selected_ids
            ]

            for _ in range(needed):
                if not pool:
                    raise ValueError(f"Insufficient candidates for {corpus_file}, {band}")

                def priority(candidate: dict[str, Any]) -> tuple[Any, ...]:
                    place = candidate["print_places_gw"] or "[not extracted]"
                    language = candidate["language_statements_gw"]
                    new_explicit_language = bool(language) and language not in selected_languages
                    return (
                        0 if new_explicit_language else 1,
                        selected_places[place],
                        -place_frequencies[(corpus_file, place)],
                        stable_hash(candidate["istc_id"]),
                    )

                chosen = min(pool, key=priority)
                language_note = (
                    chosen["language_statements_gw"]
                    if chosen["language_statements_gw"]
                    else "language not stated in extracted GW title"
                )
                place_note = chosen["print_places_gw"] or "printing place not extracted"
                add(
                    chosen,
                    "Stratified pilot selection: "
                    f"{DATE_BAND_LABELS[band]}; {place_note}; {language_note}",
                )
                pool.remove(chosen)

    if len(selected) != 60:
        raise ValueError(f"Pilot must contain 60 ISTC identifiers, found {len(selected)}")

    source_counts = Counter(row["corpus_file"] for row in selected)
    expected_source_counts = {
        source: sum(bands.values()) for source, bands in TARGETS.items()
    }
    if source_counts != Counter(expected_source_counts):
        raise ValueError(
            f"Unexpected corpus-group totals: {source_counts}; "
            f"expected {expected_source_counts}"
        )

    return selected


def write_selection(rows: list[dict[str, Any]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for sample_order, row in enumerate(rows, start=1):
            writer.writerow(
                {
                    column: sample_order if column == "sample_order" else row[column]
                    for column in OUTPUT_COLUMNS
                }
            )


def main() -> None:
    candidates = build_candidates()
    selected = select_candidates(candidates)
    write_selection(selected)

    source_counts = Counter(row["corpus_group"] for row in selected)
    date_counts = Counter(row["date_band"] for row in selected)
    place_count = len(
        {row["print_places_gw"] or "[not extracted]" for row in selected}
    )
    print(f"Wrote {OUTPUT_PATH.relative_to(REPOSITORY_ROOT)}")
    print(f"ISTC identifiers: {len(selected)}")
    print(f"Corpus groups: {dict(source_counts)}")
    print(f"Date bands: {dict(date_counts)}")
    print(f"Distinct extracted printing-place values: {place_count}")


if __name__ == "__main__":
    main()
