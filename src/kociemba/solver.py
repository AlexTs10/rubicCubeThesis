"""
Kociemba Two-Phase Algorithm Solver

This module implements Herbert Kociemba's two-phase algorithm for solving
the Rubik's Cube in near-optimal move counts.

Algorithm Overview:
1. Phase 1 (G0 -> G1): Orient all pieces and place UD-slice edges
   - Max 12 moves theoretically
   - Search space: 2.2 billion states
   - Uses IDA* with pruning tables

2. Phase 2 (G1 -> Solved): Solve within the restricted G1 group
   - Max 18 moves theoretically
   - Search space: 39,038,976,000 states before pruning
   - Uses only half-turns of F, B and quarter-turns of U, D, R, L

Total: Max 30 moves theoretically, typically <19 moves in practice
"""

import multiprocessing
import signal
import threading
import time
from contextlib import contextmanager
from typing import List, Optional, Tuple
from ..cube.rubik_cube import RubikCube
from .cubie import CubieCube, from_facelet_cube, apply_move_to_cubie
from .coord import CoordCube, get_corner_orientation, get_edge_orientation, get_udslice
from .coord import get_corner_permutation, get_edge_permutation, get_udslice_permutation
from .moves import ALL_MOVE_NAMES, PHASE2_MOVES, get_move_tables
from .pruning import get_pruning_tables

try:
    import kociemba as native_kociemba
except ImportError:  # pragma: no cover - optional dependency
    native_kociemba = None


class _NativeKociembaTimeout(RuntimeError):
    """Raised when the optional native backend exceeds its budget."""


def _native_kociemba_worker(cube_string: str, max_depth: int, conn) -> None:
    """Run the optional native backend in a child process."""
    try:
        if native_kociemba is None:
            conn.send(("error", "native kociemba backend is not installed"))
            return

        raw_solution = native_kociemba.solve(cube_string, max_depth=max_depth)
        conn.send(("ok", raw_solution))
    except Exception as exc:  # pragma: no cover - exercised via parent timeout/error handling
        conn.send(("error", repr(exc)))
    finally:
        conn.close()


_KOCIEMBA_FACE_ORDER = (0, 5, 2, 1, 4, 3)  # U, R, F, D, L, B
_KOCIEMBA_FACE_CHARS = {
    0: 'U',
    1: 'D',
    2: 'F',
    3: 'B',
    4: 'L',
    5: 'R',
}


