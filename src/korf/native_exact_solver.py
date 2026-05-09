"""
Native Exact Solver (First Slice)

This module provides the first native exact-solver path for the repository.
It uses cubie-level IDA* search with only admissible heuristics. By default it
loads the repository's native admissible heuristic stack lazily; callers may
override that with any admissible cubie heuristic, including zero for shallow
proof tests.

Important semantics:
- A returned solution is exact under the repository's move metric.
- `None` means the run was incomplete (timeout or depth limit), not "unsolved".
- This module does not call the external optimal-solver backend.
"""

from __future__ import annotations

import math
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

from ..cube.rubik_cube import RubikCube
from ..kociemba.cubie import ALL_MOVES, CubieCube, from_facelet_cube
from .corner_database import CornerPatternDatabase
from .native_coordinate_heuristic import NativeCoordinateHeuristic

MOVE_ORDER = [
    "U", "U'", "U2",
    "D", "D'", "D2",
    "F", "F'", "F2",
    "B", "B'", "B2",
    "L", "L'", "L2",
    "R", "R'", "R2",
]

_TIMEOUT = object()
_SearchResult = Union[List[str], int, object]
_CubieHeuristic = Callable[[CubieCube], int]


def zero_heuristic(_: CubieCube) -> int:
    """Trivial admissible heuristic."""
    return 0


def make_corner_heuristic(corner_db: CornerPatternDatabase) -> _CubieHeuristic:
    """Create an admissible heuristic from a loaded corner database."""
    return corner_db.get_corner_distance


def _state_key(cubie: CubieCube) -> bytes:
    """Collision-free key for exact path-cycle checks."""
    return (
        cubie.corner_perm.tobytes()
        + cubie.corner_orient.tobytes()
        + cubie.edge_perm.tobytes()
        + cubie.edge_orient.tobytes()
    )


