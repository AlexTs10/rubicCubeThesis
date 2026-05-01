#!/usr/bin/env python3
"""Generate LaTeX tables for thesis."""

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
    """Normalize multiple benchmark JSON shapes into flat algorithm rows."""
    if isinstance(payload, list):
        if payload and "algorithm" in payload[0]:
            return payload

        normalized = []
        for row in payload:
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
                    }
                )
        return normalized

    if isinstance(payload, dict) and "results" in payload:
        normalized = []
        for row in payload["results"]:
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
                    }
                )
        return normalized

    raise ValueError("Unsupported benchmark file format")


def find_default_data_files() -> list[Path]:
    """Find the canonical benchmark source set for table generation."""
    return find_default_benchmark_sources(DEFAULT_DATA_DIR)


def find_default_data_file() -> Path | None:
    """Return the first canonical benchmark source for backward compatibility."""
    files = find_default_data_files()
    return files[0] if files else None


def generate_latex_table(json_file: Path | list[Path]):
    """Generate LaTeX comparison table."""
    json_files = json_file if isinstance(json_file, list) else [json_file]
    results = []
    for path in json_files:
        results.extend(normalize_results(load_normalized_benchmark_payload(path)))

    print(r"\begin{table}[h]")
    print(r"\centering")
    print(r"\caption{Algorithm Performance Comparison}")
    print(r"\label{tab:algorithm_comparison}")
    print(r"\begin{tabular}{|l|c|c|c|c|}")
    print(r"\hline")
    print(r"\textbf{Algorithm} & \textbf{Avg Moves} & \textbf{Avg Time (s)} & \textbf{Success Rate} & \textbf{Range (moves)} \\")
    print(r"\hline")

    for algo in ["Thistlethwaite", "Kociemba", "External exact backend"]:
        successful = [r for r in results if r["algorithm"] == algo and r["success"]]
        total = len([r for r in results if r["algorithm"] == algo])

        if successful:
            lengths = [r["solution_length"] for r in successful]
            times = [r["time_seconds"] for r in successful]

            avg_length = np.mean(lengths)
            avg_time = np.mean(times)
            success_rate = len(successful) / total * 100
            min_len = min(lengths)
            max_len = max(lengths)

            print(f"{algo} & {avg_length:.1f} & {avg_time:.3f} & {success_rate:.1f}\\% & {min_len}--{max_len} \\\\")

    print(r"\hline")
    print(r"\end{tabular}")
    print(r"\end{table}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        default_files = find_default_data_files()
        if default_files:
            generate_latex_table(default_files)
        else:
            print("No data files found!")
    else:
        json_files = resolve_benchmark_sources(Path(sys.argv[1]))
        if json_files:
            generate_latex_table(json_files)
        else:
            print(f"No data files found for {sys.argv[1]}!")
