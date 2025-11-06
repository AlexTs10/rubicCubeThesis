"""
Thistlethwaite Algorithm Solver

Main implementation of Thistlethwaite's 4-phase algorithm for solving
the Rubik's Cube in at most 52 moves (typically 45 moves with optimization).

The algorithm works by progressively restricting the cube to nested subgroups:
G0 (all states) → G1 → G2 → G3 → G4 (solved)

Each phase restricts the allowed moves while maintaining previous invariants.
"""

from typing import List, Optional, Tuple
import time
from ..cube.rubik_cube import RubikCube
from .coordinates import CubeCoordinates
from .moves import ALL_PHASE_MOVES
from .tables import ThistlethwaitePatternDatabases
from .ida_star import IDAStarSearch


class ThistlethwaiteSolver:
    """
    Complete Thistlethwaite algorithm solver.

    Solves the Rubik's Cube in 4 phases with guaranteed solution length
    of at most 52 moves (typically 30-45 moves).
    """

    def __init__(
        self,
        use_pattern_databases: bool = True,
        cache_dir: str = "data/pattern_databases"
    ):
        """
        Initialize Thistlethwaite solver.

        Args:
            use_pattern_databases: Whether to use pattern databases for IDA* heuristic
            cache_dir: Directory to cache pattern databases
        """
        self.use_pattern_databases = use_pattern_databases
        self.pattern_databases = None

        if use_pattern_databases:
            self.pattern_databases = ThistlethwaitePatternDatabases(cache_dir)
            # Pattern databases will be loaded on first solve

        self._databases_loaded = False

        # Phase configurations
        self.phase_max_depths = [7, 10, 13, 15]
        self.phase_timeouts = [10.0, 30.0, 60.0, 120.0]

    def _ensure_databases_loaded(self):
        """Ensure pattern databases are loaded (lazy loading)."""
        if not self.use_pattern_databases or self._databases_loaded:
            return

        print("Loading pattern databases for first time...")
        self.pattern_databases.load_all(ALL_PHASE_MOVES, max_depth=15)
        self._databases_loaded = True

    def solve(
        self,
        cube: RubikCube,
        verbose: bool = True
    ) -> Optional[Tuple[List[str], List[List[str]]]]:
        """
        Solve a Rubik's Cube using Thistlethwaite's algorithm.

        Args:
            cube: Scrambled cube to solve
            verbose: Whether to print progress

        Returns:
            Tuple of (all_moves, phase_moves) where:
            - all_moves: Complete solution as a single list
            - phase_moves: Solution broken down by phase [[p0_moves], [p1_moves], ...]
            Returns None if solving fails
        """
        if verbose:
            print("\n" + "="*60)
            print("THISTLETHWAITE'S ALGORITHM SOLVER")
            print("="*60)

        # Check if already solved
        if cube.is_solved():
            if verbose:
                print("Cube is already solved!")
            return ([], [[], [], [], []])

        # Ensure pattern databases are loaded
        if self.use_pattern_databases:
            self._ensure_databases_loaded()

        # Solve each phase
        current_cube = cube.copy()
        all_moves = []
        phase_solutions = []
        total_start_time = time.time()

        for phase in range(4):
            if verbose:
                print(f"\n{'='*60}")
                print(f"PHASE {phase}: {self._get_phase_name(phase)}")
                print(f"{'='*60}")

            phase_start_time = time.time()

            # Solve this phase
            phase_moves = self._solve_phase(phase, current_cube, verbose)

            if phase_moves is None:
                if verbose:
                    print(f"Failed to solve phase {phase}")
                return None

            phase_time = time.time() - phase_start_time

            # Apply phase moves
            for move in phase_moves:
                current_cube.apply_move(move)

            all_moves.extend(phase_moves)
            phase_solutions.append(phase_moves)

            if verbose:
                print(f"\nPhase {phase} completed:")
                print(f"  Moves: {len(phase_moves)}")
                print(f"  Solution: {' '.join(phase_moves) if phase_moves else '(already in group)'}")
                print(f"  Time: {phase_time:.2f}s")

        total_time = time.time() - total_start_time

        if verbose:
            print(f"\n{'='*60}")
            print("SOLUTION FOUND!")
            print(f"{'='*60}")
            print(f"Total moves: {len(all_moves)}")
            print(f"Total time: {total_time:.2f}s")
            print(f"\nComplete solution:")
            print(f"  {' '.join(all_moves)}")
            print(f"\nBy phase:")
            for i, moves in enumerate(phase_solutions):
                print(f"  Phase {i}: {' '.join(moves) if moves else '(none)'}")

            # Verify solution
            test_cube = cube.copy()
            test_cube.apply_moves(all_moves)
            if test_cube.is_solved():
                print(f"\n✓ Solution verified!")
            else:
                print(f"\n✗ WARNING: Solution does not solve cube!")

        return (all_moves, phase_solutions)

    def _solve_phase(
        self,
        phase: int,
        cube: RubikCube,
        verbose: bool
    ) -> Optional[List[str]]:
        """
        Solve a single phase using IDA* search.

        Args:
            phase: Phase number (0-3)
            cube: Current cube state
            verbose: Whether to print progress

        Returns:
            List of moves to reach next group, or None if failed
        """
        # Get goal check and heuristic for this phase
        goal_check = self._get_goal_check(phase)
        heuristic = self._get_heuristic(phase)

        # Check if already in goal
        if goal_check(cube):
            if verbose:
                print("Already in target group!")
            return []

        # Get allowed moves
        moves = ALL_PHASE_MOVES[phase]

        if verbose:
            print(f"Allowed moves ({len(moves)}): {', '.join(moves)}")
            if self.use_pattern_databases:
                h_value = heuristic(cube)
                print(f"Heuristic estimate: {h_value} moves")

        # Create IDA* search
        search = IDAStarSearch(
            goal_check=goal_check,
            heuristic=heuristic,
            allowed_moves=moves,
            max_depth=self.phase_max_depths[phase],
            timeout=self.phase_timeouts[phase]
        )

        # Perform search
        if verbose:
            print("Searching...")

        solution = search.search(cube)

        if solution is not None and verbose:
            print(f"Nodes explored: {search.nodes_explored}")

        return solution

    def _get_phase_name(self, phase: int) -> str:
        """Get descriptive name for a phase."""
        names = [
            "G0 → G1 (Orient Edges)",
            "G1 → G2 (Orient Corners + E-slice)",
            "G2 → G3 (Tetrads + Edge Slices)",
            "G3 → G4 (Final Solve)"
        ]
        return names[phase]

    def _get_goal_check(self, phase: int):
        """Get goal checking function for a phase."""
        if phase == 0:
            # Phase 0: All edges oriented
            def check(cube: RubikCube) -> bool:
                coords = CubeCoordinates(cube)
                return coords.get_edge_orientation_coord() == 0
            return check

        elif phase == 1:
            # Phase 1: All corners oriented + E-slice edges in place
            def check(cube: RubikCube) -> bool:
                coords = CubeCoordinates(cube)
                co = coords.get_corner_orientation_coord()
                es = coords.get_e_slice_coord()
                # E-slice coord should be 0 when all E-edges are in E-slice
                # For now, simplified check
                return co == 0 and es == 0
            return check

        elif phase == 2:
            # Phase 2: Corners in tetrads + edges in slices
            def check(cube: RubikCube) -> bool:
                coords = CubeCoordinates(cube)
                ct = coords.get_corner_tetrad_coord()
                # Simplified: check if tetrad coordinate is 0
                return ct == 0
            return check

        elif phase == 3:
            # Phase 3: Fully solved
            def check(cube: RubikCube) -> bool:
                return cube.is_solved()
            return check

        else:
            raise ValueError(f"Invalid phase: {phase}")

    def _get_heuristic(self, phase: int):
        """Get heuristic function for a phase."""
        if self.use_pattern_databases and self._databases_loaded:
            # Use pattern database lookup
            db = self.pattern_databases.get_database(phase)

            def heuristic(cube: RubikCube) -> int:
                return db.lookup(cube)

            return heuristic
        else:
            # Default heuristic: return 0 (no information)
            def heuristic(cube: RubikCube) -> int:
                return 0

            return heuristic


def solve_cube(
    cube: RubikCube,
    use_pattern_databases: bool = True,
    verbose: bool = True
) -> Optional[List[str]]:
    """
    Convenience function to solve a cube with Thistlethwaite's algorithm.

    Args:
        cube: Cube to solve
        use_pattern_databases: Whether to use pattern databases
        verbose: Whether to print progress

    Returns:
        List of moves to solve the cube, or None if failed
    """
    solver = ThistlethwaiteSolver(use_pattern_databases=use_pattern_databases)
    result = solver.solve(cube, verbose=verbose)

    if result is None:
        return None

    all_moves, _ = result
    return all_moves
