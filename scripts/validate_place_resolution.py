#!/usr/bin/env python3
"""Validate the curated place crosswalk and the resolved itinerary table."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "data" / "authority" / "place-authorities.csv"
STATIONS_PATH = ROOT / "data" / "derived" / "mei-itinerary-stations-resolved.csv"

REQUIRED_RESOLVED_FIELDS = (
    "resolved_name",
    "country_code",
    "place_authority",
    "place_authority_id",
    "place_authority_url",
    "latitude",
    "longitude",
)

COUNTRY_CODES = {
    "France": "FR",
    "Italy": "IT",
    "United Kingdom": "GB",
    "United States": "US",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def validate_coordinates(label: str, latitude: str, longitude: str) -> None:
    try:
        lat = float(latitude)
        lon = float(longitude)
    except ValueError as error:
        raise ValueError(f"{label}: non-numeric coordinates") from error
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError(f"{label}: coordinates outside WGS84 ranges")


def main() -> None:
    mappings = read_csv(MAPPING_PATH)
    stations = read_csv(STATIONS_PATH)

    mapping_ids = [row["mapping_id"] for row in mappings]
    if len(mapping_ids) != len(set(mapping_ids)):
        raise ValueError("Duplicate mapping_id in place-authorities.csv")
    mappings_by_id = {row["mapping_id"]: row for row in mappings}

    mapping_keys: set[tuple[str, str, str, str]] = set()
    for mapping in mappings:
        context_field = (mapping.get("match_context_field") or "").strip()
        context_key = (mapping.get("match_context_key") or "").strip()
        if bool(context_field) != bool(context_key):
            raise ValueError(
                f"{mapping['mapping_id']}: incomplete context-specific match"
            )
        apply_existing = (mapping.get("apply_to_existing_coordinates") or "").strip()
        if apply_existing not in ("", "true"):
            raise ValueError(
                f"{mapping['mapping_id']}: apply_to_existing_coordinates must be blank or true"
            )
        key = (
            mapping["station_type"],
            mapping["source_key"],
            context_field,
            context_key,
        )
        if key in mapping_keys:
            raise ValueError(f"Duplicate mapping key: {key}")
        mapping_keys.add(key)

        has_point = bool(mapping["latitude"] and mapping["longitude"])
        if mapping["resolution_status"] == "resolved":
            missing = [field for field in REQUIRED_RESOLVED_FIELDS if not mapping[field]]
            if missing:
                raise ValueError(
                    f"{mapping['mapping_id']}: resolved mapping lacks {', '.join(missing)}"
                )
            validate_coordinates(
                mapping["mapping_id"], mapping["latitude"], mapping["longitude"]
            )
        elif has_point:
            raise ValueError(
                f"{mapping['mapping_id']}: unresolved mapping must not have a point"
            )

    station_ids = [row["station_id"] for row in stations]
    if len(station_ids) != len(set(station_ids)):
        raise ValueError("Duplicate station_id in resolved itinerary table")

    applied: Counter[str] = Counter()
    locations: dict[tuple[str, str], set[tuple[str, str, str]]] = defaultdict(set)
    point_count = 0
    for station in stations:
        latitude = station["latitude"]
        longitude = station["longitude"]
        if bool(latitude) != bool(longitude):
            raise ValueError(f"{station['station_id']}: incomplete coordinate pair")
        if latitude:
            validate_coordinates(station["station_id"], latitude, longitude)
            point_count += 1
            preferred_name = station["preferred_placename"]
            authority_id = station["place_authority_id"]
            if preferred_name and authority_id:
                country = station["resolved_country_code"] or COUNTRY_CODES.get(
                    station["country"], station["country"]
                )
                locations[(preferred_name, country)].add(
                    (authority_id, latitude, longitude)
                )

        mapping_id = station["location_mapping_id"]
        if mapping_id:
            if mapping_id not in mappings_by_id:
                raise ValueError(f"{station['station_id']}: unknown mapping {mapping_id}")
            applied[mapping_id] += 1

    for mapping in mappings:
        expected = int(mapping["affected_station_count"])
        actual = applied[mapping["mapping_id"]]
        if expected != actual:
            raise ValueError(
                f"{mapping['mapping_id']}: expected {expected} applications, found {actual}"
            )

    inconsistent = {
        name: values for name, values in locations.items() if len(values) > 1
    }
    if inconsistent:
        raise ValueError(f"Inconsistent authority points for place names: {inconsistent}")

    statuses = Counter(row["location_resolution_status"] for row in stations)
    print(
        f"Validated {len(mappings)} mappings and {len(stations)} stations; "
        f"{point_count} stations have coordinates; statuses={dict(statuses)}"
    )


if __name__ == "__main__":
    main()
