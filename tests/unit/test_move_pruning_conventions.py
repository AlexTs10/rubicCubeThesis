"""Regression tests for opposite-face pruning conventions."""

from src.kociemba.solver import KociembaSolver
from src.korf.native_exact_solver import NativeExactSolver


def test_kociemba_opposite_face_pruning_convention():
    """Kociemba keeps D/U, B/F, R/L and prunes the reverse order."""
    solver = KociembaSolver(backend="internal")

    pruned = {
        ("U", "D"),
        ("F", "B"),
        ("L", "R"),
    }
    retained = {
        ("D", "U"),
        ("B", "F"),
        ("R", "L"),
    }

    for previous, current in pruned:
        assert solver._prunes_opposite_face_order(previous[0], current[0])

    for previous, current in retained:
        assert not solver._prunes_opposite_face_order(previous[0], current[0])


def test_native_exact_opposite_face_canonical_order():
    """Native exact pruning keeps U/D, F/B, L/R and prunes the reverse order."""
    solver = NativeExactSolver()

    for previous, current in [("D", "U"), ("B", "F"), ("R", "L")]:
        assert solver._is_redundant_move(previous, current)

    for previous, current in [("U", "D"), ("F", "B"), ("L", "R")]:
        assert not solver._is_redundant_move(previous, current)
