#!/usr/bin/env python3
"""Analyze benchmark data for thesis."""

import json
import sys
from pathlib import Path
import numpy as np

def analyze_data(json_file: Path):
    """Generate statistical analysis."""

    with open(json_file) as f:
        results = json.load(f)

    print("="*60)
    print("STATISTICAL ANALYSIS")
    print("="*60)

    for algo in ["Thistlethwaite", "Kociemba"]:
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
        # Find most recent file
        files = sorted(Path(".").glob("thesis_data_complete_*.json"), reverse=True)
        if files:
            json_file = files[0]
        else:
            print("No benchmark data files found!")
            sys.exit(1)
    else:
        json_file = Path(sys.argv[1])

    analyze_data(json_file)
