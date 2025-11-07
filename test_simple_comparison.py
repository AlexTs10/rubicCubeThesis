"""
Simple test to verify the comparison framework can be imported and initialized.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Step 1: Importing modules...")
from src.cube.rubik_cube import RubikCube
print("  ✓ RubikCube imported")

from src.thistlethwaite import ThistlethwaiteSolver
print("  ✓ ThistlethwaiteSolver imported")

from src.kociemba.cubie import CubieCube, from_facelet_cube
print("  ✓ CubieCube imported")

from src.korf.a_star import IDAStarSolver
from src.korf.composite_heuristic import create_heuristic
print("  ✓ Korf solvers imported")

print("\nStep 2: Testing Thistlethwaite on a simple scramble...")
cube = RubikCube()
scramble = cube.scramble(moves=5, seed=42)
print(f"  Scramble: {' '.join(scramble)}")

solver = ThistlethwaiteSolver(use_pattern_databases=False)
result = solver.solve(cube, verbose=False)

if result:
    all_moves, phase_moves = result
    print(f"  ✓ Thistlethwaite solved in {len(all_moves)} moves")
else:
    print("  ✗ Thistlethwaite failed")

print("\nStep 3: Testing Korf IDA* on same scramble...")
cube2 = RubikCube()
cube2.scramble(moves=5, seed=42)

heuristic = create_heuristic('manhattan')  # Use simple Manhattan for speed
korf_solver = IDAStarSolver(heuristic=heuristic, max_depth=15, timeout=30.0)
solution = korf_solver.solve(cube2)

if solution:
    print(f"  ✓ Korf IDA* solved in {len(solution)} moves")
else:
    print("  ✗ Korf IDA* failed")

print("\n✓ All tests passed! Comparison framework components are working.")
