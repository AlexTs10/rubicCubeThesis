"""Unit tests for the native admissible coordinate heuristic."""

import pytest

from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import from_facelet_cube
from src.korf.corner_database import create_corner_database
from src.korf.native_coordinate_heuristic import NativeCoordinateHeuristic
from src.korf.native_exact_solver import NativeExactSolver


def _cube_from_moves(moves):
    cube = RubikCube()
    cube.apply_moves(moves)
    return cube


@pytest.fixture(scope="module")
def heuristic_cache_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("native_coordinate_heuristic")


@pytest.fixture(scope="module")
def coordinate_heuristic(heuristic_cache_dir):
    return NativeCoordinateHeuristic(
        cache_dir=str(heuristic_cache_dir),
        corner_db_path=None,
    )


class _DummyCornerDatabase:
    def get_corner_distance(self, cubie):
        return 0 if cubie.is_solved() else 5

    def get_statistics(self):
        return {
            "name": "corner",
            "size": 1,
            "storage_format": "byte",
            "max_depth": 5,
            "states_at_depth": {0: 1},
            "initialized_states": 1,
            "complete": True,
            "memory_bytes": 1,
        }


def test_coordinate_heuristic_is_zero_on_solved_cube(coordinate_heuristic):
    solved_cubie = from_facelet_cube(RubikCube())

    assert coordinate_heuristic(solved_cubie) == 0
    assert coordinate_heuristic.breakdown(solved_cubie) == {
        "corner_orientation": 0,
        "edge_orientation": 0,
        "udslice_position": 0,
        "corner_permutation": 0,
    }


def test_coordinate_heuristic_cache_round_trip(heuristic_cache_dir):
    cube = _cube_from_moves(["U", "R", "F"])
    cubie = from_facelet_cube(cube)

    heuristic1 = NativeCoordinateHeuristic(
        cache_dir=str(heuristic_cache_dir),
        corner_db_path=None,
    )
    breakdown1 = heuristic1.breakdown(cubie)

    heuristic2 = NativeCoordinateHeuristic(
        cache_dir=str(heuristic_cache_dir),
        corner_db_path=None,
    )
    breakdown2 = heuristic2.breakdown(cubie)

    assert breakdown1 == breakdown2
    assert len(list(heuristic_cache_dir.glob("*.pkl"))) == 4


def test_coordinate_heuristic_is_admissible_on_shallow_samples(coordinate_heuristic):
    samples = [
        (["U"], 1),
        (["U", "R"], 2),
        (["R", "U", "F"], 3),
        (["U2", "R", "F'", "L"], 4),
    ]

    for scramble, optimal_depth in samples:
        cubie = from_facelet_cube(_cube_from_moves(scramble))
        value = coordinate_heuristic(cubie)
        assert 0 <= value <= optimal_depth


def test_coordinate_heuristic_enables_native_solution_on_four_move_sample(coordinate_heuristic):
    cube = _cube_from_moves(["U2", "R", "F'", "L"])
    solver = NativeExactSolver(heuristic=coordinate_heuristic, max_depth=6, timeout=5.0)

    result = solver.solve(cube)

    assert result is not None
    solution, stats = result
    assert len(solution) == 4
    assert stats["optimal"] is True
    assert stats["heuristic"] == "NativeCoordinateHeuristic"


def test_coordinate_heuristic_includes_corner_pattern_db_when_injected(heuristic_cache_dir):
    cubie = from_facelet_cube(_cube_from_moves(["U", "R"]))
    heuristic = NativeCoordinateHeuristic(
        cache_dir=str(heuristic_cache_dir),
        corner_db=_DummyCornerDatabase(),
        corner_db_path=None,
    )

    breakdown = heuristic.breakdown(cubie)

    assert breakdown["corner_pattern_db"] == 5
    assert heuristic(cubie) == 5
    assert "corner_pattern_db" in heuristic.get_statistics()


def test_coordinate_heuristic_ignores_incomplete_corner_database(heuristic_cache_dir, tmp_path):
    corner_db_path = tmp_path / "corner_partial.pkl"
    create_corner_database(
        load_if_exists=False,
        save_path=str(corner_db_path),
        verbose=False,
        max_depth=1,
        frontier_chunk_size=64,
        move_cache_dir=str(tmp_path / "corner_cache"),
    )

    heuristic = NativeCoordinateHeuristic(
        cache_dir=str(heuristic_cache_dir),
        corner_db_path=str(corner_db_path),
    )
    breakdown = heuristic.breakdown(from_facelet_cube(_cube_from_moves(["U", "R"])))

    assert "corner_pattern_db" not in breakdown
