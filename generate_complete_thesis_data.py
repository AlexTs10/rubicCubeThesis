#!/usr/bin/env python3
"""
Generate comprehensive benchmark data for thesis analysis.
Compares Thistlethwaite and Kociemba algorithms.
"""

import json
import csv
import time
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver
from src.kociemba.solver import KociembaSolver


def run_single_test(algorithm_name: str, solver, cube: RubikCube, max_time: float = 30) -> Dict:
    """Run a single test case."""
    start_time = time.time()

    try:
        if algorithm_name == "Thistlethwaite":
            solution = solver.solve(cube, max_time=max_time, verbose=False)
        else:
            result = solver.solve(cube, timeout=max_time, verbose=False)
            if result is None:
                raise Exception("Solver returned None (timeout or failure)")
            solution, _, _ = result

        end_time = time.time()

        return {
            "algorithm": algorithm_name,
            "success": True,
            "solution_length": len(solution),
            "time_seconds": round(end_time - start_time, 4),
            "solution": " ".join(solution),
            "error": None
        }
    except Exception as e:
        return {
            "algorithm": algorithm_name,
            "success": False,
            "solution_length": None,
            "time_seconds": None,
            "solution": None,
            "error": str(e)
        }


def generate_benchmarks(depths: List[int], tests_per_depth: int, seeds_start: int = 42):
    """Generate comprehensive benchmark dataset."""

    results = []

    for depth in depths:
        print(f"\n{'='*60}")
        print(f"Testing scramble depth: {depth} moves")
        print(f"{'='*60}")

        for test_num in range(tests_per_depth):
            seed = seeds_start + test_num

            print(f"\nTest {test_num + 1}/{tests_per_depth} (seed={seed}, depth={depth})")

            # Create scrambled cube
            cube = RubikCube()
            scramble = cube.scramble(moves=depth, seed=seed)

            # Test Thistlethwaite
            print("  - Running Thistlethwaite...", end=" ", flush=True)
            thistlethwaite = ThistlethwaiteSolver()
            result_t = run_single_test("Thistlethwaite", thistlethwaite, cube.copy(), max_time=30)
            result_t.update({
                "scramble_depth": depth,
                "seed": seed,
                "scramble": " ".join(scramble),
                "test_id": f"depth{depth}_seed{seed}"
            })
            results.append(result_t)

            if result_t["success"]:
                print(f"✓ {result_t['solution_length']} moves in {result_t['time_seconds']}s")
            else:
                print(f"✗ {result_t['error']}")

            # Test Kociemba
            print("  - Running Kociemba...", end=" ", flush=True)
            kociemba = KociembaSolver()
            result_k = run_single_test("Kociemba", kociemba, cube.copy(), max_time=60)
            result_k.update({
                "scramble_depth": depth,
                "seed": seed,
                "scramble": " ".join(scramble),
                "test_id": f"depth{depth}_seed{seed}"
            })
            results.append(result_k)

            if result_k["success"]:
                print(f"✓ {result_k['solution_length']} moves in {result_k['time_seconds']}s")
            else:
                print(f"✗ {result_k['error']}")

    return results


def save_results(results: List[Dict], output_dir: Path = Path(".")):
    """Save results in multiple formats."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON format
    json_file = output_dir / f"thesis_data_complete_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Saved JSON: {json_file}")

    # CSV format
    csv_file = output_dir / f"thesis_data_complete_{timestamp}.csv"
    if results:
        keys = results[0].keys()
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
    print(f"✓ Saved CSV: {csv_file}")

    # Summary statistics
    print_summary(results)

    return json_file, csv_file


def print_summary(results: List[Dict]):
    """Print statistical summary."""

    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}\n")

    for algo in ["Thistlethwaite", "Kociemba"]:
        algo_results = [r for r in results if r["algorithm"] == algo and r["success"]]

        if algo_results:
            times = [r["time_seconds"] for r in algo_results]
            lengths = [r["solution_length"] for r in algo_results]

            print(f"{algo}:")
            print(f"  Success Rate: {len(algo_results)}/{len([r for r in results if r['algorithm'] == algo])}")
            print(f"  Avg Solution Length: {sum(lengths)/len(lengths):.1f} moves")
            print(f"  Avg Time: {sum(times)/len(times):.3f}s")
            print(f"  Min Time: {min(times):.3f}s")
            print(f"  Max Time: {max(times):.3f}s")
            print()


if __name__ == "__main__":
    print("="*60)
    print("COMPREHENSIVE THESIS BENCHMARK DATA GENERATION")
    print("="*60)
    print("\nConfiguration:")
    print("  Algorithms: Thistlethwaite, Kociemba")
    print("  Scramble Depths: 5, 10, 15, 20 moves")
    print("  Tests per Depth: 10")
    print("  Seeds: 42-51")
    print("  Total Tests: 80 (40 per algorithm)")
    print("\nEstimated Time: 10-20 minutes")
    print("="*60)

    input("\nPress Enter to start benchmark...")

    # Run benchmarks
    results = generate_benchmarks(
        depths=[5, 10, 15, 20],
        tests_per_depth=10,
        seeds_start=42
    )

    # Save results
    save_results(results, Path("."))

    print("\n" + "="*60)
    print("✓ BENCHMARK COMPLETE")
    print("="*60)
