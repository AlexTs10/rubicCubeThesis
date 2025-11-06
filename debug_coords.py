"""Debug coordinate extraction"""

from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import CubieCube, from_facelet_cube
from src.kociemba.coord import get_corner_orientation, get_edge_orientation, get_udslice

# Test with solved cube
print("Testing solved cube...")
facelet = RubikCube()
cubie = from_facelet_cube(facelet)

print(f"Corner perm: {cubie.corner_perm}")
print(f"Corner orient: {cubie.corner_orient}")
print(f"Edge perm: {cubie.edge_perm}")
print(f"Edge orient: {cubie.edge_orient}")

co = get_corner_orientation(cubie)
eo = get_edge_orientation(cubie)
us = get_udslice(cubie)

print(f"\nCoordinates:")
print(f"  Corner Orient: {co} (should be 0)")
print(f"  Edge Orient: {eo} (should be 0)")
print(f"  UD-Slice: {us} (should be 0)")

# Test basic cubie cube
print("\n\nTesting basic CubieCube (not from facelet)...")
cubie2 = CubieCube()
print(f"Corner perm: {cubie2.corner_perm}")
print(f"Corner orient: {cubie2.corner_orient}")
print(f"Edge perm: {cubie2.edge_perm}")
print(f"Edge orient: {cubie2.edge_orient}")

co2 = get_corner_orientation(cubie2)
eo2 = get_edge_orientation(cubie2)
us2 = get_udslice(cubie2)

print(f"\nCoordinates:")
print(f"  Corner Orient: {co2} (should be 0)")
print(f"  Edge Orient: {eo2} (should be 0)")
print(f"  UD-Slice: {us2} (should be 0)")
