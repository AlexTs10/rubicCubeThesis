#!/usr/bin/env python3
"""Regenerate the thesis benchmark artifacts from a fixed scramble set."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "results" / "benchmarks" / "thesis"
DEFAULT_RERUN_ROOT = ROOT / "results" / "benchmarks" / "reruns"

sys.path.insert(0, str(ROOT))

from scripts.benchmarks.artifact_utils import (
    COMBINED_BENCHMARK_NAME,
    DEPTH_BENCHMARK_GLOB,
    normalize_benchmark_payload,
)
from src.cube.rubik_cube import RubikCube
from src.evaluation.algorithm_comparison import AlgorithmComparison


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Rerun the thesis benchmarks on a fixed stored scramble set."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Benchmark JSON file or thesis benchmark directory used as the scramble source. "
            "Directories resolve to the canonical combined artifact when present."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory where thesis_bench_d*.json and thesis_results_combined.json will be written. "
            "Defaults to a timestamped directory under results/benchmarks/reruns/."
        ),
    )
    parser.add_argument(
        "--overwrite-canonical",
        action="store_true",
        help="Write into results/benchmarks/thesis instead of a timestamped rerun directory.",
    )
    parser.add_argument(
        "--thistlethwaite-timeout",
        type=float,
        default=30.0,
        help="Per-scramble timeout for Thistlethwaite.",
    )
    parser.add_argument(
        "--kociemba-timeout",
        type=float,
        default=60.0,
        help="Per-scramble timeout for Kociemba.",
    )
    parser.add_argument(
        "--korf-timeout",
        type=float,
        default=120.0,
        help="Per-scramble timeout for Korf.",
    )
    parser.add_argument(
        "--korf-max-depth",
        type=int,
        default=20,
        help="Max depth for the internal heuristic Korf fallback.",
    )
    parser.add_argument(
        "--korf-backend",
        choices=("auto", "optimal", "heuristic"),
        default="auto",
        help="Which Korf backend to use.",
    )
    return parser.parse_args()


def load_scramble_set(source: Path) -> dict[int, list[dict[str, object]]]:
    """Load the stored scramble set grouped by scramble depth."""
    grouped: dict[int, list[dict[str, object]]] = {}
    seen_scrambles: set[tuple[int, int]] = set()

    if source.is_dir():
        combined = source / COMBINED_BENCHMARK_NAME
        source_paths = [combined] if combined.exists() else sorted(source.glob(DEPTH_BENCHMARK_GLOB))
    else:
        source_paths = [source]

    for source_path in source_paths:
        payload = normalize_benchmark_payload(json.loads(source_path.read_text(encoding="utf-8")))
        if not isinstance(payload, dict) or "results" not in payload:
            raise ValueError(f"Unsupported scramble source: {source_path}")
        for row in payload.get("results", []):
            depth = int(row["scramble_depth"])
            scramble_id = int(row["scramble_id"])
            key = (depth, scramble_id)
            if key in seen_scrambles:
                continue
            seen_scrambles.add(key)
            grouped.setdefault(depth, []).append(
                {
                    "scramble_id": scramble_id,
                    "scramble_moves": list(row["scramble_moves"]),
                }
            )

    return {depth: sorted(rows, key=lambda item: item["scramble_id"]) for depth, rows in grouped.items()}


def rerun_depth(
    comparison: AlgorithmComparison,
    depth: int,
    scrambles: list[dict[str, object]],
) -> list:
    """Rerun one scramble depth with the configured comparison harness."""
    comparison.results = []

    print("=" * 70)
    print(f"RERUNNING THESIS BENCHMARKS AT DEPTH {depth}")
    print("=" * 70)

    for row in scrambles:
        cube = RubikCube()
        scramble_moves = list(row["scramble_moves"])
        cube.apply_moves(scramble_moves)
        cube._scramble_depth = depth
        cube._scramble_moves = scramble_moves

        result = comparison.compare_on_scramble(
            cube,
            scramble_id=int(row["scramble_id"]),
        )
        comparison.results.append(result)
        print()

    return comparison.results


def write_combined_results(
    output_dir: Path,
    depth_payloads: dict[int, dict[str, object]],
) -> Path:
    """Write the combined thesis benchmark artifact."""
    combined_path = output_dir / "thesis_results_combined.json"
    normalized_depth_payloads = {
        depth: normalize_benchmark_payload(payload) for depth, payload in depth_payloads.items()
    }
    depths = sorted(normalized_depth_payloads)

    combined = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "description": "Combined benchmark results across multiple depths",
            "depths": depths,
            "total_scrambles_per_depth": len(normalized_depth_payloads[depths[0]]["results"]) if depths else 0,
        },
        "results": [],
    }

    if depths:
        first_depth_meta = normalized_depth_payloads[depths[0]]["metadata"]
        for key, value in first_depth_meta.items():
            if key.startswith("korf_") or key in {
                "solver_instances_reused_per_batch",
                "benchmark_warm_start",
                "thistlethwaite_timeout",
                "kociemba_timeout",
                "kociemba_timeout_soft",
                "kociemba_timeout_grace",
                "kociemba_effective_soft_timeout",
                "timing_methodology",
                "scramble_depth_semantics",
                "verified_scramble_depth_available",
            }:
                combined["metadata"][key] = value

    for depth in depths:
        combined["metadata"][f"depth_{depth}"] = normalized_depth_payloads[depth]["metadata"]
        combined["results"].extend(normalized_depth_payloads[depth]["results"])

    combined = normalize_benchmark_payload(combined)
    combined_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    return combined_path


def main() -> None:
    """Regenerate all thesis benchmark artifacts from the stored scrambles."""
    args = parse_args()

    if not args.source.exists():
        raise FileNotFoundError(f"Scramble source not found: {args.source}")

    if args.output_dir is None:
        if args.overwrite_canonical:
            args.output_dir = DEFAULT_OUTPUT_DIR
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            args.output_dir = DEFAULT_RERUN_ROOT / timestamp

    if args.output_dir.resolve() == DEFAULT_OUTPUT_DIR.resolve() and not args.overwrite_canonical:
        raise ValueError(
            "Refusing to overwrite canonical thesis benchmark artifacts. "
            "Pass --overwrite-canonical explicitly or choose --output-dir."
        )

    scramble_set = load_scramble_set(args.source)
    if not scramble_set:
        raise ValueError(f"No scrambles found in {args.source}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    comparison = AlgorithmComparison(
        thistlethwaite_timeout=args.thistlethwaite_timeout,
        kociemba_timeout=args.kociemba_timeout,
        korf_timeout=args.korf_timeout,
        korf_max_depth=args.korf_max_depth,
        korf_backend=args.korf_backend,
    )

    depth_payloads: dict[int, dict[str, object]] = {}

    for depth in sorted(scramble_set):
        rerun_depth(comparison, depth, scramble_set[depth])
        output_path = args.output_dir / f"thesis_bench_d{depth}.json"
        comparison.export_results(str(output_path))
        depth_payloads[depth] = json.loads(output_path.read_text())

    combined_path = write_combined_results(args.output_dir, depth_payloads)

    print("=" * 70)
    print("THESIS BENCHMARK REGENERATION COMPLETE")
    print("=" * 70)
    print(f"Source scrambles: {args.source}")
    print(f"Output directory: {args.output_dir}")
    print(f"Combined results: {combined_path}")


if __name__ == "__main__":
    main()
