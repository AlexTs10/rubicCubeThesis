"""
Korf's Optimal Solver using Pattern Databases

This module implements an optimal solver for the Rubik's Cube using
Richard Korf's IDA* algorithm with pattern databases. This guarantees
optimal solutions (minimum number of moves).

Uses the RubikOptimal package (hkociemba implementation) which implements:
- Pattern databases for corners (~42MB) and edges (~244MB each)
- IDA* search with additive heuristics
- Guaranteed optimal solutions (≤20 moves)

Performance:
- PyPy: ~13 minutes for 10 random cubes
- CPython: ~8 hours for 10 random cubes (not recommended)
- Hardest positions (20 moves): ~3 hours with PyPy

References:
- Korf, R. (1997). "Finding Optimal Solutions to Rubik's Cube Using Pattern Databases"
- https://github.com/hkociemba/RubiksCube-OptimalSolver
"""

import time
from typing import List, Optional, Tuple
import numpy as np

try:
    import optimal.solver as sv
    OPTIMAL_AVAILABLE = True
except ImportError:
    OPTIMAL_AVAILABLE = False

from ..cube.rubik_cube import RubikCube, Face


class KorfOptimalSolver:
    """
    Optimal solver using Korf's IDA* algorithm with pattern databases.

    This solver guarantees finding the shortest solution but may take
    significant time for difficult positions.
    """

    def __init__(self):
        """Initialize the optimal solver."""
        if not OPTIMAL_AVAILABLE:
            raise ImportError(
                "RubikOptimal package not installed. "
                "Install with: pip install RubikOptimal\n"
                "For best performance, use PyPy: pypy3 -m pip install RubikOptimal"
            )

        # Statistics
        self.solve_count = 0
        self.total_time = 0.0
        self.total_moves = 0

    def _cube_to_string(self, cube: RubikCube) -> str:
        """
        Convert RubikCube state to the string format expected by optimal solver.

        Format: UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB
        (9 facelets for each face in order U, R, F, D, L, B)

        Args:
            cube: RubikCube instance

        Returns:
            54-character string representing cube state
        """
        # Map face indices to face letters
        face_map = {
            0: 'U',  # Up
            1: 'D',  # Down
            2: 'F',  # Front
            3: 'B',  # Back
            4: 'L',  # Left
            5: 'R'   # Right
        }

        # Order for the optimal solver: U, R, F, D, L, B
        face_order = [
            Face.U,  # 0
            Face.R,  # 5
            Face.F,  # 2
            Face.D,  # 1
            Face.L,  # 4
            Face.B   # 3
        ]

        result = []
        for face in face_order:
            face_state = cube.state[face.value]
            for facelet in face_state:
                result.append(face_map[facelet])

        return ''.join(result)

    def _parse_solution(self, solution_str: str) -> List[str]:
        """
        Parse solution string from optimal solver to list of moves.

        The optimal solver returns strings like "U1 R2 F3 D1 L2 B3"
        where the number indicates:
        - 1: 90° clockwise (U)
        - 2: 180° (U2)
        - 3: 90° counter-clockwise (U')

        Args:
            solution_str: Solution string from optimal solver

        Returns:
            List of moves in Singmaster notation
        """
        if not solution_str or solution_str.strip() == '':
            return []

        # Remove the move count suffix like "(18f*)" if present
        if '(' in solution_str:
            solution_str = solution_str.split('(')[0].strip()

        tokens = solution_str.strip().split()
        moves = []

        for token in tokens:
            if len(token) < 2:
                continue

            face = token[0]  # U, R, F, D, L, or B
            rotation = token[1]  # 1, 2, or 3

            if rotation == '1':
                moves.append(face)
            elif rotation == '2':
                moves.append(face + '2')
            elif rotation == '3':
                moves.append(face + "'")

        return moves

    def solve(
        self,
        cube: RubikCube,
        verbose: bool = True,
        timeout: Optional[float] = None
    ) -> Optional[Tuple[List[str], dict]]:
        """
        Find optimal solution for the cube.

        Args:
            cube: Scrambled cube to solve
            verbose: Whether to print progress
            timeout: Maximum time in seconds (not enforced by underlying solver)

        Returns:
            Tuple of (solution_moves, stats_dict) or None if failed
            - solution_moves: List of moves in Singmaster notation
            - stats_dict: Dictionary with solving statistics
        """
        if verbose:
            print("\n" + "="*70)
            print("KORF'S OPTIMAL SOLVER (IDA* with Pattern Databases)")
            print("="*70)
            print("⚠️  WARNING: This solver guarantees optimal solutions but may")
            print("   take significant time (minutes to hours for difficult cubes)")
            print("   For best performance, run with PyPy instead of CPython")
            print("="*70)

        # Check if already solved
        if cube.is_solved():
            if verbose:
                print("Cube is already solved!")
            return ([], {'time': 0.0, 'moves': 0, 'optimal': True})

        # Convert cube to string format
        cube_string = self._cube_to_string(cube)

        if verbose:
            print(f"\nCube state: {cube_string[:18]}...{cube_string[-18:]}")
            print("\nSearching for optimal solution...")
            print("(This may take a while - please be patient)")

        # Solve
        start_time = time.time()

        try:
            # Note: The optimal solver doesn't support timeout parameter
            # and will generate pattern databases on first run (~13 min with PyPy)
            solution_str = sv.solve(cube_string)

            if solution_str is None:
                if verbose:
                    print("\n❌ Failed to find solution")
                return None

            solve_time = time.time() - start_time

            # Parse solution
            solution = self._parse_solution(solution_str)

            # Update statistics
            self.solve_count += 1
            self.total_time += solve_time
            self.total_moves += len(solution)

            # Prepare stats
            stats = {
                'time': solve_time,
                'moves': len(solution),
                'optimal': True,
                'raw_solution': solution_str
            }

            if verbose:
                print(f"\n✓ Optimal solution found!")
                print(f"  Solution: {' '.join(solution)}")
                print(f"  Moves: {len(solution)}")
                print(f"  Time: {solve_time:.2f} seconds")
                print(f"  Raw output: {solution_str}")

                # Verify solution
                test_cube = cube.copy()
                test_cube.apply_moves(solution)
                if test_cube.is_solved():
                    print(f"  ✓ Solution verified!")
                else:
                    print(f"  ⚠️  WARNING: Solution does not solve the cube!")

            return (solution, stats)

        except Exception as e:
            if verbose:
                print(f"\n❌ Error during solving: {e}")
            return None

    def get_statistics(self) -> dict:
        """
        Get solving statistics.

        Returns:
            Dictionary with average time, moves, etc.
        """
        if self.solve_count == 0:
            return {
                'cubes_solved': 0,
                'avg_time': 0.0,
                'avg_moves': 0.0,
                'total_time': 0.0
            }

        return {
            'cubes_solved': self.solve_count,
            'avg_time': self.total_time / self.solve_count,
            'avg_moves': self.total_moves / self.solve_count,
            'total_time': self.total_time
        }


def solve_optimal(cube: RubikCube, verbose: bool = True) -> Optional[List[str]]:
    """
    Convenience function to find optimal solution.

    Args:
        cube: Scrambled cube
        verbose: Whether to print progress

    Returns:
        List of moves or None if failed
    """
    solver = KorfOptimalSolver()
    result = solver.solve(cube, verbose=verbose)

    if result is None:
        return None

    solution, _ = result
    return solution
