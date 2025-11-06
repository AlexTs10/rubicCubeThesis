"""
Thistlethwaite Algorithm Implementation

This package implements Thistlethwaite's 4-phase algorithm for solving
the Rubik's Cube. The algorithm achieves solutions in at most 52 moves
(typically 30-45 moves).

Main Components:
- ThistlethwaiteSolver: Main solver class
- CubeCoordinates: Coordinate systems for representing cube state
- PatternDatabase: Pre-computed lookup tables for heuristics
- IDAStarSearch: Search algorithm with pruning

Example Usage:
    >>> from src.cube.rubik_cube import RubikCube
    >>> from src.thistlethwaite import ThistlethwaiteSolver
    >>>
    >>> cube = RubikCube()
    >>> cube.scramble(20)
    >>>
    >>> solver = ThistlethwaiteSolver()
    >>> solution, phases = solver.solve(cube)
    >>>
    >>> print("Solution: " + ' '.join(solution))
    >>> print("Total moves: " + str(len(solution)))

Algorithm Phases:
    Phase 0 (G0 to G1): Orient all edges
    Phase 1 (G1 to G2): Orient all corners + place E-slice edges
    Phase 2 (G2 to G3): Position corners in tetrads + edges in slices
    Phase 3 (G3 to G4): Solve remaining cube using only 180 degree turns

References:
    - Original paper: Thistlethwaite (1981)
    - https://www.jaapsch.net/puzzles/thistle.htm
    - https://github.com/itsdaveba/cube-solver (Python reference)
    - https://github.com/benbotto/rubiks-cube-cracker (C++ reference)
"""

from .solver import ThistlethwaiteSolver, solve_cube
from .coordinates import CubeCoordinates
from .tables import PatternDatabase, ThistlethwaitePatternDatabases
from .ida_star import IDAStarSearch, IterativeDeepeningSearch
from .moves import (
    ALL_PHASE_MOVES,
    PHASE_0_MOVES,
    PHASE_1_MOVES,
    PHASE_2_MOVES,
    PHASE_3_MOVES,
    get_phase_moves,
    is_move_allowed
)

__all__ = [
    # Main solver
    'ThistlethwaiteSolver',
    'solve_cube',

    # Coordinates
    'CubeCoordinates',

    # Pattern databases
    'PatternDatabase',
    'ThistlethwaitePatternDatabases',

    # Search algorithms
    'IDAStarSearch',
    'IterativeDeepeningSearch',

    # Move definitions
    'ALL_PHASE_MOVES',
    'PHASE_0_MOVES',
    'PHASE_1_MOVES',
    'PHASE_2_MOVES',
    'PHASE_3_MOVES',
    'get_phase_moves',
    'is_move_allowed',
]

__version__ = '1.0.0'
__author__ = 'Rubik Cube Thesis Project'
