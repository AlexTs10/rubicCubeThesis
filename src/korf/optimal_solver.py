"""
Wrapper around an optional Korf-style exact backend.

This module does not implement the heavy optimal-search engine directly. It
loads the optional `RubikOptimal` package lazily and provides repository-local
timeout handling, cube-state conversion, statistics extraction, and result
normalization for the thesis benchmark path.

The backend uses IDA* with pattern databases and returns optimal solutions when
it completes. Runtime depends on the installed backend, Python implementation,
generated tables, and input depth, so thesis-facing performance claims should
come from the checked-in benchmark artifacts rather than this docstring.

References:
- Korf, R. (1997). "Finding Optimal Solutions to Rubik's Cube Using Pattern Databases"
- https://github.com/hkociemba/RubiksCube-OptimalSolver
"""

import io
import multiprocessing
import re
import signal
import time
from contextlib import redirect_stdout
from importlib import import_module
from importlib import util as importlib_util
from typing import List, Optional, Tuple
import numpy as np

_BACKEND_PACKAGE_NAMES = ("optimal", "RubikOptimal")
_BACKEND_MODULE_NAMES = ("optimal.solver", "RubikOptimal.solver")
_HAS_REALTIME_TIMER = all(
    hasattr(signal, attr)
    for attr in ("SIGALRM", "setitimer", "ITIMER_REAL")
)


def _backend_available() -> bool:
    """Check whether a supported RubikOptimal backend is installed."""
    return any(importlib_util.find_spec(name) is not None for name in _BACKEND_PACKAGE_NAMES)


def _load_backend_module():
    """Import the RubikOptimal backend lazily to avoid heavy import-time work."""
    for package_name, module_name in zip(_BACKEND_PACKAGE_NAMES, _BACKEND_MODULE_NAMES):
        if importlib_util.find_spec(package_name) is None:
            continue
        try:
            return import_module(module_name)
        except ImportError:
            continue
    return None


OPTIMAL_AVAILABLE = _backend_available()

from ..cube.rubik_cube import RubikCube, Face


def _optimal_backend_worker(cube_string: str, conn) -> None:
    """Run the optional optimal backend in a subprocess for portable timeouts."""
    backend_output = io.StringIO()
    try:
        backend = _load_backend_module()
        if backend is None:
            conn.send(("error", "RubikOptimal backend is not installed", backend_output.getvalue()))
            return
        with redirect_stdout(backend_output):
            result = backend.solve(cube_string)
        conn.send(("ok", result, backend_output.getvalue()))
    except Exception as exc:  # pragma: no cover - defensive child-process path
        conn.send(("error", repr(exc), backend_output.getvalue()))
    finally:
        conn.close()


