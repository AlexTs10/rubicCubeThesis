#!/usr/bin/env python3
"""Generate LaTeX tables for thesis."""

import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "results" / "benchmarks" / "thesis"

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
                ("korf", "Korf_IDA*"),
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
                normalized.append(
                    {
                        "algorithm": result.get("algorithm", algorithm_key.title()),
                        "success": result.get("solved", False),
                        "solution_length": result.get("solution_length"),
                        "time_seconds": result.get("time_seconds"),
                    }
                )
        return normalized

    raise ValueError("Unsupported benchmark file format")


def find_default_data_file() -> Path | None:
    """Find the best available benchmark file for table generation."""
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


def generate_latex_table(json_file: Path):
    """Generate LaTeX comparison table."""

    with open(json_file) as f:
        results = normalize_results(json.load(f))

    print(r"\begin{table}[h]")
    print(r"\centering")
    print(r"\caption{Algorithm Performance Comparison}")
    print(r"\label{tab:algorithm_comparison}")
    print(r"\begin{tabular}{|l|c|c|c|c|}")
    print(r"\hline")
    print(r"\textbf{Algorithm} & \textbf{Avg Moves} & \textbf{Avg Time (s)} & \textbf{Success Rate} & \textbf{Range (moves)} \\")
    print(r"\hline")

    for algo in ["Thistlethwaite", "Kociemba", "Korf_IDA*"]:
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
    default_file = find_default_data_file()
    if default_file:
        generate_latex_table(default_file)
    else:
        print("No data files found!")
