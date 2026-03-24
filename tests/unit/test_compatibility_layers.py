"""Regression tests for legacy-facing compatibility surfaces."""

import importlib

from src.cube.rubik_cube import RubikCube
from src.kociemba.solver import KociembaSolver
from src.korf.solver import KorfSolver

visualize_3d_module = importlib.import_module("src.cube.visualize_3d")


def test_visualize_cube_3d_accepts_legacy_view_angles(monkeypatch):
    cube = RubikCube()
    captured = {}
    sentinel = object()

    def fake_visualize_3d(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return sentinel

    monkeypatch.setattr(visualize_3d_module, "visualize_3d", fake_visualize_3d)

    result = visualize_3d_module.visualize_cube_3d(
        cube,
        title="Legacy",
        view_angles=(30, 45),
        show=True,
    )

    assert result is sentinel
    assert captured["args"] == (cube,)
    assert captured["kwargs"]["title"] == "Legacy"
    assert captured["kwargs"]["elev"] == 30
    assert captured["kwargs"]["azim"] == 45
    assert captured["kwargs"]["show"] is True


def test_kociemba_constructor_depth_defaults_are_honored(monkeypatch):
    cube = RubikCube()
    cube.apply_move("R")
    captured = {}

    def fake_native(self, cube_arg, max_phase1_depth, max_phase2_depth, timeout, verbose):
        captured["max_phase1_depth"] = max_phase1_depth
        captured["max_phase2_depth"] = max_phase2_depth
        return (["R'"], [], ["R'"])

    monkeypatch.setattr(KociembaSolver, "_solve_with_native_backend", fake_native)

    solver = KociembaSolver(
        backend="native",
        max_depth_phase1=11,
        max_depth_phase2=17,
    )
    result = solver.solve(cube, verbose=False)

    assert result == (["R'"], [], ["R'"])
    assert captured == {
        "max_phase1_depth": 11,
        "max_phase2_depth": 17,
    }


def test_korf_solver_auto_falls_back_to_native_backend(monkeypatch):
    cube = RubikCube()
    solver = KorfSolver(backend="auto")

    def fake_optimal(cube_arg, verbose):
        solver.last_stats = {"timed_out": True}
        solver.backend_used = "optimal"
        return None

    def fake_native(cube_arg, verbose):
        solver.last_stats = {"timed_out": False}
        solver.backend_used = "native_exact"
        return ["U"]

    monkeypatch.setattr(solver, "_solve_with_optimal_backend", fake_optimal)
    monkeypatch.setattr(solver, "_solve_with_native_backend", fake_native)

    result = solver.solve(cube, verbose=False)

    assert result == ["U"]
    assert solver.backend_used == "native_exact"
    assert solver.get_statistics() == {"timed_out": False}