class NativeExactSolver:
    """
    Native exact solver using cubie-level IDA*.

    This first slice is designed to be correct before it is fast.
    """

    def __init__(
        self,
        heuristic: Optional[_CubieHeuristic] = None,
        max_depth: int = 20,
        timeout: float = 60.0,
        move_order: Optional[Sequence[str]] = None,
        heuristic_cache_dir: str | None = None,
    ):
        """
        Initialize the native exact solver.

        Args:
            heuristic: Admissible cubie heuristic. If omitted, the repository's
                native admissible heuristic stack is loaded lazily.
            max_depth: Search depth limit in the repository's move metric.
            timeout: Maximum wall-clock time in seconds.
            move_order: Optional deterministic move order.
        """
        self.heuristic = heuristic
        self.max_depth = max_depth
        self.timeout = timeout
        self.move_order = list(move_order or MOVE_ORDER)
        self.heuristic_cache_dir = heuristic_cache_dir

        self.nodes_explored = 0
        self.iterations = 0
        self.start_time = 0.0
        self.last_stats: Dict[str, Any] = {}
        self._deadline: Optional[float] = None
        self._time_fn = time.monotonic

    def solve(
        self,
        cube: Union[RubikCube, CubieCube],
        verbose: bool = False,
        timeout: Optional[float] = None,
    ) -> Optional[Tuple[List[str], Dict[str, Any]]]:
        """
        Find an exact solution for the given cube state.

        Args:
            cube: Facelet or cubie representation.
            verbose: Unused in the first slice; accepted for API parity.
            timeout: Optional override for the configured timeout.

        Returns:
            `(solution_moves, stats)` if an exact solution was found.
            `None` if the run timed out or hit the configured depth limit.
        """
        del verbose  # API parity only.

        self.nodes_explored = 0
        self.iterations = 0
        self.start_time = time.time()

        deadline_timeout = self.timeout if timeout is None else timeout
        self._deadline = None if deadline_timeout is None else self._time_fn() + deadline_timeout

        start_cubie = self._coerce_cubie(cube)
        if start_cubie.is_solved():
            stats = self._build_stats(
                solved=True,
                solution=[],
                timed_out=False,
                depth_limit_reached=False,
                initial_bound=0,
                final_bound=0,
            )
            self.last_stats = stats.copy()
            return [], stats

        initial_bound = self._heuristic_value(start_cubie)
        bound = initial_bound
        path: List[str] = []
        path_states: Set[bytes] = {_state_key(start_cubie)}

        while bound <= self.max_depth:
            self.iterations += 1
            result = self._search(
                cubie=start_cubie,
                g_cost=0,
                bound=bound,
                path=path,
                path_states=path_states,
                last_move=None,
            )

            if result is _TIMEOUT:
                stats = self._build_stats(
                    solved=False,
                    solution=None,
                    timed_out=True,
                    depth_limit_reached=False,
                    initial_bound=initial_bound,
                    final_bound=bound,
                )
                self.last_stats = stats.copy()
                return None

            if isinstance(result, list):
                stats = self._build_stats(
                    solved=True,
                    solution=result,
                    timed_out=False,
                    depth_limit_reached=False,
                    initial_bound=initial_bound,
                    final_bound=bound,
                )
                self.last_stats = stats.copy()
                return result, stats

            if result == math.inf:
                break

            bound = result

        stats = self._build_stats(
            solved=False,
            solution=None,
            timed_out=False,
            depth_limit_reached=True,
            initial_bound=initial_bound,
            final_bound=bound,
        )
        self.last_stats = stats.copy()
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Return statistics from the last solve attempt."""
        return self.last_stats.copy()

    def _search(
        self,
        cubie: CubieCube,
        g_cost: int,
        bound: int,
        path: List[str],
        path_states: Set[bytes],
        last_move: Optional[str],
    ) -> _SearchResult:
        self.nodes_explored += 1

        if self._is_timed_out():
            return _TIMEOUT

        heuristic_value = self._heuristic_value(cubie)
        f_value = g_cost + heuristic_value
        if f_value > bound:
            return f_value

        if cubie.is_solved():
            return path.copy()

        if g_cost >= self.max_depth:
            return math.inf

        min_next_bound = math.inf

        for move in self.move_order:
            if last_move is not None and self._is_redundant_move(last_move, move):
                continue

            next_cubie = cubie.multiply(ALL_MOVES[move])
            next_key = _state_key(next_cubie)
            if next_key in path_states:
                continue

            path.append(move)
            path_states.add(next_key)
            result = self._search(
                cubie=next_cubie,
                g_cost=g_cost + 1,
                bound=bound,
                path=path,
                path_states=path_states,
                last_move=move,
            )
            path_states.remove(next_key)
            path.pop()

            if result is _TIMEOUT:
                return _TIMEOUT
            if isinstance(result, list):
                return result
            if result < min_next_bound:
                min_next_bound = result

        return min_next_bound

    def _heuristic_value(self, cubie: CubieCube) -> int:
        """Evaluate the configured heuristic with exact-path constraints."""
        self._ensure_heuristic()
        value = self.heuristic(cubie)
        if isinstance(value, bool) or int(value) != value or value < 0:
            raise ValueError(f"Heuristic must return a non-negative integer, got {value!r}")
        value = int(value)
        if value < 0:
            raise ValueError(f"Heuristic returned negative value {value}")
        return value

    def _is_timed_out(self) -> bool:
        """Check whether the current search exceeded its deadline."""
        return self._deadline is not None and self._time_fn() > self._deadline

    @staticmethod
    def _coerce_cubie(cube: Union[RubikCube, CubieCube]) -> CubieCube:
        """Convert supported cube inputs into cubie representation."""
        if isinstance(cube, CubieCube):
            return cube.copy()
        if isinstance(cube, RubikCube):
            return from_facelet_cube(cube)
        raise TypeError(f"Unsupported cube type: {type(cube)!r}")

    @staticmethod
    def _is_redundant_move(previous_move: str, current_move: str) -> bool:
        """
        Prune exact-search branches that are redundant by move commutation rules.

        Safe rules used in the first slice:
        - same face twice in a row,
        - opposite faces in non-canonical order.
        """
        previous_face = previous_move[0]
        current_face = current_move[0]

        if previous_face == current_face:
            return True

        opposite_pairs = [("U", "D"), ("F", "B"), ("L", "R")]
        for canonical_first, canonical_second in opposite_pairs:
            if previous_face == canonical_second and current_face == canonical_first:
                return True
        return False

    def _build_stats(
        self,
        solved: bool,
        solution: Optional[List[str]],
        timed_out: bool,
        depth_limit_reached: bool,
        initial_bound: int,
        final_bound: int,
    ) -> Dict[str, Any]:
        """Assemble a consistent stats dictionary for callers and tests."""
        elapsed = time.time() - self.start_time if self.start_time else 0.0
        heuristic_name = self._heuristic_name()

        return {
            "time": elapsed,
            "moves": len(solution) if solution is not None else None,
            "solution_length": len(solution) if solution is not None else None,
            "optimal": solved,
            "completed": solved,
            "timed_out": timed_out,
            "depth_limit_reached": depth_limit_reached,
            "nodes_explored": self.nodes_explored,
            "iterations": self.iterations,
            "initial_bound": initial_bound,
            "final_bound": final_bound,
            "max_depth": self.max_depth,
            "max_depth_limit": self.max_depth,
            "heuristic": heuristic_name,
            "heuristic_name": heuristic_name,
        }

    def _ensure_heuristic(self) -> None:
        """Load the default native admissible heuristic lazily when needed."""
        if self.heuristic is None:
            self.heuristic = NativeCoordinateHeuristic(cache_dir=self.heuristic_cache_dir)

    def _heuristic_name(self) -> str:
        """Return a stable name for the configured or default heuristic."""
        if self.heuristic is None:
            return NativeCoordinateHeuristic.__name__
        return getattr(self.heuristic, "__name__", self.heuristic.__class__.__name__)


def solve_exact_native(
    cube: Union[RubikCube, CubieCube],
    *,
    heuristic: Optional[_CubieHeuristic] = None,
    max_depth: int = 20,
    timeout: float = 60.0,
    heuristic_cache_dir: str = "data/pattern_databases/native_exact",
) -> Optional[Tuple[List[str], Dict[str, Any]]]:
    """Convenience wrapper returning the native solution and stats."""
    solver = NativeExactSolver(
        heuristic=heuristic,
        max_depth=max_depth,
        timeout=timeout,
        heuristic_cache_dir=heuristic_cache_dir,
    )
    return solver.solve(cube)


def solve_optimal_native(
    cube: Union[RubikCube, CubieCube],
    *,
    heuristic: Optional[_CubieHeuristic] = None,
    max_depth: int = 20,
    timeout: float = 60.0,
    heuristic_cache_dir: str = "data/pattern_databases/native_exact",
) -> Optional[List[str]]:
    """Convenience wrapper returning only the optimal move sequence."""
    result = solve_exact_native(
        cube,
        heuristic=heuristic,
        max_depth=max_depth,
        timeout=timeout,
        heuristic_cache_dir=heuristic_cache_dir,
    )
    if result is None:
        return None
    solution, _ = result
    return solution


def optimal_distance_native(
    cube: Union[RubikCube, CubieCube],
    *,
    heuristic: Optional[_CubieHeuristic] = None,
    max_depth: int = 20,
    timeout: float = 60.0,
    heuristic_cache_dir: str = "data/pattern_databases/native_exact",
) -> Optional[int]:
    """Return the exact move distance when the native search completes."""
    solution = solve_optimal_native(
        cube,
        heuristic=heuristic,
        max_depth=max_depth,
        timeout=timeout,
        heuristic_cache_dir=heuristic_cache_dir,
    )
    if solution is None:
        return None
    return len(solution)
