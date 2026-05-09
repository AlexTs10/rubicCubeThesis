"""Unit tests for benchmark artifact generation contracts."""

import json
from pathlib import Path

import pytest

import scripts.benchmarks.artifact_utils as artifact_utils
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
                "scramble_generation": "legacy_random_all_moves_redundant_allowed",
                "scramble_corpus_status": "legacy redundant scrambles preserved",
                "current_generator_for_new_runs": "random_no_consecutive_same_face_moves",
                "environment": {"python_version": "3.12.2"},
                "external_exact_backend_provenance": {
                    "package": "RubikOptimal",
                    "version": "1.1.0",
                    "solver_py_sha256": "abc123",
                },
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
    assert combined["metadata"]["scramble_generation"] == "legacy_random_all_moves_redundant_allowed"
    assert combined["metadata"]["scramble_corpus_status"] == "legacy redundant scrambles preserved"
    assert combined["metadata"]["current_generator_for_new_runs"] == "random_no_consecutive_same_face_moves"
    assert combined["metadata"]["environment"]["python_version"] == "3.12.2"
    assert combined["metadata"]["external_exact_backend_provenance"]["solver_py_sha256"] == "abc123"


def test_regenerator_loads_source_scramble_metadata(tmp_path):
    """Reruns should preserve whether the loaded source corpus is legacy redundant."""
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "metadata": {
                    "scramble_generation": "legacy_random_all_moves_redundant_allowed",
                    "scramble_corpus_status": "legacy redundant scrambles preserved",
                    "current_generator_for_new_runs": "random_no_consecutive_same_face_moves",
                },
                "results": [
                    {
                        "scramble_depth": 5,
                        "scramble_id": 0,
                        "scramble_moves": ["R", "R'"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    metadata = benchmark_regen.load_scramble_source_metadata(source)

    assert metadata["scramble_generation"] == "legacy_random_all_moves_redundant_allowed"
    assert metadata["scramble_corpus_status"] == "legacy redundant scrambles preserved"
    assert metadata["current_generator_for_new_runs"] == "random_no_consecutive_same_face_moves"


def test_write_combined_results_backfills_current_export_schema(tmp_path):
    """Combined artifacts should normalize older depth shards to the current exporter schema."""
    depth_payloads = {
        5: {
            "metadata": {
                "timestamp": "2026-03-20T21:08:41.058167",
                "total_scrambles": 1,
                "korf_backend": "optimal_external",
                "korf_guarantees_optimal": True,
            },
            "results": [
                {
                    "scramble_id": 7,
                    "scramble_depth": 5,
                    "scramble_moves": ["F", "L2", "B'", "F'", "F"],
                    "timestamp": "2026-03-20T21:08:30.321949",
                    "thistlethwaite": {
                        "algorithm": "Thistlethwaite",
                        "scramble_depth": 5,
                        "solved": True,
                        "solution_length": 10,
                        "time_seconds": 0.1,
                        "memory_mb": 1.0,
                        "nodes_explored": None,
                        "reason_failed": None,
                        "solution_moves": [],
                        "used_fallback": False,
                        "backend": "thistlethwaite_native",
                        "optimal_guaranteed": False,
                    },
                    "kociemba": {
                        "algorithm": "Kociemba",
                        "scramble_depth": 5,
                        "solved": True,
                        "solution_length": 8,
                        "time_seconds": 0.01,
                        "memory_mb": 1.0,
                        "nodes_explored": None,
                        "reason_failed": None,
                        "solution_moves": [],
                        "used_fallback": None,
                        "backend": "kociemba_internal",
                        "optimal_guaranteed": False,
                    },
                    "korf": {
                        "algorithm": "Korf_IDA*",
                        "scramble_depth": 5,
                        "solved": True,
                        "solution_length": 3,
                        "time_seconds": 0.001,
                        "memory_mb": 1.0,
                        "nodes_explored": 33,
                        "reason_failed": None,
                        "solution_moves": ["B", "L2", "F'"],
                        "used_fallback": None,
                        "backend": "optimal_external",
                        "optimal_guaranteed": True,
                    },
                }
            ],
        }
    }

    combined_path = benchmark_regen.write_combined_results(tmp_path, depth_payloads)
    combined = json.loads(combined_path.read_text())
    row = combined["results"][0]

    assert combined["metadata"]["verified_scramble_depth_available"] is True
    assert combined["metadata"]["depth_5"]["verified_scramble_depth_available"] is True
    assert row["case_id"] == "d5_007"
    assert row["requested_scramble_length"] == 5
    assert row["verified_scramble_depth"] == 3
    assert row["scramble_depth_is_verified"] is True
    assert row["korf"]["requested_scramble_length"] == 5
    assert row["korf"]["verified_scramble_depth"] == 3
    assert row["korf"]["scramble_depth_is_verified"] is True
    assert row["thistlethwaite"]["verified_scramble_depth"] is None
    assert row["kociemba"]["scramble_depth_is_verified"] is False


def test_combined_results_assign_globally_unique_case_ids(tmp_path):
    """Repeated scramble_id values across depths should still have unique case_id values."""
    depth_payloads = {}
    for depth in (5, 10):
        depth_payloads[depth] = {
            "metadata": {"timestamp": "2026-03-20T21:08:41.058167"},
            "results": [
                {
                    "scramble_id": 0,
                    "scramble_depth": depth,
                    "scramble_moves": ["R"] * depth,
                }
            ],
        }

    combined_path = benchmark_regen.write_combined_results(tmp_path, depth_payloads)
    combined = json.loads(combined_path.read_text())

    case_ids = [row["case_id"] for row in combined["results"]]
    assert case_ids == ["d5_000", "d10_000"]
    assert len(case_ids) == len(set(case_ids))


def test_committed_thesis_benchmark_artifacts_match_current_schema():
    """Checked-in thesis benchmark artifacts should already match the normalizer output."""
    thesis_benchmark_dir = Path(__file__).resolve().parents[2] / "results" / "benchmarks" / "thesis"

    for artifact_path in sorted(thesis_benchmark_dir.glob("thesis_bench_d*.json")) + [
        thesis_benchmark_dir / "thesis_results_combined.json"
    ]:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert payload == artifact_utils.normalize_benchmark_payload(payload)


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


def test_native_exact_validation_requires_oracle_for_oracle_cases(tmp_path, monkeypatch):
    """Oracle-tagged cases must not fall back to generated scramble length."""

    class DummyHeuristic:
        def __init__(self, *args, **kwargs):
            pass

        def get_statistics(self):
            return {"corner_pattern_db_loaded": False, "corner_pattern_db_complete": False}

    monkeypatch.setattr(native_validation, "NativeCoordinateHeuristic", DummyHeuristic)

    case = native_validation.ValidationCase(
        scramble=["R", "U", "F"],
        expected_depth=3,
        use_oracle=True,
        category="oracle_sample",
    )

    with pytest.raises(ValueError, match="oracle-dependent validation cases require"):
        native_validation.validate_corpus(
            [case],
            corpus_generation={"oracle_cases": 1, "total_cases": 1},
            use_oracle=False,
            max_depth=5,
            timeout=5.0,
            heuristic_cache_dir=str(tmp_path / "heuristics"),
            corner_db_path=None,
            disable_corner_db=True,
        )


def test_canonical_validation_reports_record_corpus_generation():
    """The canonical validation report pair should include the full corpus recipe."""
    validation_dir = Path(__file__).resolve().parents[2] / "results" / "validation" / "native_exact"
    manifest = json.loads((validation_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    preset = native_validation.CANONICAL_PRESET
    exhaustive_cases = len(native_validation.generate_exhaustive_corpus(preset["exhaustive_depth"]))
    oracle_cases = len(
        native_validation.generate_random_corpus(
            depths=preset["oracle_depths"],
            samples_per_depth=preset["oracle_samples_per_depth"],
            seed=preset["seed"],
        )
    )
    expected_corpus_generation = native_validation.build_corpus_generation(
        exhaustive_depth=preset["exhaustive_depth"],
        oracle_depths=preset["oracle_depths"],
        oracle_samples_per_depth=preset["oracle_samples_per_depth"],
        seed=preset["seed"],
        preset=native_validation.CANONICAL_PRESET_NAME,
    )
    expected_corpus_generation.update(
        {
            "exhaustive_cases": exhaustive_cases,
            "oracle_cases": oracle_cases,
            "total_cases": exhaustive_cases + oracle_cases,
        }
    )

    for report_info in manifest["canonical_reports"].values():
        report = json.loads((validation_dir / report_info["file"]).read_text(encoding="utf-8"))
        assert report["config"]["corpus_generation"] == expected_corpus_generation
