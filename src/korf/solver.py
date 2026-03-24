"""
Compatibility wrapper for legacy ``src.korf.solver`` imports.

Older demos and notebooks referenced a ``KorfSolver`` class that returned only
the move sequence. The current repository exposes a richer exact backend API,
so this module provides a thin adapter without changing the newer interfaces.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..cube.rubik_cube import RubikCube
from .native_coordinate_heuristic import NativeCoordinateHeuristic
from .native_exact_solver import NativeExactSolver
from .optimal_solver import KorfOptimalSolver


class KorfSolver:
    """
    Backward-compatible solver facade for notebooks and demos.

    In ``auto`` mode, prefer the external exact backend when available and fall
    back to the repository's native exact solver otherwise.
    """

    def __init__(
        self,
        max_depth: int = 20,
        timeout: Optional[float] = None,
        backend: str = "auto",
        heuristic_cache_dir: str = "data/pattern_databases/native_exact",
    ) -> None:
        if backend not in {"auto", "optimal", "native"}:
            raise ValueError("backend must be one of: auto, optimal, native")

        self.max_depth = max_depth
        self.timeout = timeout
        self.backend = backend
        self.heuristic_cache_dir = heuristic_cache_dir
        self.backend_used: Optional[str] = None
        self.last_stats: Dict[str, object] = {}

    def _solve_with_optimal_backend(
        self,
        cube: RubikCube,
        verbose: bool,
    ) -> Optional[List[str]]:
        try:
            solver = KorfOptimalSolver()
        except ImportError:
            return None

        result = solver.solve(cube, verbose=verbose, timeout=self.timeout)
        self.last_stats = solver.last_stats.copy()
        self.backend_used = "optimal"
        if result is None:
            return None

        solution, _stats = result
        return solution

    def _solve_with_native_backend(
        self,
        cube: RubikCube,
        verbose: bool,
    ) -> Optional[List[str]]:
        heuristic = NativeCoordinateHeuristic(cache_dir=self.heuristic_cache_dir)
        solver = NativeExactSolver(
            heuristic=heuristic,
            max_depth=self.max_depth,
            timeout=60.0 if self.timeout is None else self.timeout,
            heuristic_cache_dir=self.heuristic_cache_dir,
        )
        result = solver.solve(cube, verbose=verbose, timeout=self.timeout)
        self.last_stats = solver.get_statistics()
        self.backend_used = "native_exact"
        if result is None:
            return None

        solution, _stats = result
        return solution

    def solve(self, cube: RubikCube, verbose: bool = True) -> Optional[List[str]]:
        """Return only the move sequence, matching the historical notebook API."""
        if self.backend in {"auto", "optimal"}:
            solution = self._solve_with_optimal_backend(cube, verbose=verbose)
            if solution is not None or self.backend == "optimal":
                return solution

        return self._solve_with_native_backend(cube, verbose=verbose)

    def get_statistics(self) -> Dict[str, object]:
        """Expose the most recent backend stats to legacy callers."""
        return self.last_stats.copy()
