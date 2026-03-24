"""Unit tests for the first native exact solver slice."""

import pytest

from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import from_facelet_cube
from src.korf.native_exact_solver import (
    NativeExactSolver,
    optimal_distance_native,
    solve_exact_native,
    solve_optimal_native,
    zero_heuristic,
)


def _cube_from_moves(moves):
    cube = RubikCube()
    cube.apply_moves(moves)
    return cube


def _assert_solution_solves(scramble, solution):
    cube = _cube_from_moves(scramble)
    cube.apply_moves(solution)
    assert cube.is_solved()


def test_native_exact_solver_solves_solved_cube():
    cube = RubikCube()
    solver = NativeExactSolver(heuristic=zero_heuristic, max_depth=4, timeout=5.0)

    result = solver.solve(cube)

    assert result is not None
    solution, stats = result
    assert solution == []
    assert stats["optimal"] is True
    assert stats["completed"] is True
    assert stats["moves"] == 0


@pytest.mark.parametrize(
    "move",
    ["U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "L", "L'", "L2", "R", "R'", "R2"],
)
def test_native_exact_solver_single_move_states_are_exact(move):
    cube = _cube_from_moves([move])
    solver = NativeExactSolver(heuristic=zero_heuristic, max_depth=3, timeout=5.0)

    result = solver.solve(cube)

    assert result is not None
    solution, stats = result
    assert len(solution) == 1
    assert stats["optimal"] is True
    assert stats["moves"] == 1
    _assert_solution_solves([move], solution)


@pytest.mark.parametrize(
    "scramble",
    [
        ["R", "U"],
        ["F", "R2"],
        ["L", "B'"],
        ["U2", "R"],
        ["D", "L2"],
    ],
)
def test_native_exact_solver_two_move_states_are_exact(scramble):
    cube = _cube_from_moves(scramble)
    solver = NativeExactSolver(heuristic=zero_heuristic, max_depth=4, timeout=5.0)

    result = solver.solve(cube)

    assert result is not None
    solution, stats = result
    assert len(solution) == 2
    assert stats["optimal"] is True
    assert stats["moves"] == 2
    _assert_solution_solves(scramble, solution)


def test_native_exact_solver_three_move_state():
    scramble = ["R", "U", "F"]
    cube = _cube_from_moves(scramble)
    solver = NativeExactSolver(heuristic=zero_heuristic, max_depth=5, timeout=10.0)

    result = solver.solve(cube)

    assert result is not None
    solution, stats = result
    assert len(solution) == 3
    assert stats["optimal"] is True
    assert stats["moves"] == 3
    _assert_solution_solves(scramble, solution)


def test_native_exact_solver_accepts_cubie_input():
    scramble = ["R", "U"]
    cubie = from_facelet_cube(_cube_from_moves(scramble))
    solver = NativeExactSolver(heuristic=zero_heuristic, max_depth=4, timeout=5.0)

    result = solver.solve(cubie)

    assert result is not None
    solution, stats = result
    assert len(solution) == 2
    assert stats["optimal"] is True


def test_depth_limit_is_reported_as_incomplete():
    cube = _cube_from_moves(["R", "U"])
    solver = NativeExactSolver(heuristic=zero_heuristic, max_depth=1, timeout=5.0)

    result = solver.solve(cube)

    assert result is None
    stats = solver.get_statistics()
    assert stats["optimal"] is False
    assert stats["completed"] is False
    assert stats["depth_limit_reached"] is True
    assert stats["timed_out"] is False


def test_optimal_distance_matches_solution_length():
    scramble = ["R", "U", "F"]
    cube = _cube_from_moves(scramble)

    solution = solve_optimal_native(cube, heuristic=zero_heuristic, max_depth=5, timeout=10.0)
    distance = optimal_distance_native(cube, heuristic=zero_heuristic, max_depth=5, timeout=10.0)

    assert solution is not None
    assert distance == len(solution) == 3


def test_solve_exact_native_returns_solution_and_stats():
    cube = _cube_from_moves(["R", "U"])

    result = solve_exact_native(cube, heuristic=zero_heuristic, max_depth=4, timeout=5.0)

    assert result is not None
    solution, stats = result
    assert len(solution) == 2
    assert stats["solution_length"] == 2
    assert stats["heuristic"] == "zero_heuristic"


def test_native_exact_solver_rejects_non_integer_heuristics():
    cube = _cube_from_moves(["U"])
    solver = NativeExactSolver(heuristic=lambda _: 0.5, max_depth=3, timeout=5.0)

    with pytest.raises(ValueError, match="non-negative integer"):
        solver.solve(cube)
