"""Unit tests for the optional Korf optimal-solver wrapper."""

import signal
import time

import pytest

from src.cube.rubik_cube import RubikCube
from src.korf.optimal_solver import KorfOptimalSolver


def _build_solver(backend, timeout_supported: bool = True) -> KorfOptimalSolver:
    """Create a lightweight KorfOptimalSolver instance around a fake backend."""
    solver = object.__new__(KorfOptimalSolver)
    solver._backend = backend
    solver.solve_count = 0
    solver.total_time = 0.0
    solver.total_moves = 0
    solver.timeout_supported = timeout_supported
    solver.last_stats = {}
    return solver


class _ReportingBackend:
    """Fake backend that prints progress and returns a 1-move solution."""

    def solve(self, cubestring):
        print("depth 14 done in 0.50 s, 100 nodes generated, about 200 nodes/s")
        print("total time: 1.50 s, nodes generated: 300")
        return "U3 (1f*)"


class _SlowBackend:
    """Fake backend that should be interrupted by the wrapper timeout."""

    def solve(self, cubestring):
        time.sleep(0.2)
        return "U3 (1f*)"


class _MalformedBackend:
    """Fake backend that returns a token the wrapper must reject."""

    def solve(self, cubestring):
        return "UX (1f*)"


class _WrongSolutionBackend:
    """Fake backend that returns a syntactically valid but incorrect solution."""

    def solve(self, cubestring):
        return "U1 (1f*)"


def test_optimal_solver_parses_backend_node_counts():
    """The wrapper should recover node counts from the backend logs."""
    cube = RubikCube()
    cube.apply_move("U")

    solver = _build_solver(_ReportingBackend())
    solution, stats = solver.solve(cube, verbose=False, timeout=1.0)

    assert solution == ["U'"]
    assert stats["nodes_explored"] == 300
    assert solver.get_statistics()["nodes_explored"] == 300
    assert stats["verified"] is True


def test_optimal_solver_rejects_malformed_backend_output_quietly():
    """Malformed backend output should fail closed even when verbose=False."""
    cube = RubikCube()
    cube.apply_move("U")

    solver = _build_solver(_MalformedBackend())
    result = solver.solve(cube, verbose=False)

    assert result is None
    assert "Invalid backend move rotation" in solver.last_stats["error"]


def test_optimal_solver_rejects_non_solving_backend_output_quietly():
    """A parsed solution is not returned unless it actually solves the cube."""
    cube = RubikCube()
    cube.apply_move("U")

    solver = _build_solver(_WrongSolutionBackend())
    result = solver.solve(cube, verbose=False)

    assert result is None
    assert solver.last_stats["verified"] is False
    assert solver.last_stats["optimal"] is False


@pytest.mark.skipif(
    not all(hasattr(signal, attr) for attr in ("SIGALRM", "setitimer", "ITIMER_REAL")),
    reason="real-time signal timer not available on this platform",
)
def test_optimal_solver_enforces_timeout():
    """The wrapper should stop slow backends when a timeout is provided."""
    cube = RubikCube()
    cube.apply_move("U")

    solver = _build_solver(_SlowBackend(), timeout_supported=True)
    result = solver.solve(cube, verbose=False, timeout=0.05)

    assert result is None
    stats = solver.get_statistics()
    assert stats["last_timed_out"] is True
