# TASK 03: Complete Benchmark Data Generation

**Priority:** 🔴 HIGH
**Status:** 🔄 In Progress - Timeout Fix Implemented, Partial Data Collected
**Estimated Time:** 1 hour (to complete remaining tests)
**Difficulty:** Medium
**Blocker:** Yes - Required for thesis results chapter

---

## 📝 PROBLEM DESCRIPTION

Current benchmark dataset is incomplete:
- ✅ **Kociemba:** 40/40 test cases (100% complete)
- ❌ **Thistlethwaite:** 0/40 test cases (0% complete - blocked by API issue)

### What's Needed:
Complete dataset comparing both algorithms across multiple scramble depths for quantitative thesis analysis.

### Current Data Files:
- `thesis_data_20251107_054744.json` (13 KB) - Kociemba only
- `thesis_data_20251107_054744.csv` (3.2 KB) - Kociemba only

---

## 🚨 ISSUE DISCOVERED (2025-01-07) - ✅ RESOLVED

### Initial Problem
Benchmark generation **stopped at Test 7/10 (depth=5, seed=48)** due to extremely long computation time in Kociemba solver without timeout.

### Root Cause
- Benchmark script not passing timeout parameter to Kociemba solver
- Kociemba solver has built-in timeout support but wasn't being used
- Return value handling was incorrect for both solvers (both return tuples)

### Solution Implemented (2025-01-07)
✅ **Fixed timeout handling in `generate_complete_thesis_data.py`:**
1. Pass `timeout=60` parameter to Kociemba solver (with 10s grace period = 70s max)
2. Handle Kociemba's tuple return value: `(solution, phase1_moves, phase2_moves)`
3. Handle Thistlethwaite's tuple return value: `(solution, phases)`
4. Disable verbose output for both solvers during benchmarking
5. Add proper error handling for timeout cases

**Commits:**
- `9e09835` - Fix benchmark timeout handling for Kociemba solver
- `585f406` - Fix Thistlethwaite return value handling in benchmark

### Test Results After Fix
✅ **Test 7 (seed=48, depth=5) now completes successfully:**
- Thistlethwaite: 11 moves in 53.96s
- Kociemba: 5 moves in 0.0005s

✅ **Partial benchmark completed (50/80 tests) before manual stop:**
- Depth 5: 10/10 tests completed (20 total for both algorithms)
- Depth 10: 10/10 tests completed (20 total for both algorithms)
- Depth 15: 5/10 tests completed (10 total for both algorithms)
- Depth 20: 0/10 tests (not started)

**All tests passed with timeout mechanism working correctly!**

---

## 🎯 ACCEPTANCE CRITERIA

- [ ] 40 test cases for Thistlethwaite solver generated
- [ ] 40 test cases for Kociemba solver (re-run for consistency)
- [ ] Both algorithms tested at depths: 5, 10, 15, 20 moves
- [ ] 10 tests per depth (seeds 42-51)
- [ ] Complete dataset in JSON format
- [ ] Complete dataset in CSV format
- [ ] Optional: LaTeX table format for direct thesis inclusion
- [ ] Statistical summary generated (mean, median, std dev)

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Verify TASK_01 is Complete

```bash
# Test that Thistlethwaite accepts max_time
python -c "
from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver

cube = RubikCube()
cube.scramble(moves=10, seed=42)
solver = ThistlethwaiteSolver()
solution = solver.solve(cube, max_time=30)
print(f'✓ Thistlethwaite API fixed: {len(solution)} moves')
"
```

If this fails, complete TASK_01 first.

---

### Step 2: Locate or Create Benchmark Script

```bash
# Find existing benchmark script
find . -name "*benchmark*" -o -name "*thesis_data*" | grep -v __pycache__ | grep ".py"

# Common locations:
ls generate_thesis_data.py 2>/dev/null
ls scripts/benchmark.py 2>/dev/null
ls scripts/run_comprehensive_tests.py 2>/dev/null
```

If script doesn't exist, create it (see Step 3).

---

### Step 3: Create/Update Benchmark Script

**Create:** `generate_complete_thesis_data.py`

