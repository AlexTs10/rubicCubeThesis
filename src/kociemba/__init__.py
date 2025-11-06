"""
Kociemba's Two-Phase Algorithm for Rubik's Cube Solving

This package implements Herbert Kociemba's famous two-phase algorithm,
which solves the Rubik's Cube in near-optimal move counts (typically <19 moves).

Main components:
- cubie: Cubie-level representation (corners and edges with orientations)
- coord: Six coordinate systems for the two phases
- moves: Precomputed move tables for fast coordinate updates
- pruning: Pattern databases for IDA* heuristic
- solver: Main two-phase IDA* solver

Usage:
    from src.kociemba import KociembaSolver, solve_cube
    from src.cube.rubik_cube import RubikCube

    # Create and scramble a cube
    cube = RubikCube()
    cube.scramble(20)

    # Solve with Kociemba's algorithm
    solution = solve_cube(cube)
    print(f"Solution: {' '.join(solution)}")

Performance:
- Average solution length: <19 moves
- Average solve time: <5 seconds
- Pattern database size: ~80 MB
"""

from .solver import KociembaSolver, solve_cube
from .cubie import CubieCube, from_facelet_cube
from .coord import CoordCube

__all__ = [
    'KociembaSolver',
    'solve_cube',
    'CubieCube',
    'from_facelet_cube',
    'CoordCube',
]
