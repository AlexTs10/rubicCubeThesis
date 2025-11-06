"""Debug Phase 1 solver"""

from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import CubieCube, from_facelet_cube, apply_move_to_cubie
from src.kociemba.coord import CoordCube, get_corner_orientation, get_edge_orientation, get_udslice
from src.kociemba.moves import get_move_tables

# Create a simple scramble
cube = RubikCube()
cube.apply_moves(['R', 'U'])

# Convert to cubie
cubie = from_facelet_cube(cube)

print("Initial state:")
print(f"  CO={get_corner_orientation(cubie)}")
print(f"  EO={get_edge_orientation(cubie)}")
print(f"  UDS={get_udslice(cubie)}")

# Test manual move application
print("\nApplying moves manually:")
moves = ['U', 'R', 'U2', 'L2', 'U', 'R2', 'L']

for move in moves:
    cubie = apply_move_to_cubie(cubie, move)
    co = get_corner_orientation(cubie)
    eo = get_edge_orientation(cubie)
    us = get_udslice(cubie)
    print(f"  After {move}: CO={co}, EO={eo}, UDS={us}")

print(f"\nFinal: Is Phase1 solved? {co == 0 and eo == 0 and us == 0}")

# Now test with move tables
print("\n\nTesting move tables:")
cubie2 = from_facelet_cube(cube)
co2 = get_corner_orientation(cubie2)
eo2 = get_edge_orientation(cubie2)
us2 = get_udslice(cubie2)

print(f"Initial: CO={co2}, EO={eo2}, UDS={us2}")

# Load move tables
tables = get_move_tables()
tables.load()

for move in moves:
    co2, eo2, us2 = tables.apply_move_to_coords(co2, eo2, us2, move)
    print(f"  After {move}: CO={co2}, EO={eo2}, UDS={us2}")

print(f"\nFinal: Is Phase1 solved? {co2 == 0 and eo2 == 0 and us2 == 0}")

# Compare
print(f"\nDo they match? CO: {co == co2}, EO: {eo == eo2}, UDS: {us == us2}")
