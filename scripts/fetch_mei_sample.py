#!/usr/bin/env python3
"""Fetch a small, reproducible sample from the public CERL MEI API.

This is an exploratory script, not yet the production harvester for the full
corpus. It deliberately includes one ISTC identifier without a current MEI hit
so that the missing-data case remains visible in the sample.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPOSITORY_ROOT / "data" / "sample" / "mei-api-sample.json"
API_ENDPOINT = "https://data.cerl.org/mei/_search"

# Three ordinary edition links plus all three ISTC links recorded for GW 13403.
SAMPLE_ISTC_IDS = (
    "ib00512000",  # GW 04168: one MEI copy at the time of the test
    "ib00503000",  # GW 04172: several MEI copies
    "ib00506000",  # GW 04175: a larger result set
    "ih00370100",  # GW 13403
    "ih00427000",  # GW 13403: no MEI hit at the time of the test
    "ih00427100",  # GW 13403
)


def fetch_sample() -> dict:
    query = "(" + " OR ".join(SAMPLE_ISTC_IDS) + ")"
    parameters = urlencode(
        {
            "query": query,
            "_format": "json",
            "nofacets": "true",
            "size": "100",
            "mode": "unstored",
        }
    )
    request = Request(
        f"{API_ENDPOINT}?{parameters}",
        headers={"User-Agent": "prayer-books-in-motion exploratory data reuse"},
    )
    with urlopen(request, timeout=60) as response:
        api_response = json.load(response)

    raw_records = api_response.get("rows", [])
    relationships: list[dict] = []
    related_record_ids: set[str] = set()
    counts = {
        identifier: {"direct": 0, "bound_with": 0}
        for identifier in SAMPLE_ISTC_IDS
    }

    for record in raw_records:
        mei_id = record.get("id")
        host_item_id = record.get("hostItemId")
        common = {
            "mei_id": mei_id,
            "host_istc_id": host_item_id,
            "holding_institution_id": record.get("holdingInstitutionId"),
            "shelfmark": record.get("shelfmark"),
        }

        if host_item_id in SAMPLE_ISTC_IDS:
            relationships.append(
                {
                    "requested_istc_id": host_item_id,
                    "relation_type": "direct",
                    "linked_copy_id": record.get("copyId"),
                    **common,
                }
            )
            counts[host_item_id]["direct"] += 1
            related_record_ids.add(mei_id)

        for bound_item in record.get("boundWith", []):
            requested_id = bound_item.get("istcId")
            if requested_id not in SAMPLE_ISTC_IDS:
                continue
            relationships.append(
                {
                    "requested_istc_id": requested_id,
                    "relation_type": "bound_with",
                    "linked_copy_id": bound_item.get("copyId"),
                    **common,
                }
            )
            counts[requested_id]["bound_with"] += 1
            related_record_ids.add(mei_id)

    # Preserve all records that are directly or materially related to a
    # requested edition. The relationship table keeps these cases distinct.
    records = [record for record in raw_records if record.get("id") in related_record_ids]

    return {
        "metadata": {
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "source": API_ENDPOINT,
            "purpose": "Exploratory API and data-model test",
            "requested_istc_ids": list(SAMPLE_ISTC_IDS),
            "api_hits_reported": api_response.get("hits", {}).get("value"),
            "records_returned_raw": len(raw_records),
            "records_returned": len(records),
            "unrelated_records_discarded": len(raw_records) - len(records),
            "relationships_returned": len(relationships),
            "records_per_istc_id": counts,
        },
        "relationships": relationships,
        "records": records,
    }


def main() -> None:
    sample = fetch_sample()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(sample, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {OUTPUT_PATH.relative_to(REPOSITORY_ROOT)}")
    print(f"MEI records retained: {sample['metadata']['records_returned']}")
    for identifier, counts in sample["metadata"]["records_per_istc_id"].items():
        print(
            f"  {identifier}: {counts['direct']} direct, "
            f"{counts['bound_with']} bound-with"
        )


if __name__ == "__main__":
    main()
