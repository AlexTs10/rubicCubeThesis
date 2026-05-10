import json

import pytest

from src.cube.rubik_cube import RubikCube
from src.evaluation.statistics import StatisticalAnalyzer
from src.evaluation.validation import ValidationSuite
from src.evaluation.visualizations import VisualizationGenerator


def _sample_results(tmp_path):
    payload = {
        "metadata": {
            "total_tests": 2,
            "total_time_seconds": 120,
        },
        "results": [
            {
                "scramble_depth": 5,
                "thistlethwaite": {
                    "solved": True,
                    "solution_length": 12,
                    "time_seconds": 0.4,
                    "memory_mb": 2.0,
                    "nodes_explored": None,
                },
                "kociemba": {
                    "solved": True,
                    "solution_length": 8,
                    "time_seconds": 0.2,
                    "memory_mb": 1.0,
                    "nodes_explored": 40,
                },
                "korf": {
                    "solved": True,
                    "solution_length": 5,
                    "time_seconds": 0.05,
                    "memory_mb": 3.0,
                    "nodes_explored": 120,
                },
            },
            {
                "scramble_depth": 10,
                "thistlethwaite": {
                    "solved": False,
                    "solution_length": 0,
                    "time_seconds": 30.0,
                    "memory_mb": 4.0,
                    "nodes_explored": None,
                    "reason_failed": "timeout",
                },
                "kociemba": {
                    "solved": True,
                    "solution_length": 11,
                    "time_seconds": 0.5,
                    "memory_mb": 1.5,
                    "nodes_explored": 70,
                },
                "korf": {
                    "solved": False,
                    "solution_length": 0,
                    "time_seconds": 120.0,
                    "memory_mb": 10.0,
                    "nodes_explored": None,
                    "reason_failed": "timeout",
                },
            },
        ],
    }
    path = tmp_path / "sample_results.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_statistical_analyzer_summarizes_and_exports(tmp_path, capsys):
    analyzer = StatisticalAnalyzer(str(_sample_results(tmp_path)))

    summary = analyzer.generate_summary()

    thistle = summary["Thistlethwaite"]
    assert thistle.total_tests == 2
    assert thistle.successful_tests == 1
    assert thistle.success_rate == 0.5
    assert thistle.solution_length_mean == 12
    assert thistle.failure_reasons == {"timeout": 1}

    kociemba = summary["Kociemba"]
    assert kociemba.solution_length_median == 9.5
    assert kociemba.nodes_total == 110

    analyzer.print_summary(summary)
    assert "STATISTICAL ANALYSIS SUMMARY" in capsys.readouterr().out

    for table_format, suffix in [
        ("markdown", "md"),
        ("latex", "tex"),
        ("csv", "csv"),
    ]:
        output = tmp_path / f"summary.{suffix}"
        analyzer.export_table(str(output), format=table_format)
        assert output.exists()
        assert "Kociemba" in output.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="Unknown format"):
        analyzer.export_table(str(tmp_path / "bad.txt"), format="html")


def test_statistical_analyzer_handles_empty_and_unsuccessful_inputs(tmp_path):
    payload = {
        "metadata": {"total_tests": 0, "total_time_seconds": 0},
        "results": [
            {
                "scramble_depth": 5,
                "thistlethwaite": {"solved": False, "reason_failed": "timeout"},
                "kociemba": {"solved": False, "reason_failed": ""},
                "korf": {"solved": False},
            }
        ],
    }
    path = tmp_path / "failures.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    analyzer = StatisticalAnalyzer(str(path))
    summary = analyzer.generate_summary()

    assert summary["Thistlethwaite"].success_rate == 0.0
    assert summary["Thistlethwaite"].failure_reasons == {"timeout": 1}
    assert summary["Kociemba"].failure_reasons == {}
    assert StatisticalAnalyzer._mean([]) == 0.0
    assert StatisticalAnalyzer._median([]) == 0.0
    assert StatisticalAnalyzer._std([1]) == 0.0
    assert StatisticalAnalyzer._percentile([], 50) == 0.0


def _invert_moves(moves):
    inverse = []
    for move in reversed(moves):
        if move.endswith("'"):
            inverse.append(move[:-1])
        elif move.endswith("2"):
            inverse.append(move)
        else:
            inverse.append(f"{move}'")
    return inverse


def test_validation_suite_covers_solver_api_and_reports(tmp_path, capsys):
    suite = ValidationSuite()

    class TupleSolver:
        def solve(self, _cube):
            return (["U"], {"metadata": True})

    class ListSolver:
        def solve(self, _cube):
            return ["R"]

    class NoneSolver:
        def solve(self, _cube):
            return None

    class RaisingSolver:
        def solve(self, _cube):
            raise RuntimeError("solver unavailable")

    solved_cube = RubikCube()
    assert suite._solve_with_algorithm(TupleSolver(), solved_cube) == ["U"]
    assert suite._solve_with_algorithm(ListSolver(), solved_cube) == ["R"]
    assert suite._solve_with_algorithm(NoneSolver(), solved_cube) is None
    assert suite._solve_with_algorithm(object(), solved_cube) is None
    assert suite._solve_with_algorithm(RaisingSolver(), solved_cube) is None
    assert "solver unavailable" in capsys.readouterr().out

    class SuperflipSolver:
        def solve(self, _cube):
            return _invert_moves(suite.superflip_scramble)

    result = suite._test_superflip(SuperflipSolver(), "SuperflipSolver")
    assert result.solved is True
    assert result.is_optimal is True
    assert result.solution_length == 20

    failing_results = suite.run_all_validations([RaisingSolver()])
    suite.print_report(failing_results)
    report_path = tmp_path / "validation.md"
    suite.export_validation_report(failing_results, str(report_path))
    assert "Reference Validation Cases" in report_path.read_text(encoding="utf-8")


def test_visualization_generator_extracts_data_and_writes_figures(tmp_path):
    generator = VisualizationGenerator(str(_sample_results(tmp_path)))

    assert generator.algorithm_data["Thistlethwaite"]["solution_lengths"] == [12]
    assert generator.algorithm_data["Kociemba"]["nodes"] == [40, 70]
    assert generator.algorithm_data["Korf_IDA*"]["scramble_depths"] == [5]

    figure_dir = tmp_path / "figures"
    generator.generate_all_figures(str(figure_dir))

    expected = {
        "fig1_solution_length_boxplot.png",
        "fig2_time_comparison.png",
        "fig3_memory_comparison.png",
        "fig4_success_rate.png",
        "fig5_solution_distribution.png",
        "fig6_nodes_comparison.png",
        "fig7_performance_vs_depth.png",
    }
    assert expected.issubset({path.name for path in figure_dir.glob("*.png")})


def test_visualization_generator_no_data_paths(tmp_path, capsys):
    path = tmp_path / "empty.json"
    path.write_text(json.dumps({"results": []}), encoding="utf-8")
    generator = VisualizationGenerator(str(path))

    generator.plot_solution_length_boxplot(str(tmp_path / "box.png"))
    generator.plot_time_comparison_bar(str(tmp_path / "time.png"))
    generator.plot_memory_comparison_bar(str(tmp_path / "memory.png"))
    generator.plot_nodes_comparison(str(tmp_path / "nodes.png"))

    output = capsys.readouterr().out
    assert "No data available for box plot" in output
    assert "No data available for time comparison" in output
    assert "No data available for memory comparison" in output
    assert "No node data available" in output
