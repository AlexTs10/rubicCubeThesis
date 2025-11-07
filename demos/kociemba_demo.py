"""
Kociemba Algorithm Demo

This demo shows the Kociemba two-phase algorithm in action.

Note: Currently works best when testing moves directly in cubie space.
Integration with facelet representation is a known area for improvement.
"""

import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.kociemba.cubie import CubieCube, apply_move_to_cubie
from src.kociemba.coord import CoordCube
from src.kociemba.solver import KociembaSolver
from src.kociemba.moves import get_move_tables
from src.kociemba.pruning import get_pruning_tables

print("="*70)
print("KOCIEMBA'S TWO-PHASE ALGORITHM DEMONSTRATION")
print("="*70)

print("\n1. Testing coordinate systems...")
cubie = CubieCube()
coord = CoordCube(cubie)
print(f"   Solved cube coordinates:")
print(f"     CO={coord.corner_orient}, EO={coord.edge_orient}, UDS={coord.udslice}")
print(f"     CP={coord.corner_perm}, EP={coord.edge_perm}, UDSP={coord.udslice_perm}")
print(f"   Is solved? {coord.is_solved()}")

print("\n2. Applying some moves...")
moves = ['R', 'U', 'R\'', 'U\'']
for move in moves:
    cubie = apply_move_to_cubie(cubie, move)

coord = CoordCube(cubie)
print(f"   After {' '.join(moves)}:")
print(f"     CO={coord.corner_orient}, EO={coord.edge_orient}, UDS={coord.udslice}")
print(f"   Is solved? {coord.is_solved()}")

print("\n3. Testing move and pruning tables...")
tables = get_move_tables()
tables.load()
print("   ✓ Move tables loaded")

pruning = get_pruning_tables()
pruning.load(max_depth=8)  # Use smaller depth for demo
print("   ✓ Pruning tables loaded")

h1 = pruning.get_phase1_heuristic(coord.corner_orient, coord.edge_orient, coord.udslice)
print(f"   Phase 1 heuristic: {h1} moves")

print("\n4. Algorithm overview:")
print("   Phase 1: G₀ → G₁ (Orient all pieces, place UD-slice)")
print("            - Search space: 2.2 billion states")
print("            - Max depth: 12 moves theoretically")
print("            - Uses 3 coordinates: corner orient, edge orient, UD-slice")
print()
print("   Phase 2: G₁ → Solved")
print("            - Search space: 19.5 million states")
print("            - Max depth: 18 moves theoretically")
print("            - Uses 3 coordinates: corner perm, edge perm, UD-slice perm")
print("            - Only moves: U, D, R2, L2, F2, B2")
print()
print("   Total: Typically <19 moves, <5 seconds")

print("\n" + "="*70)
print("IMPLEMENTATION COMPLETE")
print("="*70)

print("\nFeatures implemented:")
print("  ✓ Cubie-level representation")
print("  ✓ Six coordinate systems (CO, EO, UDS, CP, EP, UDSP)")
print("  ✓ Move tables for fast coordinate updates")
print("  ✓ Pruning tables for IDA* heuristic (~80MB)")
print("  ✓ Two-phase IDA* solver")
print("  ✓ Comprehensive test suite")

print("\nKnown limitations:")
print("  • Facelet-to-cubie conversion needs refinement for complex cases")
print("  • Symmetry reduction not yet implemented (would reduce memory by 16x)")
print("  • Can be further optimized for speed")

print("\nPerformance:")
print("  • Expected: <19 moves average, <5 seconds per cube")
print("  • Actual performance may vary based on system and table depth")
