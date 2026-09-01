"""Regression tests for the thesis workflow helper functions."""

import json
from pathlib import Path

import pytest

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


def test_local_build_requires_bibliography_tool_before_latexmk(monkeypatch):
    """Local latexmk mode should fail early when the bibliography backend is absent."""
    commands = []

    monkeypatch.setattr(
        thesis_workflow,
        "toolchain_status",
        lambda: {
            "bibliography_backend": "bibtex",
            "latexmk": True,
            "xelatex": True,
            "bibliography_tool": False,
            "tectonic": False,
            "local_tex_ready": False,
            "docker_cli": False,
            "docker_daemon": False,
        },
    )
    monkeypatch.setattr(thesis_workflow, "run_build_command", lambda *args, **kwargs: commands.append(args))

    with pytest.raises(SystemExit) as excinfo:
        thesis_workflow.build_thesis(mode="local", image=thesis_workflow.DOCKER_IMAGE, clean=False)

    assert "bibtex" in str(excinfo.value)
    assert commands == []


def test_validate_exits_nonzero_when_no_build_path(monkeypatch):
    """Validation should fail its process when it reports blocking build-path issues."""
    data = {
        "toolchain": {
            "bibliography_backend": "bibtex",
            "local_tex_ready": False,
            "docker_daemon": False,
            "latexmk": False,
            "xelatex": False,
            "bibliography_tool": False,
            "tectonic": False,
            "docker_cli": False,
        },
        "bibliography": {"missing_keys": []},
        "benchmarks": {"files": ["results/benchmarks/thesis/thesis_results_combined.json"]},
        "remaining_targets": [],
        "approval_metadata": {"ready": True, "missing_fields": [], "path": Path("thesis/chapters/00_approval.tex")},
    }

    monkeypatch.setattr(thesis_workflow, "build_status_data", lambda: data)
    monkeypatch.setattr(thesis_workflow, "write_or_print", lambda *_args, **_kwargs: None)

    with pytest.raises(SystemExit) as excinfo:
        thesis_workflow.validate(output=None)

    assert "No thesis build path is ready" in str(excinfo.value)


def test_approval_metadata_status_detects_placeholders(tmp_path, monkeypatch):
    """The workflow should make final-submission approval placeholders explicit."""
    chapters_dir = tmp_path / "thesis" / "chapters"
    chapters_dir.mkdir(parents=True)
    approval = chapters_dir / "00_approval.tex"
    approval.write_text(
        "\n".join(
            [
                r"Κυριάκος Σγάρμπας, Αναπληρωτής Καθηγητής & \dotfill \\[0.8cm]",
                r"Ονοματεπώνυμο μέλους επιτροπής, ιδιότητα & \dotfill \\[0.8cm]",
                r"Ονοματεπώνυμο μέλους επιτροπής, ιδιότητα & \dotfill \\[0.8cm]",
                r"\noindent\textbf{Ημερομηνία εξέτασης:} \dotfill",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(thesis_workflow, "CHAPTERS_DIR", chapters_dir)

    status = thesis_workflow.approval_metadata_status()

    assert status["ready"] is False
    assert status["missing_fields"] == [
        "committee member 2 full name and title/status",
        "committee member 3 full name and title/status",
        "official examination date",
    ]


def test_approval_metadata_status_detects_unbolded_date_placeholder(tmp_path, monkeypatch):
    """Date placeholder detection should not depend on the current textbf wrapper."""
    chapters_dir = tmp_path / "thesis" / "chapters"
    chapters_dir.mkdir(parents=True)
    approval = chapters_dir / "00_approval.tex"
    approval.write_text(
        "\n".join(
            [
                r"Κυριάκος Σγάρμπας, Αναπληρωτής Καθηγητής & \dotfill \\[0.8cm]",
                r"Μέλος Επιτροπής, Καθηγητής & \dotfill \\[0.8cm]",
                r"Άλλο Μέλος Επιτροπής, Καθηγήτρια & \dotfill \\[0.8cm]",
                r"\noindent Ημερομηνία εξέτασης: \dotfill",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(thesis_workflow, "CHAPTERS_DIR", chapters_dir)

    status = thesis_workflow.approval_metadata_status()

    assert status["ready"] is False
    assert status["missing_fields"] == ["official examination date"]


def test_final_submission_validation_can_block_on_approval_placeholders(monkeypatch):
    """Normal validation warns, but final-submission mode should fail on approval placeholders."""
    data = {
        "toolchain": {
            "bibliography_backend": "bibtex",
            "local_tex_ready": True,
            "docker_daemon": False,
            "latexmk": False,
            "xelatex": False,
            "bibliography_tool": False,
            "tectonic": True,
            "docker_cli": True,
        },
        "bibliography": {"missing_keys": []},
        "benchmarks": {"files": ["results/benchmarks/thesis/thesis_results_combined.json"]},
        "remaining_targets": [],
        "approval_metadata": {
            "ready": False,
            "missing_fields": ["official examination date"],
            "path": Path("thesis/chapters/00_approval.tex"),
        },
    }

    monkeypatch.setattr(thesis_workflow, "build_status_data", lambda: data)
    monkeypatch.setattr(thesis_workflow, "write_or_print", lambda *_args, **_kwargs: None)

    thesis_workflow.validate(output=None)

    with pytest.raises(SystemExit) as excinfo:
        thesis_workflow.validate(output=None, final_submission=True)

    assert "Approval page still has final-submission placeholders" in str(excinfo.value)


def test_status_markdown_reports_final_submission_readiness():
    """Status output should surface approval metadata readiness, not only validation."""
    data = {
        "chapters": [
            {
                "name": "01_introduction.tex",
                "words": 100,
                "citations": 1,
                "state": "complete",
            }
        ],
        "bibliography": {
            "total_entries": 1,
            "cited_count": 1,
            "missing_keys": [],
            "unused_count": 0,
        },
        "benchmarks": {"files": [], "total_scrambles": 0, "algorithms": {}},
        "figures": [],
        "toolchain": {
            "bibliography_backend": "bibtex",
            "latexmk": False,
            "xelatex": False,
            "bibliography_tool": False,
            "tectonic": True,
            "docker_cli": True,
            "docker_daemon": False,
            "local_tex_ready": True,
        },
        "code_stats": {
            "src_files": 1,
            "src_lines": 10,
            "test_files": 1,
            "test_lines": 10,
            "ui_files": 0,
            "ui_lines": 0,
            "web_files": 0,
            "web_lines": 0,
            "modules": [],
        },
        "remaining_targets": [],
        "approval_metadata": {
            "ready": False,
            "missing_fields": ["official examination date"],
            "path": Path("thesis/chapters/00_approval.tex"),
        },
    }

    markdown = thesis_workflow.format_status_markdown(data)

    assert "## Final Submission Readiness" in markdown
    assert "- Approval page metadata: incomplete" in markdown
    assert "- Missing: official examination date" in markdown
    assert "validate --final-submission" in markdown
