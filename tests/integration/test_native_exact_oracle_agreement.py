"""Opt-in agreement tests between the native exact solver and the external oracle."""

import os

import pytest

from src.cube.rubik_cube import RubikCube
from src.korf.native_coordinate_heuristic import NativeCoordinateHeuristic
from src.korf.native_exact_solver import solve_exact_native
from src.korf.optimal_solver import KorfOptimalSolver, OPTIMAL_AVAILABLE

pytestmark = pytest.mark.external


def _cube_from_moves(moves):
    cube = RubikCube()
    cube.apply_moves(moves)
    return cube


@pytest.mark.skipif(
    not OPTIMAL_AVAILABLE or os.environ.get("RUN_NATIVE_ORACLE_TESTS") != "1",
    reason="external oracle validation is opt-in and requires the RubikOptimal backend",
)
def test_native_exact_solver_matches_oracle_on_shallow_samples():
    oracle = KorfOptimalSolver()
    heuristic = NativeCoordinateHeuristic()
    samples = [
        ["U"],
        ["U", "R"],
        ["R", "U", "F"],
        ["U2", "R", "F'", "L"],
        ["U2", "R", "F'", "L", "B"],
        ["U", "R2", "F", "L'", "D"],
    ]

    for scramble in samples:
        cube = _cube_from_moves(scramble)

        native_result = solve_exact_native(cube, heuristic=heuristic, max_depth=7, timeout=20.0)
        oracle_result = oracle.solve(cube, verbose=False, timeout=20.0)

        assert native_result is not None, f"native solver did not complete for {scramble}"
        assert oracle_result is not None, f"oracle did not complete for {scramble}"

        native_moves, native_stats = native_result
        oracle_moves, oracle_stats = oracle_result

        assert len(native_moves) == len(oracle_moves)
        assert native_stats["solution_length"] == oracle_stats["moves"]