class KociembaSolver:
    """
    Kociemba's two-phase algorithm solver.

    Achieves near-optimal solutions with scramble-dependent runtime.
    """

    def __init__(
        self,
        cache_dir: str = "data/kociemba",
        timeout_grace: float = 10.0,
        backend: str = "auto",
        native_timeout_threshold: float = 10.0,
        max_depth_phase1: Optional[int] = None,
        max_depth_phase2: Optional[int] = None,
    ):
        """
        Initialize Kociemba solver.

        Args:
            cache_dir: Directory to cache move and pruning tables
            timeout_grace: Extra seconds allowed beyond requested timeout
                before aborting search (softens strict cutoff)
            backend: One of 'auto', 'internal', or 'native'
            native_timeout_threshold: In auto mode, prefer the native
                `kociemba` package for short timeout budgets at or below
                this threshold
            max_depth_phase1: Optional legacy default for Phase 1 depth.
                Older notebooks passed this at construction time.
            max_depth_phase2: Optional legacy default for Phase 2 depth.
        """
        if backend not in {"auto", "internal", "native"}:
            raise ValueError("backend must be one of: auto, internal, native")

        self.cache_dir = cache_dir
        self.timeout_grace = timeout_grace
        self.backend = backend
        self.native_timeout_threshold = native_timeout_threshold
        self.default_max_phase1_depth = 12 if max_depth_phase1 is None else max_depth_phase1
        self.default_max_phase2_depth = 18 if max_depth_phase2 is None else max_depth_phase2
        self.move_tables = None
        self.pruning_tables = None
        self._initialized = False

        # Search statistics
        self.nodes_explored = 0
        self.last_backend_used: Optional[str] = None

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

    @contextmanager
    def _native_timeout_guard(self, timeout: float):
        """Enforce a wall-clock budget for the optional native backend."""
        if timeout <= 0:
            raise _NativeKociembaTimeout()

        if not hasattr(signal, "setitimer") or not hasattr(signal, "SIGALRM"):
            yield
            return

        if threading.current_thread() is not threading.main_thread():
            yield
            return

        def _raise_timeout(signum, frame):  # pragma: no cover - signal handler
            raise _NativeKociembaTimeout()

        previous_handler = signal.getsignal(signal.SIGALRM)
        previous_timer = signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, _raise_timeout)
        signal.setitimer(signal.ITIMER_REAL, timeout)

        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0.0)
            signal.signal(signal.SIGALRM, previous_handler)
            if previous_timer != (0.0, 0.0):
                signal.setitimer(signal.ITIMER_REAL, *previous_timer)

    def _solve_native_in_subprocess(self, cube_string: str, max_depth: int, timeout: float) -> str:
        """Fallback native execution for environments where signals are unavailable."""
        ctx = multiprocessing.get_context("spawn")
        parent_conn, child_conn = ctx.Pipe(duplex=False)
        process = ctx.Process(
            target=_native_kociemba_worker,
            args=(cube_string, max_depth, child_conn),
            daemon=True,
        )
        process.start()
        child_conn.close()

        try:
            process.join(timeout)
            if process.is_alive():
                process.terminate()
                process.join()
                raise _NativeKociembaTimeout()

            if not parent_conn.poll(0.1):
                raise RuntimeError("native kociemba backend exited without returning a solution")

            status, payload = parent_conn.recv()
            if status == "ok":
                return payload
            raise RuntimeError(f"native kociemba backend failed: {payload}")
        finally:
            parent_conn.close()

    @staticmethod
    def _cube_to_native_string(cube: RubikCube) -> str:
        """Convert the repo's facelet cube to the `kociemba` package format."""
        return "".join(
            _KOCIEMBA_FACE_CHARS[int(cube.state[face, idx])]
            for face in _KOCIEMBA_FACE_ORDER
            for idx in range(9)
        )

    @staticmethod
    def _split_solution_by_g1(
        cube: RubikCube,
        solution: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Recover a plausible phase split from a full move sequence.

        The native `kociemba` package returns only the combined solution.
        We scan for the earliest prefix that reaches G1 and whose suffix
        consists only of valid Phase 2 moves.
        """
        cubie = from_facelet_cube(cube)
        suffix_phase2_ok = [True] * (len(solution) + 1)
        seen_only_phase2 = True

        for idx in range(len(solution) - 1, -1, -1):
            seen_only_phase2 = seen_only_phase2 and solution[idx] in PHASE2_MOVES
            suffix_phase2_ok[idx] = seen_only_phase2

        if CoordCube(cubie).is_phase1_solved() and suffix_phase2_ok[0]:
            return [], solution

        for idx, move in enumerate(solution, start=1):
            cubie = apply_move_to_cubie(cubie, move)
            if CoordCube(cubie).is_phase1_solved() and suffix_phase2_ok[idx]:
                return solution[:idx], solution[idx:]

        # Fallback: preserve API shape even if no clean split is found.
        return solution, []

    def _solve_with_native_backend(
        self,
        cube: RubikCube,
        max_phase1_depth: int,
        max_phase2_depth: int,
        timeout: float,
        verbose: bool
    ) -> Optional[Tuple[List[str], List[str], List[str]]]:
        """Solve via the optional native `kociemba` package."""
        if native_kociemba is None:
            return None

        cube_string = self._cube_to_native_string(cube)
        max_depth = max_phase1_depth + max_phase2_depth
        native_budget = max(0.0, timeout) + self.timeout_grace

        try:
            if not hasattr(signal, "setitimer") or threading.current_thread() is not threading.main_thread():
                raw_solution = self._solve_native_in_subprocess(
                    cube_string,
                    max_depth,
                    native_budget,
                )
            else:
                with self._native_timeout_guard(native_budget):
                    raw_solution = native_kociemba.solve(cube_string, max_depth=max_depth)
        except _NativeKociembaTimeout:
            self.last_backend_used = "native_timeout"
            if verbose:
                print("Native kociemba backend timed out.")
            return None
        except Exception:
            self.last_backend_used = "native_error"
            if verbose:
                print("Native kociemba backend failed.")
            return None

        solution = [move for move in raw_solution.split() if move]

        test_cube = cube.copy()
        test_cube.apply_moves(solution)
        if not test_cube.is_solved():
            self.last_backend_used = "native_error"
            return None

        phase1_solution, phase2_solution = self._split_solution_by_g1(cube, solution)
        self.nodes_explored = 0
        self.last_backend_used = "native"

        if verbose:
            print("Using native kociemba backend.")

        return (solution, phase1_solution, phase2_solution)

    def solve(
        self,
        cube: RubikCube,
        max_phase1_depth: Optional[int] = None,
        max_phase2_depth: Optional[int] = None,
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
        if max_phase1_depth is None:
            max_phase1_depth = self.default_max_phase1_depth
        if max_phase2_depth is None:
            max_phase2_depth = self.default_max_phase2_depth

        if verbose:
            print("\n" + "="*70)
            print("KOCIEMBA'S TWO-PHASE ALGORITHM SOLVER")
            print("="*70)

        # Check if already solved
        if cube.is_solved():
            if verbose:
                print("Cube is already solved!")
            self.last_backend_used = "none"
            return ([], [], [])

        use_native_first = (
            self.backend == "native" or
            (
                self.backend == "auto" and
                native_kociemba is not None and
                timeout <= self.native_timeout_threshold
            )
        )

        if use_native_first:
            native_result = self._solve_with_native_backend(
                cube, max_phase1_depth, max_phase2_depth, timeout, verbose
            )
            if native_result is not None:
                return native_result
            if self.last_backend_used == "native_timeout":
                return None
            if self.backend == "native":
                return None

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
            if self.backend == "auto":
                native_result = self._solve_with_native_backend(
                    cube, max_phase1_depth, max_phase2_depth, timeout, verbose
                )
                if native_result is not None:
                    return native_result
                if self.last_backend_used == "native_timeout":
                    return None
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
            if self.backend == "auto":
                native_result = self._solve_with_native_backend(
                    cube, max_phase1_depth, max_phase2_depth, timeout, verbose
                )
                if native_result is not None:
                    return native_result
                if self.last_backend_used == "native_timeout":
                    return None
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
            if self.backend == "auto":
                native_result = self._solve_with_native_backend(
                    cube, max_phase1_depth, max_phase2_depth, timeout, verbose
                )
                if native_result is not None:
                    return native_result
                if self.last_backend_used == "native_timeout":
                    return None
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

        self.last_backend_used = "internal"
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
