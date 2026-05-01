"""Regression tests for the thesis workflow helper functions."""

import json
from pathlib import Path

import scripts.thesis_workflow as thesis_workflow


def test_collect_status_figures_prefers_thesis_figures(tmp_path, monkeypatch):
    """Status reporting should discover figures under thesis/figures first."""
    thesis_dir = tmp_path / "thesis"
    root_dir = tmp_path

    thesis_figures = thesis_dir / "figures"
    root_figures = root_dir / "figures"
    thesis_figures.mkdir(parents=True)
    root_figures.mkdir()

    (thesis_figures / "fig1.png").write_bytes(b"thesis-figure")
    (root_figures / "fig2.png").write_bytes(b"root-figure")

    monkeypatch.setattr(thesis_workflow, "THESIS_DIR", thesis_dir)
    monkeypatch.setattr(thesis_workflow, "ROOT", root_dir)

    figures = thesis_workflow.collect_status_figures()

    assert [path.relative_to(root_dir) for path in figures] == [
        Path("thesis/figures/fig1.png"),
        Path("figures/fig2.png"),
    ]


def test_load_benchmark_results_prefers_combined_artifact(tmp_path, monkeypatch):
    """Workflow summaries should consume the canonical combined thesis artifact when present."""
    root_dir = tmp_path
    benchmark_dir = root_dir / "results" / "benchmarks" / "thesis"
    benchmark_dir.mkdir(parents=True)

    combined_path = benchmark_dir / "thesis_results_combined.json"
    combined_path.write_text(
        json.dumps(
            {
                "metadata": {"total_scrambles": 1},
                "results": [
                    {
                        "scramble_id": 1,
                        "scramble_depth": 5,
                        "scramble_moves": ["F", "L2", "B'", "F'", "F"],
                        "timestamp": "2026-03-20T21:08:30.321949",
                        "thistlethwaite": {"solved": True},
                        "kociemba": {"solved": True},
                        "korf": {
                            "solved": True,
                            "solution_length": 3,
                            "optimal_guaranteed": True,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (benchmark_dir / "thesis_bench_d5.json").write_text(
        json.dumps({"metadata": {"total_scrambles": 99}, "results": []}),
        encoding="utf-8",
    )

    monkeypatch.setattr(thesis_workflow, "ROOT", root_dir)
    monkeypatch.setattr(thesis_workflow, "BENCHMARK_DIR", benchmark_dir)

    bench_files, records = thesis_workflow.load_benchmark_results()

    assert bench_files == [combined_path]
    assert records[0]["_source_file"] == "results/benchmarks/thesis/thesis_results_combined.json"
    assert records[0]["requested_scramble_length"] == 5
    assert records[0]["verified_scramble_depth"] == 3


def test_load_benchmark_results_falls_back_to_all_depth_shards(tmp_path, monkeypatch):
    """Workflow summaries should aggregate all depth shards when no combined artifact exists."""
    root_dir = tmp_path
    benchmark_dir = root_dir / "results" / "benchmarks" / "thesis"
    benchmark_dir.mkdir(parents=True)

    for depth in (5, 10):
        (benchmark_dir / f"thesis_bench_d{depth}.json").write_text(
            json.dumps(
                {
                    "metadata": {"total_scrambles": 1},
                    "results": [
                        {
                            "scramble_id": depth,
                            "scramble_depth": depth,
                            "scramble_moves": ["R"] * depth,
                            "timestamp": "2026-03-20T21:08:30.321949",
                            "thistlethwaite": {"solved": True},
                            "kociemba": {"solved": True},
                            "korf": {
                                "solved": True,
                                "solution_length": depth - 1,
                                "optimal_guaranteed": True,
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr(thesis_workflow, "ROOT", root_dir)
    monkeypatch.setattr(thesis_workflow, "BENCHMARK_DIR", benchmark_dir)

    bench_files, records = thesis_workflow.load_benchmark_results()

    assert [path.name for path in bench_files] == ["thesis_bench_d5.json", "thesis_bench_d10.json"]
    assert len(records) == 2
    assert [record["_source_file"] for record in records] == [
        "results/benchmarks/thesis/thesis_bench_d5.json",
        "results/benchmarks/thesis/thesis_bench_d10.json",
    ]
