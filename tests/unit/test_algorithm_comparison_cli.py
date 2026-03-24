"""Regression tests for the phase 9 algorithm comparison CLI."""

from argparse import Namespace
from importlib import util
from pathlib import Path
import types

import pytest


def load_cli_module():
    module_path = Path(__file__).resolve().parents[2] / "demos" / "phase9" / "algorithm_comparison_cli.py"
    spec = util.spec_from_file_location("algorithm_comparison_cli", module_path)
    module = util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class _FakeRubikCube:
    def scramble(self, moves: int, seed: int):
        return ["R", "U", "R'"]


class _FakeComparison:
    def __init__(self, *args, **kwargs):
        self.results = []
        self.exported = None

    def compare_on_scramble(self, cube, scramble_id=0):
        return types.SimpleNamespace(
            thistlethwaite=types.SimpleNamespace(
                solved=False,
                solution_length=None,
                time_seconds=0.0,
                memory_mb=0.0,
                nodes_explored=None,
                backend="thistlethwaite_native",
                optimal_guaranteed=False,
                solution_moves=None,
            ),
            kociemba=types.SimpleNamespace(
                solved=False,
                solution_length=None,
                time_seconds=0.0,
                memory_mb=0.0,
                nodes_explored=None,
                backend="kociemba_internal",
                optimal_guaranteed=False,
                solution_moves=None,
            ),
            korf=types.SimpleNamespace(
                solved=False,
                solution_length=None,
                time_seconds=0.0,
                memory_mb=0.0,
                nodes_explored=None,
                backend="optimal_external",
                optimal_guaranteed=True,
                solution_moves=None,
            ),
        )

    def export_results(self, filename):
        assert len(self.results) == 1
        self.exported = ("json", filename, len(self.results))
        Path(filename).write_text('{"results_len": 1}', encoding="utf-8")

    def export_summary_table(self, filename, format="markdown"):
        assert len(self.results) == 1
        self.exported = (format, filename, len(self.results))
        Path(filename).write_text("results_len 1", encoding="utf-8")


@pytest.mark.parametrize(
    ("suffix", "expected"),
    [
        (".json", '{"results_len": 1}'),
        (".md", "results_len 1"),
    ],
)
def test_cli_exports_the_computed_result(tmp_path, monkeypatch, suffix, expected):
    cli = load_cli_module()

    monkeypatch.setattr(cli, "RICH_AVAILABLE", False)
    monkeypatch.setattr(cli, "RubikCube", _FakeRubikCube)
    monkeypatch.setattr(cli, "AlgorithmComparison", _FakeComparison)
    monkeypatch.setattr(cli, "print_comparison_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "print_winners", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        cli.argparse.ArgumentParser,
        "parse_args",
        lambda self: Namespace(
            depth=5,
            seed=42,
            thistle_timeout=30.0,
            kociemba_timeout=60.0,
            korf_timeout=120.0,
            korf_max_depth=20,
            export=str(tmp_path / f"comparison{suffix}"),
        ),
    )

    cli.main()

    assert (tmp_path / f"comparison{suffix}").read_text(encoding="utf-8") == expected