class KorfOptimalSolver:
    """
    Adapter for the optional RubikOptimal exact backend.

    Completed backend runs return shortest solutions. Difficult positions may
    exceed the configured timeout or require backend-generated tables.
    """

    def __init__(self):
        """Initialize the optimal solver."""
        self._backend = _load_backend_module()
        if self._backend is None:
            raise ImportError(
                "Optional RubikOptimal backend is not installed or not importable. "
                "Install with: pip install RubikOptimal\n"
                "If you are using a local checkout, ensure the solver is importable "
                "as `optimal.solver`."
            )

        # Statistics
        self.solve_count = 0
        self.total_time = 0.0
        self.total_moves = 0
        self.timeout_supported = _HAS_REALTIME_TIMER
        self.last_stats = {}

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
            if len(token) != 2:
                raise ValueError(f"Invalid backend move token: {token!r}")

            face = token[0]  # U, R, F, D, L, or B
            rotation = token[1]  # 1, 2, or 3
            if face not in {'U', 'R', 'F', 'D', 'L', 'B'}:
                raise ValueError(f"Invalid backend move face: {token!r}")

            if rotation == '1':
                moves.append(face)
            elif rotation == '2':
                moves.append(face + '2')
            elif rotation == '3':
                moves.append(face + "'")
            else:
                raise ValueError(f"Invalid backend move rotation: {token!r}")

        return moves

    def _solve_backend_with_process_timeout(self, cube_string: str, timeout: float) -> Tuple[str, str]:
        """Invoke the real backend in a subprocess and enforce a wall-clock timeout."""
        ctx = multiprocessing.get_context("spawn")
        parent_conn, child_conn = ctx.Pipe(duplex=False)
        process = ctx.Process(
            target=_optimal_backend_worker,
            args=(cube_string, child_conn),
            daemon=True,
        )
        process.start()
        child_conn.close()

        try:
            if parent_conn.poll(timeout):
                message = parent_conn.recv()
            else:
                process.terminate()
                process.join(timeout=1.0)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=1.0)
                raise TimeoutError("Korf optimal solver exceeded timeout")
        finally:
            parent_conn.close()

        process.join(timeout=1.0)
        status, payload, child_stdout = message
        if status == "ok":
            return payload, child_stdout
        raise RuntimeError(payload)

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
            timeout: Maximum time in seconds

        Returns:
            Tuple of (solution_moves, stats_dict) or None if failed
            - solution_moves: List of moves in Singmaster notation
            - stats_dict: Dictionary with solving statistics
        """
        if verbose:
            print("\n" + "="*70)
            print("EXTERNAL RUBIKOPTIMAL EXACT BACKEND WRAPPER")
            print("="*70)
            print("Backend: optional RubikOptimal package")
            print("WARNING: This backend returns optimal solutions when it completes but may")
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
        backend_output = io.StringIO()

        try:
            def _timeout_handler(signum, frame):  # pragma: no cover - exercised via signal delivery
                raise TimeoutError("Korf optimal solver exceeded timeout")

            def _invoke_backend() -> str:
                with redirect_stdout(backend_output):
                    result = self._backend.solve(cube_string)
                if verbose and backend_output.getvalue():
                    print(backend_output.getvalue(), end="")
                return result

            if timeout is not None and self.timeout_supported:
                previous_handler = signal.getsignal(signal.SIGALRM)
                signal.signal(signal.SIGALRM, _timeout_handler)
                signal.setitimer(signal.ITIMER_REAL, timeout)
                try:
                    solution_str = _invoke_backend()
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0.0)
                    signal.signal(signal.SIGALRM, previous_handler)
            elif timeout is not None:
                solution_str, child_stdout = self._solve_backend_with_process_timeout(cube_string, timeout)
                backend_output.write(child_stdout)
                if verbose and child_stdout:
                    print(child_stdout, end="")
            else:
                solution_str = _invoke_backend()

            solve_time = time.time() - start_time
            backend_stats = self._parse_backend_output(backend_output.getvalue())

            if solution_str is None:
                self.last_stats = {
                    'time': solve_time,
                    'optimal': False,
                    'timed_out': False,
                    **backend_stats,
                }
                if verbose:
                    print("\n❌ Failed to find solution")
                return None

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
                'raw_solution': solution_str,
                'timed_out': False,
                'verified': False,
                **backend_stats,
            }

            # Verify every backend result before exposing it through the public API.
            test_cube = cube.copy()
            test_cube.apply_moves(solution)
            if not test_cube.is_solved():
                stats['optimal'] = False
                stats['error'] = 'Backend solution did not solve the cube'
                self.last_stats = stats.copy()
                if verbose:
                    print("  WARNING: backend solution does not solve the cube")
                return None

            stats['verified'] = True
            self.last_stats = stats.copy()

            if verbose:
                print(f"\n✓ Optimal solution found!")
                print(f"  Solution: {' '.join(solution)}")
                print(f"  Moves: {len(solution)}")
                print(f"  Time: {solve_time:.2f} seconds")
                print(f"  Raw output: {solution_str}")

                print(f"  ✓ Solution verified!")

            return (solution, stats)

        except TimeoutError:
            solve_time = time.time() - start_time
            backend_stats = self._parse_backend_output(backend_output.getvalue())
            self.last_stats = {
                'time': solve_time,
                'optimal': False,
                'timed_out': True,
                **backend_stats,
            }
            if verbose:
                print(f"\n❌ Timeout after {solve_time:.2f} seconds")
            return None
        except Exception as e:
            self.last_stats = {
                'time': time.time() - start_time,
                'optimal': False,
                'timed_out': False,
                'error': str(e),
            }
            if verbose:
                print(f"\n❌ Error during solving: {e}")
            return None

    @staticmethod
    def _parse_backend_output(output: str) -> dict:
        """Extract useful metrics from the backend's progress prints."""
        stats = {}

        match = re.search(r"nodes generated:\s*(\d+)", output)
        if match:
            nodes_generated = int(match.group(1))
            stats['nodes_explored'] = nodes_generated
            stats['nodes_generated'] = nodes_generated

        depth_matches = re.findall(
            r"depth\s+(\d+)\s+done in\s+([0-9.]+)\s+s,\s+(\d+)\s+nodes generated",
            output,
        )
        if depth_matches:
            stats['depth_progress'] = [
                {
                    'depth': int(depth),
                    'seconds': float(seconds),
                    'nodes_generated': int(nodes),
                }
                for depth, seconds, nodes in depth_matches
            ]

        return stats

    def get_statistics(self) -> dict:
        """
        Get solving statistics.

        Returns:
            Dictionary with average time, moves, etc.
        """
        if self.solve_count == 0:
            base_stats = {
                'cubes_solved': 0,
                'avg_time': 0.0,
                'avg_moves': 0.0,
                'total_time': 0.0,
            }
        else:
            base_stats = {
                'cubes_solved': self.solve_count,
                'avg_time': self.total_time / self.solve_count,
                'avg_moves': self.total_moves / self.solve_count,
                'total_time': self.total_time,
            }

        base_stats.update(
            {
                'timeout_supported': self.timeout_supported,
                'nodes_explored': self.last_stats.get('nodes_explored'),
                'last_time': self.last_stats.get('time', 0.0),
                'last_timed_out': self.last_stats.get('timed_out', False),
            }
        )
        return base_stats


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
