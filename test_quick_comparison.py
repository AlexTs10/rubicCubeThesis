"""
Quick comparison test - Tests 3 scrambles to validate the framework
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import time
from src.cube.rubik_cube import RubikCube
from src.thistlethwaite import ThistlethwaiteSolver
from src.korf.a_star import IDAStarSolver
from src.korf.composite_heuristic import create_heuristic

print("=" * 70)
print("QUICK ALGORITHM COMPARISON TEST")
print("=" * 70)
print()

# Initialize solvers
print("Initializing solvers...")
thistle_solver = ThistlethwaiteSolver(use_pattern_databases=False)
print("  ✓ Thistlethwaite ready")

heuristic = create_heuristic('manhattan')
korf_solver = IDAStarSolver(heuristic=heuristic, max_depth=15, timeout=30.0)
print("  ✓ Korf IDA* ready")
print()

results = []

# Test 3 scrambles
for i in range(3):
    print(f"Test {i+1}/3:")
    cube = RubikCube()
    scramble = cube.scramble(moves=6, seed=100 + i)
    print(f"  Scramble: {' '.join(scramble)}")

    # Test Thistlethwaite
    cube1 = cube.copy()
    start = time.time()
    result1 = thistle_solver.solve(cube1, verbose=False)
    time1 = time.time() - start

    if result1:
        moves1, _ = result1
        print(f"  Thistlethwaite: {len(moves1)} moves in {time1:.3f}s ✓")
    else:
        print(f"  Thistlethwaite: FAILED in {time1:.3f}s ✗")

    # Test Korf IDA*
    cube2 = cube.copy()
    start = time.time()
    result2 = korf_solver.solve(cube2)
    time2 = time.time() - start

    if result2:
        print(f"  Korf IDA*:      {len(result2)} moves in {time2:.3f}s ✓")
    else:
        print(f"  Korf IDA*:      FAILED in {time2:.3f}s ✗")

    print()

    results.append({
        'thistle_solved': result1 is not None,
        'thistle_moves': len(result1[0]) if result1 else None,
        'thistle_time': time1,
        'korf_solved': result2 is not None,
        'korf_moves': len(result2) if result2 else None,
        'korf_time': time2
    })

print("=" * 70)
print("SUMMARY")
print("=" * 70)

thistle_success = sum(1 for r in results if r['thistle_solved'])
korf_success = sum(1 for r in results if r['korf_solved'])

print(f"\nThistlethwaite:")
print(f"  Success rate: {thistle_success}/3 ({thistle_success/3*100:.1f}%)")
if thistle_success > 0:
    avg_moves = sum(r['thistle_moves'] for r in results if r['thistle_solved']) / thistle_success
    avg_time = sum(r['thistle_time'] for r in results if r['thistle_solved']) / thistle_success
    print(f"  Avg moves: {avg_moves:.1f}")
    print(f"  Avg time:  {avg_time:.3f}s")

print(f"\nKorf IDA*:")
print(f"  Success rate: {korf_success}/3 ({korf_success/3*100:.1f}%)")
if korf_success > 0:
    avg_moves = sum(r['korf_moves'] for r in results if r['korf_solved']) / korf_success
    avg_time = sum(r['korf_time'] for r in results if r['korf_solved']) / korf_success
    print(f"  Avg moves: {avg_moves:.1f}")
    print(f"  Avg time:  {avg_time:.3f}s")

print("\n" + "=" * 70)
print("✓ Comparison framework validation complete!")
print("=" * 70)
