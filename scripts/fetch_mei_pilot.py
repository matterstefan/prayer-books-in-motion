#!/usr/bin/env python3
"""Fetch the reproducible 60-ISTC pilot from the public CERL MEI API.

Each ISTC query is cached separately so that an interrupted run can resume
without repeating completed requests. Search results are paginated with the
documented `offset` and `size` parameters. The combined JSON retains complete
MEI records, query metadata, and separate direct/bound-with relationships.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SELECTION_PATH = REPOSITORY_ROOT / "data" / "sample" / "mei-pilot-istc.csv"
CACHE_DIRECTORY = REPOSITORY_ROOT / "data" / "cache" / "mei-pilot"
OUTPUT_PATH = REPOSITORY_ROOT / "data" / "sample" / "mei-pilot.json"
API_ENDPOINT = "https://data.cerl.org/mei/_search"
PAGE_SIZE = 100
RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def hits_value(response: dict[str, Any]) -> int:
    hits = response.get("hits", 0)
    if isinstance(hits, dict):
        hits = hits.get("value", 0)
    if not isinstance(hits, int):
        raise ValueError(f"Unexpected MEI hits value: {hits!r}")
    return hits


def read_selection() -> list[str]:
    with SELECTION_PATH.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    identifiers = [row["istc_id"].strip() for row in rows]
    if len(identifiers) != 60:
        raise ValueError(f"Pilot selection must contain 60 rows, found {len(identifiers)}")
    if "" in identifiers or len(set(identifiers)) != len(identifiers):
        raise ValueError("Pilot ISTC identifiers must be non-empty and unique")
    return identifiers


class RateLimiter:
    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds
        self.last_request_at: float | None = None

    def wait(self) -> None:
        if self.last_request_at is not None:
            elapsed = time.monotonic() - self.last_request_at
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self.last_request_at = time.monotonic()


def request_page(
    istc_id: str,
    offset: int,
    page_size: int,
    limiter: RateLimiter,
    retries: int = 4,
) -> dict[str, Any]:
    parameters = urlencode(
        {
            "query": istc_id,
            "_format": "json",
            "nofacets": "true",
            "size": str(page_size),
            "offset": str(offset),
            "mode": "unstored",
        }
    )
    request = Request(
        f"{API_ENDPOINT}?{parameters}",
        headers={
            "User-Agent": "prayer-books-in-motion scientific data reuse",
            "Accept": "application/json",
        },
    )

    for attempt in range(1, retries + 1):
        limiter.wait()
        try:
            with urlopen(request, timeout=60) as response:
                raw = response.read()
                try:
                    return json.loads(raw)
                except (json.JSONDecodeError, UnicodeDecodeError) as error:
                    preview = " ".join(raw[:600].decode("utf-8", errors="replace").split())
                    raise ValueError(
                        f"MEI returned non-JSON content for {istc_id}; "
                        f"HTTP {response.status}; "
                        f"Content-Type: {response.headers.get('Content-Type', '(missing)')}; "
                        f"URL: {response.geturl()}; "
                        f"bytes: {len(raw)}; "
                        f"response beginning: {preview or '(empty response)'}"
                    ) from error
        except HTTPError as error:
            if error.code not in RETRYABLE_HTTP_CODES or attempt == retries:
                raise
            time.sleep(2**attempt)
        except (URLError, TimeoutError):
            if attempt == retries:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("Unreachable retry state")


def fetch_complete_query(
    istc_id: str,
    limiter: RateLimiter,
    page_size: int = PAGE_SIZE,
) -> dict[str, Any]:
    if not 1 <= page_size <= 100:
        raise ValueError("MEI search page size must be between 1 and 100")

    rows: list[dict[str, Any]] = []
    seen_record_ids: set[str] = set()
    offset = 0
    reported_hits: int | None = None

    while reported_hits is None or offset < reported_hits:
        response = request_page(istc_id, offset, page_size, limiter)
        if not isinstance(response, dict) or "hits" not in response or "rows" not in response:
            raise ValueError(f"MEI response lacks search-result fields for {istc_id}")
        page_hits = hits_value(response)
        if reported_hits is None:
            reported_hits = page_hits
        elif page_hits != reported_hits:
            raise RuntimeError(
                f"MEI hit count changed during paginated query for {istc_id}: "
                f"{reported_hits} to {page_hits}"
            )

        page_rows = response.get("rows", [])
        if not isinstance(page_rows, list):
            raise ValueError(f"Unexpected rows value for {istc_id}")
        if not page_rows and offset < reported_hits:
            raise RuntimeError(
                f"MEI returned an empty page for {istc_id} at offset {offset} "
                f"before the reported {reported_hits} hits were retrieved"
            )

        new_rows = 0
        for record in page_rows:
            record_id = str(record.get("id", ""))
            if not record_id:
                raise ValueError(f"MEI result without id for {istc_id}")
            if record_id in seen_record_ids:
                continue
            seen_record_ids.add(record_id)
            rows.append(record)
            new_rows += 1
        if page_rows and new_rows == 0:
            raise RuntimeError(
                f"Pagination for {istc_id} made no progress at offset {offset}"
            )
        offset += len(page_rows)

    if len(rows) != reported_hits:
        raise RuntimeError(
            f"MEI reported {reported_hits} hits for {istc_id}, "
            f"but {len(rows)} distinct records were retrieved"
        )

    return {
        "retrieved_at": now_iso(),
        "endpoint": API_ENDPOINT,
        "query": istc_id,
        "page_size": page_size,
        "reported_hits": reported_hits,
        "rows": rows,
    }


def load_or_fetch(
    istc_id: str,
    limiter: RateLimiter,
    refresh: bool,
) -> tuple[dict[str, Any], bool]:
    cache_path = CACHE_DIRECTORY / f"{istc_id}.json"
    if cache_path.exists() and not refresh:
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("query") != istc_id:
            raise ValueError(f"Cache query mismatch in {cache_path}")
        return cached, True

    result = fetch_complete_query(istc_id, limiter)
    atomic_write_json(cache_path, result)
    return result, False


def relationship_rows(record: dict[str, Any], requested_id: str) -> list[dict[str, Any]]:
    common = {
        "mei_id": record.get("id"),
        "host_istc_id": record.get("hostItemId"),
        "holding_institution_id": record.get("holdingInstitutionId"),
        "shelfmark": record.get("shelfmark"),
    }
    relationships: list[dict[str, Any]] = []
    if record.get("hostItemId") == requested_id:
        relationships.append(
            {
                "requested_istc_id": requested_id,
                "relation_type": "direct",
                "linked_copy_id": record.get("copyId"),
                **common,
            }
        )
    for bound_item in record.get("boundWith", []):
        if bound_item.get("istcId") == requested_id:
            relationships.append(
                {
                    "requested_istc_id": requested_id,
                    "relation_type": "bound_with",
                    "linked_copy_id": bound_item.get("copyId"),
                    **common,
                }
            )
    return relationships


def combine_queries(
    identifiers: list[str],
    query_results: list[tuple[dict[str, Any], bool]],
) -> dict[str, Any]:
    records_by_id: dict[str, dict[str, Any]] = {}
    relationships: list[dict[str, Any]] = []
    seen_relationships: set[tuple[Any, ...]] = set()
    results_metadata: dict[str, dict[str, Any]] = {}

    for istc_id, (query_result, from_cache) in zip(identifiers, query_results):
        direct_count = 0
        bound_with_count = 0
        related_record_ids: set[str] = set()

        for record in query_result["rows"]:
            found_relationships = relationship_rows(record, istc_id)
            for relationship in found_relationships:
                key = (
                    relationship["requested_istc_id"],
                    relationship["relation_type"],
                    relationship["mei_id"],
                    relationship["linked_copy_id"],
                )
                if key in seen_relationships:
                    continue
                seen_relationships.add(key)
                relationships.append(relationship)
                if relationship["relation_type"] == "direct":
                    direct_count += 1
                else:
                    bound_with_count += 1

            if not found_relationships:
                continue
            record_id = str(record["id"])
            related_record_ids.add(record_id)
            existing = records_by_id.get(record_id)
            if existing is not None and existing != record:
                raise RuntimeError(
                    f"MEI record {record_id} changed between pilot queries"
                )
            records_by_id[record_id] = record

        results_metadata[istc_id] = {
            "retrieved_at": query_result["retrieved_at"],
            "api_hits_reported": query_result["reported_hits"],
            "rows_returned": len(query_result["rows"]),
            "related_records_retained": len(related_record_ids),
            "unrelated_records_discarded": (
                len(query_result["rows"]) - len(related_record_ids)
            ),
            "direct_relationships": direct_count,
            "bound_with_relationships": bound_with_count,
            "loaded_from_cache": from_cache,
        }

    return {
        "metadata": {
            "compiled_at": now_iso(),
            "source": API_ENDPOINT,
            "purpose": "Reproducible 60-ISTC data-model and visualisation pilot",
            "selection_file": str(SELECTION_PATH.relative_to(REPOSITORY_ROOT)),
            "requested_istc_ids": identifiers,
            "requested_istc_count": len(identifiers),
            "summed_api_hits_reported": sum(
                item[0]["reported_hits"] for item in query_results
            ),
            "distinct_mei_records_retained": len(records_by_id),
            "relationships_retained": len(relationships),
            "query_results": results_metadata,
        },
        "relationships": relationships,
        "records": list(records_by_id.values()),
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and summarize the 60-row selection without network requests",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="ignore the local cache and intentionally retrieve every query again",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="minimum delay in seconds between API requests (default: 1.5)",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.delay < 0:
        raise ValueError("Delay must not be negative")
    identifiers = read_selection()
    print(f"Validated pilot selection: {len(identifiers)} unique ISTC identifiers")
    if arguments.check:
        return

    limiter = RateLimiter(arguments.delay)
    query_results: list[tuple[dict[str, Any], bool]] = []
    for position, istc_id in enumerate(identifiers, start=1):
        print(f"[{position:02d}/{len(identifiers)}] {istc_id}", flush=True)
        query_results.append(
            load_or_fetch(istc_id, limiter, refresh=arguments.refresh)
        )

    combined = combine_queries(identifiers, query_results)
    atomic_write_json(OUTPUT_PATH, combined)
    print(f"Wrote {OUTPUT_PATH.relative_to(REPOSITORY_ROOT)}")
    print(
        "Distinct MEI records retained: "
        f"{combined['metadata']['distinct_mei_records_retained']}"
    )
    print(f"Relationships retained: {combined['metadata']['relationships_retained']}")


if __name__ == "__main__":
    main()
