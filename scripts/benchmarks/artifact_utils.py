#!/usr/bin/env python3
"""Shared helpers for thesis benchmark artifact selection and normalization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK_DIR = ROOT / "results" / "benchmarks" / "thesis"
COMBINED_BENCHMARK_NAME = "thesis_results_combined.json"
DEPTH_BENCHMARK_GLOB = "thesis_bench_d*.json"
LEGACY_BENCHMARK_PATTERNS = ("thesis_data_complete_*.json", "thesis_data_*.json")
SCRAMBLE_DEPTH_SEMANTICS = (
    "scramble_depth records the requested scramble length; "
    "verified_scramble_depth is populated only when the exact "
    "distance is known from the optimal Korf backend."
)


def _depth_sort_key(path: Path) -> tuple[int, str]:
    """Sort depth shards numerically instead of lexicographically."""
    try:
        return (int(path.stem.rsplit("d", 1)[1]), path.name)
    except (IndexError, ValueError):
        return (10**9, path.name)


def find_default_benchmark_sources(data_dir: Path = DEFAULT_BENCHMARK_DIR) -> list[Path]:
    """Return the canonical benchmark source set for a thesis benchmark directory."""
    combined = data_dir / COMBINED_BENCHMARK_NAME
    if combined.exists():
        return [combined]

    depth_shards = sorted(data_dir.glob(DEPTH_BENCHMARK_GLOB), key=_depth_sort_key)
    if depth_shards:
        return depth_shards

    for pattern in LEGACY_BENCHMARK_PATTERNS:
        matches = sorted(data_dir.glob(pattern), reverse=True)
        if matches:
            return [matches[0]]

    return []


def resolve_benchmark_sources(source: Path | None = None) -> list[Path]:
    """Resolve a benchmark file or directory into the concrete source files to load."""
    if source is None:
        return find_default_benchmark_sources()
    if source.is_dir():
        return find_default_benchmark_sources(source)
    return [source] if source.exists() else []


def _requested_scramble_length(result: dict[str, Any]) -> int:
    value = result.get("requested_scramble_length")
    if value is not None:
        return int(value)

    scramble_moves = result.get("scramble_moves")
    if isinstance(scramble_moves, list):
        return len(scramble_moves)

    return int(result.get("scramble_depth", 0))


def _verified_scramble_depth(result: dict[str, Any]) -> int | None:
    value = result.get("verified_scramble_depth")
    if value is not None:
        return int(value)

    korf = result.get("korf")
    if (
        isinstance(korf, dict)
        and korf.get("solved")
        and korf.get("optimal_guaranteed")
        and korf.get("solution_length") is not None
    ):
        return int(korf["solution_length"])

    return None


def _case_id(result: dict[str, Any], requested_scramble_length: int) -> str:
    value = result.get("case_id")
    if value:
        return str(value)
    scramble_id = int(result.get("scramble_id", 0))
    return f"d{requested_scramble_length}_{scramble_id:03d}"


def normalize_benchmark_result(result: dict[str, Any]) -> dict[str, Any]:
    """Backfill exporter fields that older committed artifacts may not yet contain."""
    normalized = dict(result)
    requested_scramble_length = _requested_scramble_length(normalized)
    verified_scramble_depth = _verified_scramble_depth(normalized)

    normalized["case_id"] = _case_id(normalized, requested_scramble_length)
    normalized["requested_scramble_length"] = requested_scramble_length
    normalized["verified_scramble_depth"] = verified_scramble_depth
    normalized["scramble_depth_is_verified"] = verified_scramble_depth is not None

    for key in ("thistlethwaite", "kociemba", "korf"):
        algorithm_result = normalized.get(key)
        if not isinstance(algorithm_result, dict):
            continue

        algorithm_payload = dict(algorithm_result)
        algorithm_payload["requested_scramble_length"] = requested_scramble_length
        if (
            algorithm_payload.get("solved")
            and algorithm_payload.get("optimal_guaranteed")
            and algorithm_payload.get("solution_length") is not None
        ):
            algorithm_payload["verified_scramble_depth"] = int(algorithm_payload["solution_length"])
        else:
            algorithm_payload["verified_scramble_depth"] = None
        algorithm_payload["scramble_depth_is_verified"] = (
            algorithm_payload["verified_scramble_depth"] is not None
        )
        normalized[key] = algorithm_payload

    return normalized


def normalize_benchmark_payload(payload: Any) -> Any:
    """Normalize a benchmark payload to the current exporter schema."""
    if not isinstance(payload, dict) or "results" not in payload:
        return payload

    normalized = dict(payload)
    normalized_results = [normalize_benchmark_result(result) for result in payload.get("results", [])]
    normalized["results"] = normalized_results

    metadata = dict(payload.get("metadata", {}))
    metadata["scramble_depth_semantics"] = SCRAMBLE_DEPTH_SEMANTICS
    metadata["verified_scramble_depth_available"] = any(
        result.get("verified_scramble_depth") is not None for result in normalized_results
    )

    results_by_depth: dict[int, list[dict[str, Any]]] = {}
    for result in normalized_results:
        depth = int(result.get("scramble_depth", 0))
        results_by_depth.setdefault(depth, []).append(result)

    for key, value in list(metadata.items()):
        if not key.startswith("depth_") or not isinstance(value, dict):
            continue
        try:
            depth = int(key.split("_", 1)[1])
        except ValueError:
            continue
        depth_metadata = dict(value)
        depth_metadata["scramble_depth_semantics"] = SCRAMBLE_DEPTH_SEMANTICS
        depth_metadata["verified_scramble_depth_available"] = any(
            result.get("verified_scramble_depth") is not None
            for result in results_by_depth.get(depth, [])
        )
        metadata[key] = depth_metadata

    normalized["metadata"] = metadata
    return normalized


def load_normalized_benchmark_payload(path: Path) -> Any:
    """Load a benchmark artifact and upgrade it to the current schema in memory."""
    return normalize_benchmark_payload(json.loads(path.read_text(encoding="utf-8")))


def load_normalized_results(paths: Sequence[Path]) -> list[dict[str, Any]]:
    """Load normalized benchmark result rows from one or more artifact files."""
    normalized_results: list[dict[str, Any]] = []
    for path in paths:
        payload = load_normalized_benchmark_payload(path)
        if isinstance(payload, dict):
            normalized_results.extend(payload.get("results", []))
        elif isinstance(payload, list):
            normalized_results.extend(payload)
    return normalized_results
