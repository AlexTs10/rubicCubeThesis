"""Unit tests for benchmark artifact generation contracts."""

import json

import scripts.benchmarks.regenerate_thesis_benchmarks as benchmark_regen
import scripts.verification.native_exact_validation as native_validation


def test_write_combined_results_preserves_korf_provenance(tmp_path):
    """The combined benchmark artifact should retain the Korf provenance block."""
    depth_payloads = {
        5: {
            "metadata": {
                "korf_backend": "optimal_external",
                "korf_backend_preference": "auto",
                "korf_guarantees_optimal": True,
                "korf_timeout_enforced": True,
                "korf_pattern_db_loaded": True,
                "korf_pattern_db_status": "provided by external optimal backend",
                "scramble_depth_semantics": (
                    "scramble_depth records the requested scramble length; verified_scramble_depth "
                    "is populated only when the exact distance is known from the optimal Korf backend."
                ),
            },
            "results": [{"scramble_depth": 5}],
        }
    }

    combined_path = benchmark_regen.write_combined_results(tmp_path, depth_payloads)
    combined = json.loads(combined_path.read_text())

    assert combined["metadata"]["korf_backend"] == "optimal_external"
    assert combined["metadata"]["korf_backend_preference"] == "auto"
    assert combined["metadata"]["korf_guarantees_optimal"] is True
    assert combined["metadata"]["korf_timeout_enforced"] is True
    assert combined["metadata"]["korf_pattern_db_loaded"] is True
    assert combined["metadata"]["korf_pattern_db_status"] == "provided by external optimal backend"
    assert "scramble_depth_semantics" in combined["metadata"]


def test_native_exact_validation_records_corpus_generation(tmp_path, monkeypatch):
    """Validation reports should embed the corpus-generation inputs."""

    class DummyHeuristic:
        def __init__(self, *args, **kwargs):
            pass

    class DummyNativeExactSolver:
        def __init__(self, *args, **kwargs):
            pass

        def solve(self, cube):
            return (["R'"], {"optimal": True, "completed": True, "moves": 1})

        def get_statistics(self):
            return {"optimal": True, "completed": True, "moves": 1}

    class DummyOracleSolver:
        def solve(self, cube, verbose=False, timeout=None):
            return (["R'"], {"optimal": True, "completed": True, "moves": 1})

    monkeypatch.setattr(native_validation, "NativeCoordinateHeuristic", DummyHeuristic)
    monkeypatch.setattr(native_validation, "NativeExactSolver", DummyNativeExactSolver)
    monkeypatch.setattr(native_validation, "KorfOptimalSolver", DummyOracleSolver)

    case = native_validation.ValidationCase(
        scramble=["R"],
        expected_depth=1,
        use_oracle=True,
        category="oracle_sample",
    )
    corpus_generation = {
        "exhaustive_depth": 3,
        "oracle_depths": [4, 5],
        "oracle_samples_per_depth": 3,
        "seed": 42,
        "exhaustive_cases": 1,
        "oracle_cases": 1,
        "total_cases": 2,
    }

    report = native_validation.validate_corpus(
        [case],
        corpus_generation=corpus_generation,
        use_oracle=True,
        max_depth=5,
        timeout=5.0,
        heuristic_cache_dir=str(tmp_path / "heuristics"),
        corner_db_path=None,
        disable_corner_db=True,
    )

    assert report["config"]["corpus_generation"] == corpus_generation
    assert report["summary"]["total_cases"] == 1
    assert report["summary"]["successful_cases"] == 1
    assert report["summary"]["failure_count"] == 0
