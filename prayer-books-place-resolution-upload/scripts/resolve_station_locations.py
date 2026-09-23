#!/usr/bin/env python3
"""Apply the curated place-authority crosswalk to itinerary stations."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "derived" / "mei-itinerary-stations.csv"
MAPPING_PATH = ROOT / "data" / "authority" / "place-authorities.csv"
OUTPUT_PATH = ROOT / "data" / "derived" / "mei-itinerary-stations-resolved.csv"

ADDED_COLUMNS = (
    "location_mapping_id",
    "resolved_country_code",
    "place_wikidata_id",
    "institution_wikidata_id",
    "location_resolution_method",
    "location_resolution_note",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def station_key(row: dict[str, str]) -> tuple[str, str] | None:
    if row["station_type"] == "print_place":
        return "print_place", row["place_name"]
    if row["station_type"] == "current_holding":
        return "current_holding", row["institution_id"]
    if row["station_type"] == "provenance_place" and not (
        row["latitude"] and row["longitude"]
    ):
        return "provenance_place", row["place_name"]
    return None


def main() -> None:
    source_columns, station_rows = read_csv(SOURCE_PATH)
    _, mapping_rows = read_csv(MAPPING_PATH)
    mappings = {
        (row["station_type"], row["source_key"]): row for row in mapping_rows
    }
    if len(mappings) != len(mapping_rows):
        raise ValueError("Duplicate station_type/source_key mapping found")

    applied = Counter()
    output: list[dict[str, str]] = []
    for original in station_rows:
        row = dict(original)
        for column in ADDED_COLUMNS:
            row[column] = ""

        key = station_key(row)
        if key is not None:
            if key not in mappings:
                raise ValueError(f"No location mapping found for {key}")
            mapping = mappings[key]
            applied[mapping["mapping_id"]] += 1

            row["location_mapping_id"] = mapping["mapping_id"]
            row["resolved_country_code"] = mapping["country_code"]
            row["place_wikidata_id"] = mapping["place_wikidata_id"]
            row["institution_wikidata_id"] = mapping["institution_wikidata_id"]
            row["location_resolution_method"] = mapping["resolution_method"]
            row["location_resolution_note"] = mapping["resolution_note"]

            if mapping["resolution_status"] == "resolved":
                row["place_name"] = mapping["resolved_name"]
                row["preferred_placename"] = mapping["resolved_name"]
                row["place_authority"] = mapping["place_authority"]
                row["place_authority_id"] = mapping["place_authority_id"]
                row["place_authority_url"] = mapping["place_authority_url"]
                row["latitude"] = mapping["latitude"]
                row["longitude"] = mapping["longitude"]
                row["location_resolution_status"] = "coordinates_resolved"
            else:
                row["location_resolution_status"] = mapping["resolution_status"]

        output.append(row)

    for mapping in mapping_rows:
        expected = int(mapping["affected_station_count"])
        actual = applied[mapping["mapping_id"]]
        if expected != actual:
            raise ValueError(
                f"Mapping {mapping['mapping_id']} expected {expected} rows but applied to {actual}"
            )

    write_csv(OUTPUT_PATH, source_columns + list(ADDED_COLUMNS), output)
    point_count = sum(bool(row["latitude"] and row["longitude"]) for row in output)
    statuses = Counter(row["location_resolution_status"] for row in output)
    print(
        f"Wrote {OUTPUT_PATH}: {point_count}/{len(output)} stations have point coordinates; "
        f"statuses={dict(statuses)}"
    )


if __name__ == "__main__":
    main()
