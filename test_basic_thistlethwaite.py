"""Quick test of Thistlethwaite implementation."""

import sys
sys.path.insert(0, '/home/user/rubicCubeThesis')

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver
from src.thistlethwaite.coordinates import permutation_to_rank, rank_to_permutation
import numpy as np

print("="*60)
print("TESTING THISTLETHWAITE IMPLEMENTATION")
print("="*60)

# Test 1: Permutation utilities
print("\n1. Testing permutation utilities...")
perm = np.array([0, 1, 2, 3])
rank = permutation_to_rank(perm)
print(f"   Identity permutation rank: {rank}")
assert rank == 0, "Identity should have rank 0"

perm2 = rank_to_permutation(rank, 4)
assert np.array_equal(perm, perm2), "Round-trip failed"
print("   ✓ Permutation utilities work")

# Test 2: Cube initialization
print("\n2. Testing cube initialization...")
cube = RubikCube()
assert cube.is_solved(), "New cube should be solved"
print("   ✓ Cube initializes correctly")

# Test 3: Simple solve
print("\n3. Testing Thistlethwaite solver...")
solver = ThistlethwaiteSolver(use_pattern_databases=False)
print("   Solver initialized")

# Test on solved cube
print("\n4. Testing on already solved cube...")
result = solver.solve(cube, verbose=False)
if result is not None:
    all_moves, phase_moves = result
    print(f"   Solution length: {len(all_moves)} (should be 0)")
    assert len(all_moves) == 0, "Solved cube should need 0 moves"
    print("   ✓ Correctly handles solved cube")
else:
    print("   ✗ Failed to solve (this is unexpected)")

# Test on simple scramble
print("\n5. Testing on simple scramble...")
cube2 = RubikCube()
scramble = ['U', 'R', 'U\'']
cube2.apply_moves(scramble)
print(f"   Scramble: {' '.join(scramble)}")

print("   Solving (this may take a while without pattern databases)...")
result2 = solver.solve(cube2, verbose=False)

if result2 is not None:
    all_moves2, phase_moves2 = result2
    print(f"   Solution length: {len(all_moves2)}")

    # Verify solution
    test_cube = RubikCube()
    test_cube.apply_moves(scramble)
    test_cube.apply_moves(all_moves2)

    if test_cube.is_solved():
        print("   ✓ Solution verified!")
        print(f"   Solution: {' '.join(all_moves2)}")
    else:
        print("   ✗ Solution doesn't work!")
else:
    print("   ⚠ Solver didn't find solution (may need more time or pattern databases)")

print("\n" + "="*60)
print("BASIC TESTS COMPLETE")
print("="*60)
