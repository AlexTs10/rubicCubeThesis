#!/usr/bin/env python3
"""Generate LaTeX tables for thesis."""

import json
import sys
from pathlib import Path
import numpy as np

def generate_latex_table(json_file: Path):
    """Generate LaTeX comparison table."""

    with open(json_file) as f:
        results = json.load(f)

    print(r"\begin{table}[h]")
    print(r"\centering")
    print(r"\caption{Algorithm Performance Comparison}")
    print(r"\label{tab:algorithm_comparison}")
    print(r"\begin{tabular}{|l|c|c|c|c|}")
    print(r"\hline")
    print(r"\textbf{Algorithm} & \textbf{Avg Moves} & \textbf{Avg Time (s)} & \textbf{Success Rate} & \textbf{Range (moves)} \\")
    print(r"\hline")

    for algo in ["Thistlethwaite", "Kociemba"]:
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
    files = sorted(Path(".").glob("thesis_data_complete_*.json"), reverse=True)
    if files:
        generate_latex_table(files[0])
    else:
        print("No data files found!")
