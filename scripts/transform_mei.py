#!/usr/bin/env python3
"""Transform a saved MEI JSON snapshot into linked CSV tables.

The JSON file remains the complete source snapshot. These CSV files provide
stable, analysis-friendly views at copy, provenance-block, and place-occurrence
level. A fourth technical table preserves the distinction between direct ISTC
matches and records found through a bound-with relationship.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_PATH = REPOSITORY_ROOT / "data" / "sample" / "mei-pilot.json"
DEFAULT_DERIVED_DIRECTORY = REPOSITORY_ROOT / "data" / "derived"

COPY_COLUMNS = (
    "mei_id",
    "copy_id",
    "mei_url",
    "host_istc_id",
    "requested_istc_ids",
    "relationship_types",
    "holding_institution_id",
    "holding_institution_name",
    "holding_institution_short",
    "holding_country_code",
    "holding_collection",
    "shelfmark",
    "title",
    "author",
    "imprint",
    "imprint_country_code",
    "language",
    "format",
    "subject",
    "gw_references",
    "all_references",
    "general_notes",
    "description_language",
    "completeness",
    "copy_type",
    "copy_features",
    "other_identifier",
    "physical_description_note",
    "provenance_count",
    "bound_with_count",
    "source_snapshot",
    "source_retrieved_at",
    "source_endpoint",
)

PROVENANCE_COLUMNS = (
    "provenance_id",
    "mei_id",
    "provenance_sequence",
    "time_start",
    "time_end",
    "centuries",
    "certainty",
    "provenance_types",
    "source_codes",
    "acquisition_method",
    "note",
    "area_codes",
    "agent_count",
    "agent_names",
    "agent_owner_ids",
    "agent_roles",
    "agent_types",
    "agent_dates",
    "agent_external_ids",
    "agents_json",
    "binding_note",
    "binding_date",
    "binding_type",
    "binding_status",
    "cover_material",
    "board_material",
    "binding_height",
    "binding_width",
    "binding_depth",
    "decoration_note",
    "rubrication_note",
    "rubrication_date",
    "manuscript_note",
    "stamps_note",
    "shelfmark_evidence",
    "price_amount",
    "price_currency",
    "price_note",
    "evidence_date",
    "place_count",
    "additional_evidence_json",
)

PLACE_COLUMNS = (
    "place_occurrence_id",
    "provenance_id",
    "mei_id",
    "place_sequence",
    "name",
    "preferred_placename",
    "geonames_id",
    "geonames_url",
    "latitude",
    "longitude",
    "country",
    "variant_placenames",
    "variant_placename_count",
    "place_note",
)

RELATIONSHIP_COLUMNS = (
    "relationship_id",
    "requested_istc_id",
    "relation_type",
    "mei_id",
    "host_istc_id",
    "linked_copy_id",
    "holding_institution_id",
    "shelfmark",
)

EXPLICIT_PROVENANCE_KEYS = {
    "timeperiod",
    "certainty",
    "type",
    "source",
    "acquisitionMethod",
    "note",
    "area",
    "agent",
    "place",
    "bindingNote",
    "bindingDate",
    "bindingType",
    "bindingStatus",
    "coverMaterial",
    "boardMaterial",
    "bindingHeight",
    "bindingWidth",
    "bindingDepth",
    "decorationNote",
    "rubricationNote",
    "rubricationDate",
    "msNote",
    "stampsNote",
    "shelfmark",
    "priceAmount",
    "priceCurrency",
    "priceNote",
    "evidenceDate",
}


def text(value: Any) -> str:
    """Return a readable, stable representation for a CSV cell."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, list):
        return " | ".join(text(item) for item in value if item is not None)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def compact_json(value: Any) -> str:
    if value in (None, [], {}):
        return ""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unique_join(values: list[Any]) -> str:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        for item in value if isinstance(value, list) else [value]:
            item_text = text(item).strip()
            if item_text and item_text not in seen:
                seen.add(item_text)
                result.append(item_text)
    return " | ".join(result)


