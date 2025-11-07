"""
Comprehensive Benchmark for Thesis Data Generation

Generates detailed performance data for all three algorithms across
multiple scramble depths for thesis analysis.
"""

import sys
import time
import json
import csv
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver
from src.kociemba.solver import KociembaSolver

print("=" * 70)
print("COMPREHENSIVE THESIS DATA GENERATION")
print("=" * 70)
print()

# Configuration
SCRAMBLE_DEPTHS = [5, 10, 15, 20]
SCRAMBLES_PER_DEPTH = 10
SEEDS = list(range(42, 42 + SCRAMBLES_PER_DEPTH))

results = []

# Initialize solvers
print("Initializing solvers...")
thistlethwaite = ThistlethwaiteSolver()
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
        scramble = cube.scramble(depth, seed=seed)
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
                all_moves, phase_moves = solution_result
                result["thistlethwaite_moves"] = len(all_moves)
                result["thistlethwaite_time"] = solve_time
                result["thistlethwaite_success"] = True
                print(f"  Thistlethwaite: {len(all_moves)} moves in {solve_time:.3f}s")
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
            solution = kociemba.solve(test_cube)
            solve_time = time.time() - start_time

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
json_path = f"thesis_data_{timestamp}.json"
with open(json_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"✓ JSON saved to: {json_path}")

# Save as CSV
csv_path = f"thesis_data_{timestamp}.csv"
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
