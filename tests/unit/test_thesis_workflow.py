"""Regression tests for the thesis workflow helper functions."""

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
