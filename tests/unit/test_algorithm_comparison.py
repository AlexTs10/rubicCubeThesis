"""Unit tests for the algorithm comparison framework."""

import importlib
import importlib.util
import sys

import src.evaluation.algorithm_comparison as comparison_module
from src.evaluation.algorithm_comparison import AlgorithmComparison


class TestAlgorithmComparison:
    """Test evaluation configuration for the Korf path."""

    def test_memory_delta_is_clamped_to_zero(self):
        """Transient RSS drops should not produce negative memory metrics."""
        assert AlgorithmComparison._memory_delta_mb(128.0, 120.0) == 0.0
        assert AlgorithmComparison._memory_delta_mb(128.0, 132.5) == 4.5

    def test_korf_prefers_optimal_backend_when_available(self, monkeypatch):
        """The comparison benchmark should use the real optimal backend when present."""

        class DummyThistlethwaiteSolver:
            def __init__(self, *args, **kwargs):
                pass

        class DummyKociembaSolver:
            def __init__(self, *args, **kwargs):
                pass

        class DummyOptimalSolver:
            def __init__(self, *args, **kwargs):
                self.calls = 0
                self.timeout_supported = True

            def get_statistics(self):
                return {"cubes_solved": self.calls}

        monkeypatch.setattr(comparison_module, "ThistlethwaiteSolver", DummyThistlethwaiteSolver)
        monkeypatch.setattr(comparison_module, "KociembaSolver", DummyKociembaSolver)
        monkeypatch.setattr(comparison_module, "KorfOptimalSolver", DummyOptimalSolver)
        monkeypatch.setattr(comparison_module, "OPTIMAL_AVAILABLE", True)

        comparison = AlgorithmComparison(
            thistlethwaite_timeout=1.0,
            kociemba_timeout=1.0,
            korf_timeout=1.0,
            korf_max_depth=1,
        )

        assert comparison.korf_backend == "optimal_external"
        assert comparison.korf_guarantees_optimal is True
        assert comparison.korf_timeout_enforced is True
        assert comparison.korf_pattern_db_loaded is True
        assert comparison.korf_pattern_db_status == "provided by external optimal backend"

    def test_korf_falls_back_to_internal_heuristic_path(self, monkeypatch):
        """When the optional backend is unavailable, the heuristic path stays explicit."""

        class DummyThistlethwaiteSolver:
            def __init__(self, *args, **kwargs):
                pass

        class DummyKociembaSolver:
            def __init__(self, *args, **kwargs):
                pass

        class DummyHeuristic:
            use_pattern_db = True

            def get_statistics(self):
                return {
                    "pattern_db_loaded": False,
                    "pattern_db_status": "not loaded",
                }

        class DummyIDAStarSolver:
            def __init__(self, heuristic, max_depth, timeout):
                self.heuristic = heuristic
                self.max_depth = max_depth
                self.timeout = timeout

            def get_statistics(self):
                return {"nodes_explored": 0}

        monkeypatch.setattr(comparison_module, "ThistlethwaiteSolver", DummyThistlethwaiteSolver)
        monkeypatch.setattr(comparison_module, "KociembaSolver", DummyKociembaSolver)
        monkeypatch.setattr(comparison_module, "create_heuristic", lambda *args, **kwargs: DummyHeuristic())
        monkeypatch.setattr(comparison_module, "IDAStarSolver", DummyIDAStarSolver)
        monkeypatch.setattr(comparison_module, "OPTIMAL_AVAILABLE", False)

        comparison = AlgorithmComparison(
            thistlethwaite_timeout=1.0,
            kociemba_timeout=1.0,
            korf_timeout=1.0,
            korf_max_depth=1,
        )

        assert comparison.korf_backend == "heuristic_ida_star"
        assert comparison.korf_guarantees_optimal is False
        assert comparison.korf_timeout_enforced is True
        assert comparison.korf_solver.heuristic.use_pattern_db is True
        assert comparison.korf_pattern_db_loaded is False
        assert comparison.korf_pattern_db_status == "not loaded"

    def test_optimal_solver_import_is_lazy(self):
        """Importing the optimal-solver module should not load the backend eagerly."""
        sys.modules.pop("src.korf.optimal_solver", None)
        sys.modules.pop("optimal.solver", None)
        sys.modules.pop("RubikOptimal.solver", None)

        expected_backend_available = any(
            importlib.util.find_spec(name) is not None
            for name in ("optimal", "RubikOptimal")
        )

        module = importlib.import_module("src.korf.optimal_solver")

        assert module.OPTIMAL_AVAILABLE is expected_backend_available
        assert "optimal.solver" not in sys.modules
        assert "RubikOptimal.solver" not in sys.modules
