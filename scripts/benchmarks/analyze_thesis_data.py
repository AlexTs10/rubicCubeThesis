#!/usr/bin/env python3
"""Analyze benchmark data for thesis."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.benchmarks.artifact_utils import (
    DEFAULT_BENCHMARK_DIR,
    find_default_benchmark_sources,
    load_normalized_benchmark_payload,
    resolve_benchmark_sources,
)


DEFAULT_DATA_DIR = DEFAULT_BENCHMARK_DIR

def normalize_results(payload):
    """Normalize multiple benchmark JSON shapes into a flat result list."""
    if isinstance(payload, list):
        if payload and "algorithm" in payload[0]:
            return payload

        normalized = []
        for row in payload:
            depth = row.get("depth")
            for algorithm_key, label in (
                ("thistlethwaite", "Thistlethwaite"),
                ("kociemba", "Kociemba"),
                ("korf", "External exact backend"),
            ):
                normalized.append(
                    {
                        "algorithm": label,
                        "success": row.get(f"{algorithm_key}_success", False),
                        "solution_length": row.get(f"{algorithm_key}_moves"),
                        "time_seconds": row.get(f"{algorithm_key}_time"),
                        "scramble_depth": depth,
                    }
                )
        return normalized

    if isinstance(payload, dict) and "results" in payload:
        normalized = []
        for row in payload["results"]:
            depth = row.get("scramble_depth")
            for algorithm_key in ("thistlethwaite", "kociemba", "korf"):
                result = row.get(algorithm_key)
                if not result:
                    continue
                algorithm_label = (
                    "External exact backend"
                    if algorithm_key == "korf"
                    else result.get("algorithm", algorithm_key.title())
                )
                normalized.append(
                    {
                        "algorithm": algorithm_label,
                        "success": result.get("solved", False),
                        "solution_length": result.get("solution_length"),
                        "time_seconds": result.get("time_seconds"),
                        "scramble_depth": depth,
                    }
                )
        return normalized

    raise ValueError("Unsupported benchmark file format")


def find_default_data_files() -> list[Path]:
    """Find the canonical benchmark source set for analysis."""
    return find_default_benchmark_sources(DEFAULT_DATA_DIR)


def find_default_data_file() -> Path | None:
    """Return the first canonical benchmark source for backward compatibility."""
    files = find_default_data_files()
    return files[0] if files else None


def analyze_data(json_file: Path | list[Path]):
    """Generate statistical analysis."""
    json_files = json_file if isinstance(json_file, list) else [json_file]
    results = []
    for path in json_files:
        results.extend(normalize_results(load_normalized_benchmark_payload(path)))

    print("="*60)
    print("STATISTICAL ANALYSIS")
    print("="*60)

    for algo in ["Thistlethwaite", "Kociemba", "External exact backend"]:
        print(f"\n{algo} Algorithm:")
        print("-" * 40)

        algo_results = [r for r in results if r["algorithm"] == algo]
        successful = [r for r in algo_results if r["success"]]

        if not successful:
            print("  No successful results")
            continue

        times = np.array([r["time_seconds"] for r in successful])
        lengths = np.array([r["solution_length"] for r in successful])

        print(f"Success Rate: {len(successful)}/{len(algo_results)} ({len(successful)/len(algo_results)*100:.1f}%)")
        print(f"\nSolution Length:")
        print(f"  Mean:   {np.mean(lengths):.2f} moves")
        print(f"  Median: {np.median(lengths):.2f} moves")
        print(f"  Std:    {np.std(lengths):.2f} moves")
        print(f"  Min:    {np.min(lengths)} moves")
        print(f"  Max:    {np.max(lengths)} moves")

        print(f"\nExecution Time:")
        print(f"  Mean:   {np.mean(times):.4f}s")
        print(f"  Median: {np.median(times):.4f}s")
        print(f"  Std:    {np.std(times):.4f}s")
        print(f"  Min:    {np.min(times):.4f}s")
        print(f"  Max:    {np.max(times):.4f}s")

        # By depth analysis
        print(f"\nBy Scramble Depth:")
        for depth in [5, 10, 15, 20]:
            depth_results = [r for r in successful if r["scramble_depth"] == depth]
            if depth_results:
                depth_lengths = [r["solution_length"] for r in depth_results]
                depth_times = [r["time_seconds"] for r in depth_results]
                print(f"  {depth} moves: {np.mean(depth_lengths):.1f} solution moves, {np.mean(depth_times):.3f}s avg")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        json_files = find_default_data_files()
        if not json_files:
            print("No benchmark data files found!")
            sys.exit(1)
    else:
        json_files = resolve_benchmark_sources(Path(sys.argv[1]))
        if not json_files:
            print(f"No benchmark data files found for {sys.argv[1]}!")
            sys.exit(1)

    analyze_data(json_files)
