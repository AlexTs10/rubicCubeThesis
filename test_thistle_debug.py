"""Debug Thistlethwaite solver"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite import ThistlethwaiteSolver

cube = RubikCube()
scramble = cube.scramble(moves=5, seed=42)
print(f"Scramble: {' '.join(scramble)}")
print(f"Is solved before solving: {cube.is_solved()}")

solver = ThistlethwaiteSolver(use_pattern_databases=False)
print("Solver created")

try:
    result = solver.solve(cube, verbose=True)
    print(f"\nResult: {result}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