def coordinates(location: Any) -> tuple[str, str]:
    if not isinstance(location, str) or "," not in location:
        return "", ""
    latitude, longitude = location.split(",", 1)
    return latitude.strip(), longitude.strip()


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def display_path(path: Path) -> str:
    """Return a repository-relative path where possible."""
    try:
        return str(path.resolve().relative_to(REPOSITORY_ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def retrieval_times_by_mei(
    metadata: dict[str, Any], relationships: list[dict[str, Any]]
) -> dict[str, list[str]]:
    """Associate each retained record with the time of its source query."""
    query_results = metadata.get("query_results") or {}
    fallback = metadata.get("retrieved_at") or metadata.get("compiled_at")
    result: dict[str, list[str]] = defaultdict(list)
    for relationship in relationships:
        mei_id = text(relationship.get("mei_id"))
        requested_id = text(relationship.get("requested_istc_id"))
        retrieved_at = (query_results.get(requested_id) or {}).get("retrieved_at")
        retrieved_at = text(retrieved_at or fallback)
        if retrieved_at and retrieved_at not in result[mei_id]:
            result[mei_id].append(retrieved_at)
    return result


def transform(source_path: Path, derived_directory: Path) -> dict[str, int]:
    sample = json.loads(source_path.read_text(encoding="utf-8"))
    metadata = sample.get("metadata", {})
    records = sample.get("records", [])
    relationships = sample.get("relationships", [])

    if not isinstance(records, list) or not isinstance(relationships, list):
        raise ValueError("MEI snapshot must contain list-valued records and relationships")

    record_ids = [text(record.get("id")) for record in records]
    if "" in record_ids or len(record_ids) != len(set(record_ids)):
        raise ValueError("Every retained MEI record must have a unique non-empty id")

    record_id_set = set(record_ids)
    relationships_by_mei: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for relationship in relationships:
        mei_id = text(relationship.get("mei_id"))
        if mei_id not in record_id_set:
            raise ValueError(f"Relationship refers to unknown MEI record: {mei_id}")
        relationships_by_mei[mei_id].append(relationship)

    retrieval_times = retrieval_times_by_mei(metadata, relationships)
    source_snapshot = display_path(source_path)

    copy_rows: list[dict[str, Any]] = []
    provenance_rows: list[dict[str, Any]] = []
    place_rows: list[dict[str, Any]] = []

    for record in records:
        mei_id = text(record.get("id"))
        institution = record.get("holdingInstitution") or {}
        host_item = record.get("hostItem") or {}
        references = host_item.get("references") or []
        record_relationships = relationships_by_mei.get(mei_id, [])
        bound_with = record.get("boundWith") or []

        copy_rows.append(
            {
                "mei_id": mei_id,
                "copy_id": text(record.get("copyId")),
                "mei_url": f"https://data.cerl.org/mei/{mei_id}",
                "host_istc_id": text(record.get("hostItemId")),
                "requested_istc_ids": unique_join(
                    [relationship.get("requested_istc_id") for relationship in record_relationships]
                ),
                "relationship_types": unique_join(
                    [relationship.get("relation_type") for relationship in record_relationships]
                ),
                "holding_institution_id": text(record.get("holdingInstitutionId")),
                "holding_institution_name": text(institution.get("name")),
                "holding_institution_short": text(institution.get("short")),
                "holding_country_code": text(institution.get("country")),
                "holding_collection": text(record.get("holdingInstitutionCollection")),
                "shelfmark": text(record.get("shelfmark")),
                "title": text(host_item.get("title")),
                "author": text(host_item.get("author")),
                "imprint": text(host_item.get("imprint")),
                "imprint_country_code": text(host_item.get("imprint_country_code")),
                "language": text(host_item.get("language")),
                "format": text(host_item.get("format")),
                "subject": text(host_item.get("subject")),
                "gw_references": unique_join(
                    [reference for reference in references if text(reference).startswith("GW")]
                ),
                "all_references": text(references),
                "general_notes": text(record.get("generalNotes")),
                "description_language": text(record.get("descriptionLanguage")),
                "completeness": text(record.get("completeness")),
                "copy_type": text(record.get("copyType")),
                "copy_features": text(record.get("copyFeatures")),
                "other_identifier": text(record.get("otherIdentifier")),
                "physical_description_note": text(record.get("physicalDescriptionNote")),
                "provenance_count": len(record.get("provenance") or []),
                "bound_with_count": len(bound_with),
                "source_snapshot": source_snapshot,
                "source_retrieved_at": unique_join(retrieval_times.get(mei_id, [])),
                "source_endpoint": text(metadata.get("source")),
            }
        )

        for provenance_sequence, provenance in enumerate(
            record.get("provenance") or [], start=1
        ):
            provenance_id = f"{mei_id}-p{provenance_sequence:03d}"
            timeperiod = provenance.get("timeperiod") or {}
            agents = provenance.get("agent") or []
            places = provenance.get("place") or []
            areas = provenance.get("area") or []
            additional_evidence = {
                key: value
                for key, value in provenance.items()
                if key not in EXPLICIT_PROVENANCE_KEYS
            }

            provenance_rows.append(
                {
                    "provenance_id": provenance_id,
                    "mei_id": mei_id,
                    "provenance_sequence": provenance_sequence,
                    "time_start": text(timeperiod.get("start")),
                    "time_end": text(timeperiod.get("end")),
                    "centuries": text(timeperiod.get("century")),
                    "certainty": text(provenance.get("certainty")),
                    "provenance_types": text(provenance.get("type")),
                    "source_codes": text(provenance.get("source")),
                    "acquisition_method": text(provenance.get("acquisitionMethod")),
                    "note": text(provenance.get("note")),
                    "area_codes": unique_join(
                        [area.get("areaCode") for area in areas if isinstance(area, dict)]
                    ),
                    "agent_count": len(agents),
                    "agent_names": unique_join(
                        [agent.get("name") for agent in agents if isinstance(agent, dict)]
                    ),
                    "agent_owner_ids": unique_join(
                        [agent.get("ownerId") for agent in agents if isinstance(agent, dict)]
                    ),
                    "agent_roles": unique_join(
                        [agent.get("role") for agent in agents if isinstance(agent, dict)]
                    ),
                    "agent_types": unique_join(
                        [agent.get("type") for agent in agents if isinstance(agent, dict)]
                    ),
                    "agent_dates": unique_join(
                        [agent.get("dates") for agent in agents if isinstance(agent, dict)]
                    ),
                    "agent_external_ids": unique_join(
                        [agent.get("externalId") for agent in agents if isinstance(agent, dict)]
                    ),
                    "agents_json": compact_json(agents),
                    "binding_note": text(provenance.get("bindingNote")),
                    "binding_date": text(provenance.get("bindingDate")),
                    "binding_type": text(provenance.get("bindingType")),
                    "binding_status": text(provenance.get("bindingStatus")),
                    "cover_material": text(provenance.get("coverMaterial")),
                    "board_material": text(provenance.get("boardMaterial")),
                    "binding_height": text(provenance.get("bindingHeight")),
                    "binding_width": text(provenance.get("bindingWidth")),
                    "binding_depth": text(provenance.get("bindingDepth")),
                    "decoration_note": text(provenance.get("decorationNote")),
                    "rubrication_note": text(provenance.get("rubricationNote")),
                    "rubrication_date": text(provenance.get("rubricationDate")),
                    "manuscript_note": text(provenance.get("msNote")),
                    "stamps_note": text(provenance.get("stampsNote")),
                    "shelfmark_evidence": compact_json(provenance.get("shelfmark")),
                    "price_amount": text(provenance.get("priceAmount")),
                    "price_currency": text(provenance.get("priceCurrency")),
                    "price_note": text(provenance.get("priceNote")),
                    "evidence_date": text(provenance.get("evidenceDate")),
                    "place_count": len(places),
                    "additional_evidence_json": compact_json(additional_evidence),
                }
            )

            for place_sequence, place in enumerate(places, start=1):
                place_occurrence_id = f"{provenance_id}-loc{place_sequence:02d}"
                latitude, longitude = coordinates(place.get("location"))
                geonames_id = text(place.get("geonamesId"))
                variants = place.get("variantPlacenames") or []
                place_rows.append(
                    {
                        "place_occurrence_id": place_occurrence_id,
                        "provenance_id": provenance_id,
                        "mei_id": mei_id,
                        "place_sequence": place_sequence,
                        "name": text(place.get("name")),
                        "preferred_placename": text(place.get("preferredPlacename")),
                        "geonames_id": geonames_id,
                        "geonames_url": (
                            f"https://www.geonames.org/{geonames_id}" if geonames_id else ""
                        ),
                        "latitude": latitude,
                        "longitude": longitude,
                        "country": text(place.get("country")),
                        "variant_placenames": text(variants),
                        "variant_placename_count": len(variants),
                        "place_note": text(place.get("note")),
                    }
                )

    relationship_rows = [
        {"relationship_id": f"r{sequence:03d}", **relationship}
        for sequence, relationship in enumerate(relationships, start=1)
    ]

    provenance_ids = {row["provenance_id"] for row in provenance_rows}
    if len(provenance_ids) != len(provenance_rows):
        raise ValueError("Generated provenance identifiers are not unique")
    if any(row["provenance_id"] not in provenance_ids for row in place_rows):
        raise ValueError("A place occurrence refers to an unknown provenance block")

    derived_directory.mkdir(parents=True, exist_ok=True)
    write_csv(derived_directory / "mei-copies.csv", COPY_COLUMNS, copy_rows)
    write_csv(
        derived_directory / "mei-provenance.csv",
        PROVENANCE_COLUMNS,
        provenance_rows,
    )
    write_csv(derived_directory / "mei-places.csv", PLACE_COLUMNS, place_rows)
    write_csv(
        derived_directory / "mei-record-links.csv",
        RELATIONSHIP_COLUMNS,
        relationship_rows,
    )

    return {
        "copies": len(copy_rows),
        "provenance_blocks": len(provenance_rows),
        "place_occurrences": len(place_rows),
        "relationships": len(relationship_rows),
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_SOURCE_PATH,
        help="saved MEI JSON snapshot (default: data/sample/mei-pilot.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_DERIVED_DIRECTORY,
        help="directory for the four CSV tables (default: data/derived)",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    source_path = arguments.input.resolve()
    derived_directory = arguments.output_dir.resolve()
    counts = transform(source_path, derived_directory)
    print(f"Source snapshot: {display_path(source_path)}")
    print(f"MEI copies: {counts['copies']}")
    print(f"Provenance blocks: {counts['provenance_blocks']}")
    print(f"Place occurrences: {counts['place_occurrences']}")
    print(f"ISTC–MEI relationships: {counts['relationships']}")


if __name__ == "__main__":
    main()
