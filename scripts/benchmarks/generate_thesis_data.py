"""
Legacy Benchmark for Exploratory Thesis Data Generation

This script is retained for historical comparison only. It does not reproduce
the canonical 100-scramble thesis benchmark dataset. For the thesis-ready
benchmark pipeline, use `scripts/benchmarks/regenerate_thesis_benchmarks.py`.
"""

import argparse
import sys
import time
import json
import csv
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "results" / "benchmarks" / "thesis"

# Add src to path
sys.path.insert(0, str(ROOT))

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver
from src.kociemba.solver import KociembaSolver

def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run the legacy exploratory thesis benchmark script."
    )
    parser.add_argument(
        "--allow-legacy-output",
        action="store_true",
        help="Acknowledge that this script is non-canonical and retained only for exploratory use.",
    )
    return parser.parse_args()


args = parse_args()
if not args.allow_legacy_output:
    raise SystemExit(
        "Legacy script: this command does not reproduce the canonical thesis dataset. "
        "Use `python scripts/benchmarks/regenerate_thesis_benchmarks.py` instead. "
        "Re-run with `--allow-legacy-output` only if you explicitly want the historical two-algorithm benchmark."
    )

print("=" * 70)
print("LEGACY THESIS DATA GENERATION (NON-CANONICAL)")
print("=" * 70)
print()

# Configuration
SCRAMBLE_DEPTHS = [5, 10, 15, 20]
SCRAMBLES_PER_DEPTH = 10
SEEDS = list(range(42, 42 + SCRAMBLES_PER_DEPTH))

results = []

# Initialize solvers
print("Initializing solvers...")
thistlethwaite = ThistlethwaiteSolver(enable_kociemba_fallback=False)
kociemba = KociembaSolver()
print("✓ All solvers ready\n")

# Run benchmarks
total_tests = len(SCRAMBLE_DEPTHS) * SCRAMBLES_PER_DEPTH
current_test = 0

for depth in SCRAMBLE_DEPTHS:
    print(f"\n{'=' * 70}")
    print(f"DEPTH: {depth} moves")
    print(f"{'=' * 70}\n")

    for i, seed in enumerate(SEEDS):
        current_test += 1
        print(f"Test {current_test}/{total_tests} (Depth {depth}, Seed {seed})...")

        # Generate scramble
        cube = RubikCube()
        scramble = cube.scramble(depth, seed=seed, allow_redundant=False)
        scramble_str = " ".join(scramble)

        result = {
            "depth": depth,
            "seed": seed,
            "scramble": scramble_str,
            "scramble_length": len(scramble)
        }

        # Test Thistlethwaite
        try:
            test_cube = RubikCube()
            test_cube.apply_moves(scramble)
            start_time = time.time()
            solution_result = thistlethwaite.solve(test_cube, verbose=False, max_time=30)
            solve_time = time.time() - start_time

            if solution_result is not None:
                all_moves, phase_moves, used_fallback = solution_result
                result["thistlethwaite_moves"] = len(all_moves)
                result["thistlethwaite_time"] = solve_time
                result["thistlethwaite_success"] = True
                result["thistlethwaite_used_fallback"] = used_fallback
                print(f"  Thistlethwaite: {len(all_moves)} moves in {solve_time:.3f}s{' (fallback)' if used_fallback else ''}")
            else:
                result["thistlethwaite_moves"] = None
                result["thistlethwaite_time"] = solve_time
                result["thistlethwaite_success"] = False
                print(f"  Thistlethwaite: FAIL (timeout or unsolved) in {solve_time:.3f}s")
        except Exception as e:
            result["thistlethwaite_moves"] = None
            result["thistlethwaite_time"] = None
            result["thistlethwaite_success"] = False
            print(f"  Thistlethwaite: FAILED ({e})")

        # Test Kociemba
        try:
            test_cube = RubikCube()
            test_cube.apply_moves(scramble)
            start_time = time.time()
            solution_result = kociemba.solve(test_cube, timeout=60, verbose=False)
            solve_time = time.time() - start_time
            solution = solution_result[0] if solution_result is not None else None

            result["kociemba_moves"] = len(solution) if solution else None
            result["kociemba_time"] = solve_time
            result["kociemba_success"] = solution is not None
            print(f"  Kociemba: {len(solution) if solution else 'FAIL'} moves in {solve_time:.3f}s")
        except Exception as e:
            result["kociemba_moves"] = None
            result["kociemba_time"] = None
            result["kociemba_success"] = False
            print(f"  Kociemba: FAILED ({e})")

        results.append(result)

# Save results
print(f"\n{'=' * 70}")
print("SAVING RESULTS")
print(f"{'=' * 70}\n")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save as JSON
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

json_path = OUTPUT_DIR / f"legacy_thesis_data_{timestamp}.json"
with open(json_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"✓ JSON saved to: {json_path}")

# Save as CSV
csv_path = OUTPUT_DIR / f"legacy_thesis_data_{timestamp}.csv"
if results:
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"✓ CSV saved to: {csv_path}")

# Print summary statistics
print(f"\n{'=' * 70}")
print("SUMMARY STATISTICS")
print(f"{'=' * 70}\n")

for algo in ["thistlethwaite", "kociemba"]:
    print(f"{algo.upper()}:")

    successful_results = [r for r in results if r.get(f"{algo}_success")]
    if successful_results:
        moves = [r[f"{algo}_moves"] for r in successful_results]
        times = [r[f"{algo}_time"] for r in successful_results]

        print(f"  Success rate: {len(successful_results)}/{len(results)} ({100*len(successful_results)/len(results):.1f}%)")
        print(f"  Moves - Mean: {sum(moves)/len(moves):.1f}, Min: {min(moves)}, Max: {max(moves)}")
        print(f"  Time - Mean: {sum(times)/len(times):.3f}s, Min: {min(times):.3f}s, Max: {max(times):.3f}s")
    else:
        print(f"  No successful solves")
    print()

print(f"{'=' * 70}")
print("✓ THESIS DATA GENERATION COMPLETE!")
print(f"{'=' * 70}")
