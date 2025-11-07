"""
Kociemba Two-Phase Algorithm Solver

This module implements Herbert Kociemba's two-phase algorithm for solving
the Rubik's Cube in near-optimal move counts (typically <19 moves).

Algorithm Overview:
1. Phase 1 (G0 -> G1): Orient all pieces and place UD-slice edges
   - Max 12 moves theoretically
   - Search space: 2.2 billion states
   - Uses IDA* with pruning tables

2. Phase 2 (G1 -> Solved): Solve within the restricted G1 group
   - Max 18 moves theoretically
   - Search space: 19.5 million states
   - Uses only half-turns of F, B and quarter-turns of U, D, R, L

Total: Max 30 moves theoretically, typically <19 moves in practice
"""

import time
from typing import List, Optional, Tuple
from ..cube.rubik_cube import RubikCube
from .cubie import CubieCube, from_facelet_cube, apply_move_to_cubie
from .coord import CoordCube, get_corner_orientation, get_edge_orientation, get_udslice
from .coord import get_corner_permutation, get_edge_permutation, get_udslice_permutation
from .moves import ALL_MOVE_NAMES, PHASE2_MOVES, get_move_tables
from .pruning import get_pruning_tables


class KociembaSolver:
    """
    Kociemba's two-phase algorithm solver.

    Achieves near-optimal solutions (<19 moves average) in reasonable time (<5 seconds).
    """

    def __init__(self, cache_dir: str = "data/kociemba", timeout_grace: float = 10.0):
        """
        Initialize Kociemba solver.

        Args:
            cache_dir: Directory to cache move and pruning tables
            timeout_grace: Extra seconds allowed beyond requested timeout
                before aborting search (softens strict cutoff)
        """
        self.cache_dir = cache_dir
        self.timeout_grace = timeout_grace
        self.move_tables = None
        self.pruning_tables = None
        self._initialized = False

        # Search statistics
        self.nodes_explored = 0

    def _initialize(self) -> None:
        """Initialize move and pruning tables (lazy loading)."""
        if self._initialized:
            return

        print("Initializing Kociemba solver...")
        print("This may take a few minutes on first run (generating tables)...")

        # Load move tables
        self.move_tables = get_move_tables(f"{self.cache_dir}/move_tables")
        self.move_tables.load()

        # Load pruning tables (use deeper BFS to strengthen heuristics)
        self.pruning_tables = get_pruning_tables(f"{self.cache_dir}/pruning_tables")
        self.pruning_tables.load(max_depth=15)

        self._initialized = True
        print("Kociemba solver initialized!")

    def _timed_out(self, start_time: float, timeout: float) -> bool:
        """Check whether the elapsed time exceeded the soft timeout."""
        return (time.time() - start_time) > (timeout + self.timeout_grace)

    def solve(
        self,
        cube: RubikCube,
        max_phase1_depth: int = 12,
        max_phase2_depth: int = 18,
        timeout: float = 30.0,
        verbose: bool = True
    ) -> Optional[Tuple[List[str], List[str], List[str]]]:
        """
        Solve a Rubik's Cube using Kociemba's two-phase algorithm.

        Args:
            cube: Scrambled cube to solve
            max_phase1_depth: Maximum depth for Phase 1 search
            max_phase2_depth: Maximum depth for Phase 2 search
        timeout: Target time limit in seconds (soft limit; solver may use
            up to timeout + timeout_grace before aborting)
            verbose: Whether to print progress

        Returns:
            Tuple of (solution, phase1_moves, phase2_moves) or None if failed
        """
        if verbose:
            print("\n" + "="*70)
            print("KOCIEMBA'S TWO-PHASE ALGORITHM SOLVER")
            print("="*70)

        # Check if already solved
        if cube.is_solved():
            if verbose:
                print("Cube is already solved!")
            return ([], [], [])

        # Initialize tables
        self._initialize()

        # Convert to cubie representation
        cubie = from_facelet_cube(cube)

        start_time = time.time()

        # Phase 1: Reach G1
        if verbose:
            print("\n" + "-"*70)
            print("PHASE 1: G0 → G1 (Orient pieces & place UD-slice)")
            print("-"*70)

        phase1_solution = self._solve_phase1(
            cubie, max_phase1_depth, timeout, verbose
        )

        if phase1_solution is None:
            if verbose:
                print("Failed to solve Phase 1!")
            return None

        phase1_time = time.time() - start_time

        # Apply Phase 1 solution
        for move in phase1_solution:
            cubie = apply_move_to_cubie(cubie, move)

        # Verify we reached G1
        coord = CoordCube(cubie)
        if not coord.is_phase1_solved():
            if verbose:
                print("ERROR: Phase 1 solution did not reach G1!")
            return None

        # Phase 2: Solve within G1
        if verbose:
            print("\n" + "-"*70)
            print("PHASE 2: G1 → Solved")
            print("-"*70)

        remaining_time = max(0.1, timeout - phase1_time)
        phase2_solution = self._solve_phase2(
            cubie, max_phase2_depth, remaining_time, verbose
        )

        if phase2_solution is None:
            if verbose:
                print("Failed to solve Phase 2!")
            return None

        total_time = time.time() - start_time

        # Complete solution
        solution = phase1_solution + phase2_solution

        if verbose:
            print("\n" + "="*70)
            print("SOLUTION FOUND!")
            print("="*70)
            print(f"Phase 1: {len(phase1_solution)} moves in {phase1_time:.2f}s")
            print(f"Phase 2: {len(phase2_solution)} moves in {total_time - phase1_time:.2f}s")
            print(f"Total: {len(solution)} moves in {total_time:.2f}s")
            print(f"Nodes explored: {self.nodes_explored:,}")
            print(f"\nSolution: {' '.join(solution)}")

            # Verify solution
            test_cube = cube.copy()
            test_cube.apply_moves(solution)
            if test_cube.is_solved():
                print("\n✓ Solution verified!")
            else:
                print("\n✗ WARNING: Solution does not solve cube!")

        return (solution, phase1_solution, phase2_solution)

    def _solve_phase1(
        self,
        cubie: CubieCube,
        max_depth: int,
        timeout: float,
        verbose: bool
    ) -> Optional[List[str]]:
        """
        Solve Phase 1: G0 -> G1 using IDA*.

        Goal: All pieces oriented, UD-slice edges in place.

        Args:
            cubie: Current cubie state
            max_depth: Maximum search depth
            timeout: Time limit
            verbose: Print progress

        Returns:
            List of moves or None
        """
        # Get initial coordinates
        co = get_corner_orientation(cubie)
        eo = get_edge_orientation(cubie)
        us = get_udslice(cubie)

        if co == 0 and eo == 0 and us == 0:
            if verbose:
                print("Already in G1!")
            return []

        # IDA* search
        start_time = time.time()
        self.nodes_explored = 0

        for depth in range(max_depth + 1):
            if self._timed_out(start_time, timeout):
                if verbose:
                    print(f"Timeout at depth {depth}")
                return None

            if verbose:
                print(f"Searching depth {depth}...", end=" ")

            result = self._phase1_ida_search(
                co, eo, us, depth, [], None, start_time, timeout
            )

            if result is not None:
                if verbose:
                    print(f"Found! ({self.nodes_explored:,} nodes)")
                return result
            elif verbose:
                print(f"({self.nodes_explored:,} nodes)")

        return None

    def _phase1_ida_search(
        self,
        co: int,
        eo: int,
        us: int,
        depth: int,
        path: List[str],
        last_move: Optional[str],
        start_time: float,
        timeout: float
    ) -> Optional[List[str]]:
        """
        Recursive IDA* search for Phase 1.

        Args:
            co: Corner orientation coordinate
            eo: Edge orientation coordinate
            us: UD-slice coordinate
            depth: Remaining depth
            path: Current move path
            last_move: Last move (to avoid redundant moves)
            start_time: Search start time
            timeout: Time limit

        Returns:
            Solution path or None
        """
        self.nodes_explored += 1

        # Check timeout
        if self._timed_out(start_time, timeout):
            return None

        # Goal test
        if co == 0 and eo == 0 and us == 0:
            return path

        # Heuristic pruning
        if depth == 0:
            return None

        h = self.pruning_tables.get_phase1_heuristic(co, eo, us)
        if h > depth:
            return None

        # Try all moves
        for move in ALL_MOVE_NAMES:
            # Prune redundant moves (same face consecutively)
            if last_move is not None:
                last_face = last_move[0]
                if move[0] == last_face:
                    continue
                # Prune opposite faces in wrong order (U before D, F before B, L before R)
                if (last_face == 'U' and move[0] == 'D') or \
                   (last_face == 'F' and move[0] == 'B') or \
                   (last_face == 'L' and move[0] == 'R'):
                    continue

            # Apply move
            new_co, new_eo, new_us = self.move_tables.apply_move_to_coords(
                co, eo, us, move
            )

            # Recurse
            result = self._phase1_ida_search(
                new_co, new_eo, new_us, depth - 1,
                path + [move], move, start_time, timeout
            )

            if result is not None:
                return result

        return None

    def _solve_phase2(
        self,
        cubie: CubieCube,
        max_depth: int,
        timeout: float,
        verbose: bool
    ) -> Optional[List[str]]:
        """
        Solve Phase 2: G1 -> Solved using IDA*.

        Only uses Phase 2 moves (U, D, R2, L2, F2, B2 and variants).

        Args:
            cubie: Current cubie state (must be in G1)
            max_depth: Maximum search depth
            timeout: Time limit
            verbose: Print progress

        Returns:
            List of moves or None
        """
        # Get Phase 2 coordinates
        cp = get_corner_permutation(cubie)
        ep = get_edge_permutation(cubie)
        sp = get_udslice_permutation(cubie)

        if cp == 0 and ep == 0 and sp == 0:
            if verbose:
                print("Already solved!")
            return []

        # IDA* search
        start_time = time.time()
        phase2_nodes = 0

        for depth in range(max_depth + 1):
            if self._timed_out(start_time, timeout):
                if verbose:
                    print(f"Timeout at depth {depth}")
                return None

            if verbose:
                print(f"Searching depth {depth}...", end=" ")

            result = self._phase2_ida_search(
                cp, ep, sp, depth, [], None, start_time, timeout
            )

            phase2_nodes = self.nodes_explored - phase2_nodes

            if result is not None:
                if verbose:
                    print(f"Found! ({phase2_nodes:,} nodes)")
                return result
            elif verbose:
                print(f"({phase2_nodes:,} nodes)")

        return None

    def _phase2_ida_search(
        self,
        cp: int,
        ep: int,
        sp: int,
        depth: int,
        path: List[str],
        last_move: Optional[str],
        start_time: float,
        timeout: float
    ) -> Optional[List[str]]:
        """
        Recursive IDA* search for Phase 2.

        Args:
            cp: Corner permutation coordinate
            ep: Edge permutation coordinate
            sp: UD-slice permutation coordinate
            depth: Remaining depth
            path: Current move path
            last_move: Last move
            start_time: Search start time
            timeout: Time limit

        Returns:
            Solution path or None
        """
        self.nodes_explored += 1

        # Check timeout
        if self._timed_out(start_time, timeout):
            return None

        # Goal test
        if cp == 0 and ep == 0 and sp == 0:
            return path

        # Heuristic pruning
        if depth == 0:
            return None

        h = self.pruning_tables.get_phase2_heuristic(cp, ep, sp)
        if h > depth:
            return None

        # Try all Phase 2 moves
        for move in PHASE2_MOVES:
            # Prune redundant moves
            if last_move is not None:
                last_face = last_move[0]
                if move[0] == last_face:
                    continue
                if (last_face == 'U' and move[0] == 'D') or \
                   (last_face == 'L' and move[0] == 'R'):
                    continue

            # Apply move
            new_cp, new_ep, new_sp = self.move_tables.apply_move_to_phase2_coords(
                cp, ep, sp, move
            )

            # Recurse
            result = self._phase2_ida_search(
                new_cp, new_ep, new_sp, depth - 1,
                path + [move], move, start_time, timeout
            )

            if result is not None:
                return result

        return None


def solve_cube(
    cube: RubikCube,
    max_phase1_depth: int = 12,
    max_phase2_depth: int = 18,
    timeout: float = 30.0,
    verbose: bool = True
) -> Optional[List[str]]:
    """
    Convenience function to solve a cube with Kociemba's algorithm.

    Args:
        cube: Cube to solve
        max_phase1_depth: Maximum depth for Phase 1
        max_phase2_depth: Maximum depth for Phase 2
        timeout: Time limit
        verbose: Print progress

    Returns:
        List of moves to solve the cube, or None if failed
    """
    solver = KociembaSolver()
    result = solver.solve(cube, max_phase1_depth, max_phase2_depth, timeout, verbose)

    if result is None:
        return None

    solution, _, _ = result
    return solution
