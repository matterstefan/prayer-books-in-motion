#!/usr/bin/env python3
"""Build the evidence-level station table used by the itinerary visualisation.

Only direct MEI copy records receive itineraries. Each itinerary has a printing
place as its first station, zero or more place occurrences from MEI provenance
blocks, and the present holding institution as its final observed station.

The table records evidence. It does not fill chronological gaps or assert that
the straight lines drawn between known locations reproduce an actual journey.
Those display rules belong to the visualisation layer.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT_PATH = REPOSITORY_ROOT / "data" / "sample" / "mei-pilot-istc.csv"
DEFAULT_DERIVED_DIRECTORY = REPOSITORY_ROOT / "data" / "derived"
DEFAULT_OUTPUT_PATH = DEFAULT_DERIVED_DIRECTORY / "mei-itinerary-stations.csv"

STATION_COLUMNS = (
    "station_id",
    "mei_id",
    "copy_id",
    "requested_istc_id",
    "host_istc_id",
    "station_type",
    "station_role",
    "source_order",
    "place_order_within_source",
    "provenance_id",
    "place_occurrence_id",
    "location_label",
    "place_name",
    "preferred_placename",
    "place_authority",
    "place_authority_id",
    "place_authority_url",
    "latitude",
    "longitude",
    "country",
    "institution_id",
    "institution_name",
    "shelfmark",
    "time_start",
    "time_end",
    "centuries",
    "observation_date",
    "date_status",
    "certainty",
    "location_resolution_status",
    "evidence_status",
    "source_catalogue",
    "source_record_id",
    "source_url",
    "source_snapshot",
    "note",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=STATION_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def gw_urls(gw_ids: str) -> str:
    return " | ".join(
        f"https://gesamtkatalogderwiegendrucke.de/docs/GW{gw_id}.htm"
        for gw_id in split_values(gw_ids)
    )


def latest_observation_date(value: str) -> str:
    dates = sorted(item[:10] for item in split_values(value) if len(item) >= 10)
    return dates[-1] if dates else ""


def provenance_date_status(row: dict[str, str]) -> str:
    if row["time_start"] or row["time_end"]:
        return "mei_timeperiod"
    if row["centuries"]:
        return "mei_century_only"
    if row["evidence_date"]:
        return "mei_evidence_date_only"
    return "undated"


def place_resolution_status(row: dict[str, str]) -> str:
    if row["latitude"] and row["longitude"]:
        return "coordinates_supplied"
    if row["geonames_id"]:
        return "authority_without_coordinates"
    return "name_only"


def build_rows(
    pilot_rows: list[dict[str, str]],
    copy_rows: list[dict[str, str]],
    provenance_rows: list[dict[str, str]],
    place_rows: list[dict[str, str]],
    link_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    direct_links = [row for row in link_rows if row["relation_type"] == "direct"]
    link_counts = Counter(row["mei_id"] for row in direct_links)
    duplicate_links = sorted(mei_id for mei_id, count in link_counts.items() if count != 1)
    if duplicate_links:
        raise ValueError(f"Expected one direct relationship per MEI record: {duplicate_links}")

    pilot_by_istc = {row["istc_id"]: row for row in pilot_rows}
    copies_by_mei = {row["mei_id"]: row for row in copy_rows}
    provenance_by_id = {row["provenance_id"]: row for row in provenance_rows}
    places_by_mei: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in place_rows:
        places_by_mei[row["mei_id"]].append(row)

    relationship_number = {
        row["relationship_id"]: index for index, row in enumerate(direct_links, start=1)
    }
    output: list[dict[str, str]] = []

    for link in sorted(
        direct_links, key=lambda row: relationship_number[row["relationship_id"]]
    ):
        mei_id = link["mei_id"]
        istc_id = link["requested_istc_id"]
        if istc_id not in pilot_by_istc:
            raise ValueError(f"No pilot row found for {istc_id}")
        if mei_id not in copies_by_mei:
            raise ValueError(f"No copy row found for {mei_id}")

        pilot = pilot_by_istc[istc_id]
        copy = copies_by_mei[mei_id]
        print_date_status = (
            "gw_extracted_year_range"
            if pilot["year_from"] or pilot["year_to"]
            else "gw_date_not_yet_extracted"
        )

        output.append(
            {
                "station_id": f"{mei_id}-print",
                "mei_id": mei_id,
                "copy_id": copy["copy_id"],
                "requested_istc_id": istc_id,
                "host_istc_id": copy["host_istc_id"],
                "station_type": "print_place",
                "station_role": "first",
                "source_order": "0",
                "place_order_within_source": "1",
                "provenance_id": "",
                "place_occurrence_id": "",
                "location_label": pilot["print_places_gw"],
                "place_name": pilot["print_places_gw"],
                "preferred_placename": "",
                "place_authority": "",
                "place_authority_id": "",
                "place_authority_url": "",
                "latitude": "",
                "longitude": "",
                "country": "",
                "institution_id": "",
                "institution_name": "",
                "shelfmark": copy["shelfmark"],
                "time_start": pilot["year_from"],
                "time_end": pilot["year_to"],
                "centuries": "",
                "observation_date": "",
                "date_status": print_date_status,
                "certainty": "",
                "location_resolution_status": "place_name_not_yet_geocoded",
                "evidence_status": "edition_level_print_statement",
                "source_catalogue": "GW",
                "source_record_id": pilot["gw_ids"],
                "source_url": gw_urls(pilot["gw_ids"]),
                "source_snapshot": f"data/corpus/{pilot['corpus_file']}",
                "note": "Printing statement shared by copies of the edition.",
            }
        )

        copy_places = sorted(
            places_by_mei.get(mei_id, []),
            key=lambda row: (
                int(provenance_by_id[row["provenance_id"]]["provenance_sequence"]),
                int(row["place_sequence"]),
                row["place_occurrence_id"],
            ),
        )
        for place in copy_places:
            provenance = provenance_by_id[place["provenance_id"]]
            label = place["preferred_placename"] or place["name"]
            output.append(
                {
                    "station_id": place["place_occurrence_id"],
                    "mei_id": mei_id,
                    "copy_id": copy["copy_id"],
                    "requested_istc_id": istc_id,
                    "host_istc_id": copy["host_istc_id"],
                    "station_type": "provenance_place",
                    "station_role": "intermediate",
                    "source_order": provenance["provenance_sequence"],
                    "place_order_within_source": place["place_sequence"],
                    "provenance_id": place["provenance_id"],
                    "place_occurrence_id": place["place_occurrence_id"],
                    "location_label": label,
                    "place_name": place["name"],
                    "preferred_placename": place["preferred_placename"],
                    "place_authority": "GeoNames" if place["geonames_id"] else "",
                    "place_authority_id": place["geonames_id"],
                    "place_authority_url": place["geonames_url"],
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "country": place["country"],
                    "institution_id": "",
                    "institution_name": "",
                    "shelfmark": copy["shelfmark"],
                    "time_start": provenance["time_start"],
                    "time_end": provenance["time_end"],
                    "centuries": provenance["centuries"],
                    "observation_date": provenance["evidence_date"],
                    "date_status": provenance_date_status(provenance),
                    "certainty": provenance["certainty"],
                    "location_resolution_status": place_resolution_status(place),
                    "evidence_status": "copy_level_provenance_place",
                    "source_catalogue": "MEI",
                    "source_record_id": place["provenance_id"],
                    "source_url": copy["mei_url"],
                    "source_snapshot": copy["source_snapshot"],
                    "note": place["place_note"],
                }
            )

        output.append(
            {
                "station_id": f"{mei_id}-current",
                "mei_id": mei_id,
                "copy_id": copy["copy_id"],
                "requested_istc_id": istc_id,
                "host_istc_id": copy["host_istc_id"],
                "station_type": "current_holding",
                "station_role": "last",
                "source_order": str(
                    max(
                        (
                            int(provenance_by_id[row["provenance_id"]]["provenance_sequence"])
                            for row in copy_places
                        ),
                        default=0,
                    )
                    + 1
                ),
                "place_order_within_source": "1",
                "provenance_id": "",
                "place_occurrence_id": "",
                "location_label": copy["holding_institution_name"],
                "place_name": "",
                "preferred_placename": "",
                "place_authority": "",
                "place_authority_id": "",
                "place_authority_url": "",
                "latitude": "",
                "longitude": "",
                "country": copy["holding_country_code"],
                "institution_id": copy["holding_institution_id"],
                "institution_name": copy["holding_institution_name"],
                "shelfmark": copy["shelfmark"],
                "time_start": "",
                "time_end": "",
                "centuries": "",
                "observation_date": latest_observation_date(copy["source_retrieved_at"]),
                "date_status": "current_observation_only",
                "certainty": "",
                "location_resolution_status": "holding_institution_not_yet_geocoded",
                "evidence_status": "current_holding_statement",
                "source_catalogue": "MEI",
                "source_record_id": mei_id,
                "source_url": copy["mei_url"],
                "source_snapshot": copy["source_snapshot"],
                "note": "Observed as the current holding institution; no arrival date is inferred.",
            }
        )

    return output


def validate_rows(rows: list[dict[str, str]], expected_place_ids: set[str]) -> None:
    station_ids = [row["station_id"] for row in rows]
    if len(station_ids) != len(set(station_ids)):
        raise ValueError("Duplicate station_id values found")

    rows_by_mei: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        rows_by_mei[row["mei_id"]].append(row)

    for mei_id, copy_stations in rows_by_mei.items():
        counts = Counter(row["station_type"] for row in copy_stations)
        if counts["print_place"] != 1 or counts["current_holding"] != 1:
            raise ValueError(
                f"Expected one print and one current station for {mei_id}: {counts}"
            )

    generated_place_ids = {
        row["place_occurrence_id"]
        for row in rows
        if row["station_type"] == "provenance_place"
    }
    if generated_place_ids != expected_place_ids:
        missing = sorted(expected_place_ids - generated_place_ids)
        additional = sorted(generated_place_ids - expected_place_ids)
        raise ValueError(
            f"Provenance-place mismatch; missing={missing}, additional={additional}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT_PATH)
    parser.add_argument("--derived-dir", type=Path, default=DEFAULT_DERIVED_DIRECTORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    pilot_rows = read_csv(args.pilot)
    copy_rows = read_csv(args.derived_dir / "mei-copies.csv")
    provenance_rows = read_csv(args.derived_dir / "mei-provenance.csv")
    place_rows = read_csv(args.derived_dir / "mei-places.csv")
    link_rows = read_csv(args.derived_dir / "mei-record-links.csv")
    rows = build_rows(
        pilot_rows, copy_rows, provenance_rows, place_rows, link_rows
    )
    direct_mei_ids = {
        row["mei_id"] for row in link_rows if row["relation_type"] == "direct"
    }
    validate_rows(
        rows,
        {
            row["place_occurrence_id"]
            for row in place_rows
            if row["mei_id"] in direct_mei_ids
        },
    )
    write_csv(args.output, rows)

    counts = Counter(row["station_type"] for row in rows)
    direct_copies = len({row["mei_id"] for row in rows})
    print(
        f"Wrote {args.output}: {len(rows)} stations for {direct_copies} direct copies "
        f"({counts['print_place']} print, {counts['provenance_place']} provenance, "
        f"{counts['current_holding']} current)."
    )


if __name__ == "__main__":
    main()