```python
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
            solution = solver.solve(cube, max_time=max_time)
        else:
            solution = solver.solve(cube)

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
            result_k = run_single_test("Kociemba", kociemba, cube.copy())
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
```

---

### Step 4: Run Benchmark Script

```bash
# Make executable
chmod +x generate_complete_thesis_data.py

# Run benchmark (will take 10-20 minutes)
python generate_complete_thesis_data.py

# Monitor progress (it will print status updates)
```

**Expected output:**
```
=============================================================
Testing scramble depth: 5 moves
=============================================================

Test 1/10 (seed=42, depth=5)
  - Running Thistlethwaite... ✓ 12 moves in 0.2341s
  - Running Kociemba... ✓ 3 moves in 0.0012s

Test 2/10 (seed=43, depth=5)
...
```

---

### Step 5: Verify Generated Data

```bash
# Check files were created
ls -lh thesis_data_complete_*.json
ls -lh thesis_data_complete_*.csv

# Preview JSON
head -50 thesis_data_complete_*.json

# Preview CSV
head -20 thesis_data_complete_*.csv

# Count results
jq '. | length' thesis_data_complete_*.json
# Expected: 80 (40 per algorithm)

# Check success rate
jq '[.[] | select(.success == true)] | length' thesis_data_complete_*.json
# Expected: ~80 (or slightly less if some timeout)
```

---

### Step 6: Generate Statistical Analysis

**Create:** `analyze_thesis_data.py`

```python
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
```

Run analysis:
```bash
python analyze_thesis_data.py thesis_data_complete_*.json
```

---

### Step 7: Optional - Generate LaTeX Tables

**Create:** `generate_latex_tables.py`

```python
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
```

Run:
```bash
python generate_latex_tables.py > thesis_table.tex
```

---

## 🧪 VERIFICATION COMMANDS

```bash
# 1. Verify data files exist
ls -lh thesis_data_complete_*.{json,csv}

# 2. Check record count
echo "Total records:"
jq '. | length' thesis_data_complete_*.json

# 3. Check algorithms represented
echo "Algorithms tested:"
jq '[.[].algorithm] | unique' thesis_data_complete_*.json

# 4. Check success rates
echo "Thistlethwaite successes:"
jq '[.[] | select(.algorithm == "Thistlethwaite" and .success == true)] | length' thesis_data_complete_*.json

echo "Kociemba successes:"
jq '[.[] | select(.algorithm == "Kociemba" and .success == true)] | length' thesis_data_complete_*.json

# 5. Run analysis script
python analyze_thesis_data.py
```

---

## 📁 FILES TO CREATE

1. **`generate_complete_thesis_data.py`** - Benchmark script
2. **`analyze_thesis_data.py`** - Statistical analysis
3. **`generate_latex_tables.py`** - LaTeX table generator (optional)

### Generated Files:
4. **`thesis_data_complete_YYYYMMDD_HHMMSS.json`** - Raw data (JSON)
5. **`thesis_data_complete_YYYYMMDD_HHMMSS.csv`** - Raw data (CSV)
6. **`thesis_table.tex`** - LaTeX table (optional)

---

## ⏱️ TIME BREAKDOWN

- **Script creation:** 10-15 minutes (if doesn't exist)
- **Benchmark execution:** 10-20 minutes (depends on machine)
- **Analysis:** 5 minutes
- **Verification:** 5 minutes
- **LaTeX generation:** 5 minutes (optional)

**Total:** 30-50 minutes (depending on optional components)

---

## 📊 SUCCESS METRICS

You'll know you're done when:

1. ✅ 80 total benchmark records (40 per algorithm)
2. ✅ Both algorithms tested at all depths (5, 10, 15, 20)
3. ✅ Success rate >90% for both algorithms
4. ✅ JSON and CSV files generated
5. ✅ Statistical analysis completed
6. ✅ Data ready for thesis results chapter

---

## 🔗 RELATED TASKS

- **TASK_01:** Must complete first (API fix)
- **TASK_04:** Can use this data for UI demos

---

## 📚 REFERENCES

- TESTING_REPORT.md (lines 109-173) - Previous benchmark structure
- thesis_data_20251107_054744.json - Example of existing format

---

**Next Step:** Verify TASK_01 complete, then run benchmark script!
