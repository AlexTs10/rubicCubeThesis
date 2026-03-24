"""
Regression tests for lazy Korf package imports.
"""

import importlib.abc
import sys

import pytest


_BACKEND_MODULES = {
    "optimal.solver",
    "RubikOptimal.solver",
}


class _BlockBackendImports(importlib.abc.MetaPathFinder):
    """Fail fast if the exact solver backend is imported too early."""

    def find_spec(self, fullname, path, target=None):
        if fullname in _BACKEND_MODULES:
            raise AssertionError(f"unexpected backend import: {fullname}")
        return None


def test_src_korf_import_is_lazy(monkeypatch):
    """Importing src.korf should not touch the RubikOptimal backend."""
    for module_name in (
        "src.korf",
        "src.korf.optimal_solver",
        "optimal",
        "optimal.solver",
        "RubikOptimal",
        "RubikOptimal.solver",
    ):
        monkeypatch.delitem(sys.modules, module_name, raising=False)

    finder = _BlockBackendImports()
    sys.meta_path.insert(0, finder)
    try:
        import src.korf as korf

        assert "src.korf.optimal_solver" not in sys.modules

        solver_cls = korf.KorfOptimalSolver
        assert "src.korf.optimal_solver" in sys.modules

        with pytest.raises((AssertionError, ImportError)):
            solver_cls()
    finally:
        sys.meta_path.remove(finder)
