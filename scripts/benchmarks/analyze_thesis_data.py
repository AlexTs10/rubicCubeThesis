#!/usr/bin/env python3
"""Analyze benchmark data for thesis."""

import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "results" / "benchmarks" / "thesis"

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
                ("korf", "Korf_IDA*"),
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
                normalized.append(
                    {
                        "algorithm": result.get("algorithm", algorithm_key.title()),
                        "success": result.get("solved", False),
                        "solution_length": result.get("solution_length"),
                        "time_seconds": result.get("time_seconds"),
                        "scramble_depth": depth,
                    }
                )
        return normalized

    raise ValueError("Unsupported benchmark file format")


def find_default_data_file() -> Path | None:
    """Find the best available benchmark file for analysis."""
    candidates = [
        DEFAULT_DATA_DIR / "thesis_results_combined.json",
        *sorted(DEFAULT_DATA_DIR.glob("thesis_data_complete_*.json"), reverse=True),
        *sorted(DEFAULT_DATA_DIR.glob("thesis_data_*.json"), reverse=True),
        *sorted(DEFAULT_DATA_DIR.glob("thesis_bench_d*.json")),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def analyze_data(json_file: Path):
    """Generate statistical analysis."""

    with open(json_file) as f:
        results = normalize_results(json.load(f))

    print("="*60)
    print("STATISTICAL ANALYSIS")
    print("="*60)

    for algo in ["Thistlethwaite", "Kociemba", "Korf_IDA*"]:
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
        json_file = find_default_data_file()
        if json_file is None:
            print("No benchmark data files found!")
            sys.exit(1)
    else:
        json_file = Path(sys.argv[1])

    analyze_data(json_file)
