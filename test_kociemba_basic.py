"""
Basic test script for Kociemba implementation.
Tests basic functionality before running full test suite.
"""

from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import CubieCube, from_facelet_cube, apply_move_to_cubie
from src.kociemba.coord import CoordCube, get_corner_orientation, get_edge_orientation, get_udslice
from src.kociemba.solver import solve_cube

print("="*70)
print("KOCIEMBA ALGORITHM - BASIC TESTS")
print("="*70)

# Test 1: Cubie representation
print("\n1. Testing cubie representation...")
cubie = CubieCube()
assert cubie.is_solved(), "Failed: Solved cube check"
print("   ✓ Solved cube created successfully")

cubie = apply_move_to_cubie(cubie, 'R')
assert not cubie.is_solved(), "Failed: Move application"
print("   ✓ Move application works")

# Test 2: Facelet to cubie conversion
print("\n2. Testing facelet to cubie conversion...")
facelet = RubikCube()
cubie = from_facelet_cube(facelet)
assert cubie.is_solved(), "Failed: Facelet conversion"
print("   ✓ Facelet to cubie conversion works")

# Test 3: Coordinate systems
print("\n3. Testing coordinate systems...")
cubie = CubieCube()
co = get_corner_orientation(cubie)
eo = get_edge_orientation(cubie)
us = get_udslice(cubie)
assert co == 0 and eo == 0 and us == 0, "Failed: Solved coordinates"
print(f"   ✓ Solved cube coordinates: CO={co}, EO={eo}, UDS={us}")

coord = CoordCube(cubie)
assert coord.is_solved(), "Failed: CoordCube check"
print("   ✓ CoordCube class works")

# Test 4: Simple solve
print("\n4. Testing solver on simple cube...")
cube = RubikCube()
cube.apply_moves(['R', 'U'])
print(f"   Scramble: R U")

try:
    solution = solve_cube(cube, timeout=30.0, verbose=True)

    if solution is not None:
        print(f"\n   ✓ Solution found: {len(solution)} moves")

        # Verify solution
        test_cube = RubikCube()
        test_cube.apply_moves(['R', 'U'])
        test_cube.apply_moves(solution)

        if test_cube.is_solved():
            print("   ✓ Solution verified!")
        else:
            print("   ✗ Solution does not solve cube!")
    else:
        print("   ✗ Failed to find solution")
except Exception as e:
    print(f"   ✗ Error during solving: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("BASIC TESTS COMPLETE")
print("="*70)
