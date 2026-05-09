#!/usr/bin/env python3
"""Repo-local workflow for finishing the Rubik's Cube thesis with agents."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import platform
import re
import shutil
import socket
import statistics
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.benchmarks.artifact_utils import (
    load_normalized_benchmark_payload,
    resolve_benchmark_sources,
)

THESIS_DIR = ROOT / "thesis"
CHAPTERS_DIR = THESIS_DIR / "chapters"
SPECS_DIR = THESIS_DIR / "specs"
WORKFLOW_DIR = ROOT / "agent_workflow"
GENERATED_DIR = WORKFLOW_DIR / "generated"
MAPPING_FILE = ROOT / "docs" / "CODE_TO_THESIS_MAPPING.md"
BENCHMARK_DIR = ROOT / "results" / "benchmarks" / "thesis"

ALGORITHMS = ("thistlethwaite", "kociemba", "korf")
DOCKER_IMAGE = "blang/latex:ctanfull"


@dataclass(frozen=True)
class ChapterConfig:
    """Workflow metadata for a thesis chapter or appendix."""

    key: str
    title: str
    chapter_file: Path
    spec_file: Path | None
    supporting_files: tuple[Path, ...]
    figure_paths: tuple[Path, ...] = ()
    paper_dirs: tuple[Path, ...] = ()
    uses_benchmarks: bool = False
    checklist: tuple[str, ...] = ()


WORKFLOW_CONFIG: dict[str, ChapterConfig] = {
    "07_evaluation": ChapterConfig(
        key="07_evaluation",
        title="Chapter 07: Evaluation",
        chapter_file=CHAPTERS_DIR / "07_evaluation.tex",
        spec_file=SPECS_DIR / "ch07_evaluation_spec.md",
        supporting_files=(
            ROOT / "src" / "evaluation" / "algorithm_comparison.py",
            ROOT / "scripts" / "benchmarks" / "generate_thesis_data.py",
            ROOT / "scripts" / "benchmarks" / "generate_complete_thesis_data.py",
            ROOT / "scripts" / "benchmarks" / "regenerate_thesis_benchmarks.py",
            ROOT / "scripts" / "benchmarks" / "analyze_thesis_data.py",
            ROOT / "scripts" / "benchmarks" / "generate_latex_tables.py",
            MAPPING_FILE,
        ),
        figure_paths=tuple(sorted((THESIS_DIR / "figures").glob("fig*.png"))),
        paper_dirs=(ROOT / "papers" / "chapter6", ROOT / "papers" / "chapter7"),
        uses_benchmarks=True,
        checklist=(
            "Document methodology from the benchmark JSON metadata and evaluation framework.",
            "Report success rates, solution lengths, timing, memory, and node-expansion trends.",
            "Reference the generated figures and connect each claim to a number in the benchmark data.",
            "Call out limitations and fairness constraints in the experimental setup.",
        ),
    ),
    "08_implementation": ChapterConfig(
        key="08_implementation",
        title="Chapter 08: Implementation",
        chapter_file=CHAPTERS_DIR / "08_implementation.tex",
        spec_file=SPECS_DIR / "ch08_implementation_spec.md",
        supporting_files=(
            ROOT / "README.md",
            MAPPING_FILE,
            ROOT / "src" / "cube" / "rubik_cube.py",
            ROOT / "src" / "thistlethwaite" / "solver.py",
            ROOT / "src" / "kociemba" / "solver.py",
            ROOT / "src" / "korf" / "a_star.py",
            ROOT / "src" / "korf" / "composite_heuristic.py",
            ROOT / "ui" / "app.py",
            ROOT / "webapp" / "src" / "app" / "page.tsx",
        ),
        figure_paths=tuple(sorted((ROOT / "figures" / "diagrams").glob("*"))),
        paper_dirs=(),
        uses_benchmarks=False,
        checklist=(
            "Describe the module boundaries: cube core, solvers, heuristics, evaluation, and UIs.",
            "Explain implementation decisions that support fair comparison and maintainability.",
            "Include testing and verification infrastructure, not only runtime code.",
            "Use the diagrams and code statistics instead of generic architecture prose.",
        ),
    ),
    "09_conclusions": ChapterConfig(
        key="09_conclusions",
        title="Chapter 09: Conclusions",
        chapter_file=CHAPTERS_DIR / "09_conclusions.tex",
        spec_file=SPECS_DIR / "ch09_conclusions_spec.md",
        supporting_files=(
            ROOT / "README.md",
            MAPPING_FILE,
            CHAPTERS_DIR / "07_evaluation.tex",
            ROOT / "src" / "evaluation" / "algorithm_comparison.py",
            BENCHMARK_DIR / "thesis_results_combined.json",
            ROOT / "src" / "korf" / "composite_heuristic.py",
        ),
        figure_paths=(),
        paper_dirs=(ROOT / "papers" / "chapter4", ROOT / "papers" / "chapter5"),
        uses_benchmarks=True,
        checklist=(
            "Summarize thesis objectives and whether they were met.",
            "State the practical trade-off between Thistlethwaite, Kociemba, and Korf clearly.",
            "Frame the composite heuristic as the main research contribution without overstating it.",
            "Separate limitations from future work.",
        ),
    ),
    "appendix_a": ChapterConfig(
        key="appendix_a",
        title="Appendix A: Installation and Usage",
        chapter_file=CHAPTERS_DIR / "appendix_a.tex",
        spec_file=None,
        supporting_files=(
            ROOT / "README.md",
            THESIS_DIR / "README.md",
            ROOT / "requirements.txt",
            ROOT / "verify_setup.py",
            ROOT / "docs" / "demos_and_ui.md",
        ),
        checklist=(
            "Expand system requirements and environment setup.",
            "Document benchmark, demo, Streamlit, and Next.js commands.",
            "Make the appendix reproducible for a grader on a fresh machine.",
        ),
    ),
    "appendix_b": ChapterConfig(
        key="appendix_b",
        title="Appendix B: Selected Code",
        chapter_file=CHAPTERS_DIR / "appendix_b.tex",
        spec_file=None,
        supporting_files=(
            MAPPING_FILE,
            ROOT / "src" / "cube" / "rubik_cube.py",
            ROOT / "src" / "korf" / "a_star.py",
            ROOT / "src" / "korf" / "composite_heuristic.py",
        ),
        checklist=(
            "Select short, representative code snippets rather than dumping full files.",
            "Cover core representation, one search routine, and the composite heuristic.",
            "Explain why each snippet matters to the thesis argument.",
        ),
    ),
}


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate status reports and chapter packets for thesis maintenance and verification."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Generate a repo status report.")
    status_parser.add_argument("--output", type=Path, help="Write the markdown report to a file.")

    packet_parser = subparsers.add_parser("packet", help="Generate a chapter packet.")
    packet_parser.add_argument("chapter", choices=sorted(WORKFLOW_CONFIG), help="Workflow chapter key.")
    packet_parser.add_argument("--output", type=Path, help="Write the packet to a file.")

    packets_parser = subparsers.add_parser("packets", help="Generate packets for multiple chapters.")
    packets_parser.add_argument(
        "--remaining",
        action="store_true",
        help="Generate packets only for chapters that still look like stubs.",
    )

    validate_parser = subparsers.add_parser("validate", help="Run a lightweight workflow validation.")
    validate_parser.add_argument("--output", type=Path, help="Write the markdown report to a file.")

    build_parser = subparsers.add_parser("build", help="Build the thesis PDF.")
    build_parser.add_argument(
        "--mode",
        choices=("auto", "local", "docker"),
        default="auto",
        help="Build locally with XeLaTeX-compatible tooling or Tectonic, inside Docker, or pick automatically.",
    )
    build_parser.add_argument(
        "--image",
        default=DOCKER_IMAGE,
        help="Docker image to use when building in Docker mode.",
    )
    build_parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete common LaTeX auxiliary files before building.",
    )

    return parser.parse_args()


def read_text(path: Path) -> str:
    """Read a UTF-8 text file defensively."""
    return path.read_text(encoding="utf-8", errors="ignore")


def relative(path: Path) -> str:
    """Render a path relative to the repo root when possible."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def ensure_output_dir() -> None:
    """Create the generated output directory on demand."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def strip_latex(text: str) -> str:
    """Approximate plain text extraction for word counting."""
    text = re.sub(r"(?<!\\)%.*", " ", text)
    text = re.sub(r"\\[A-Za-z@]+(?:\*?)", " ", text)
    text = re.sub(r"[{}_^&$#~]", " ", text)
    text = text.replace("\\", " ")
    return re.sub(r"\s+", " ", text).strip()


def word_count(path: Path) -> int:
    """Compute an approximate word count for a LaTeX file."""
    words = strip_latex(read_text(path)).split()
    return len(words)


def bibliography_backend() -> str:
    """Read the configured biblatex backend from thesis/main.tex."""
    text = read_text(THESIS_DIR / "main.tex")
    match = re.search(r"\\usepackage\[[^\]]*backend\s*=\s*([^,\]]+)", text)
    if not match:
        return "bibtex"
    return match.group(1).strip().lower()


def extract_cite_keys(text: str) -> list[str]:
    """Extract citation keys from LaTeX-ish text."""
    keys: set[str] = set()
    pattern = re.compile(r"\\cite(?:\[[^\]]*\])?(?:\[[^\]]*\])?\{([^}]+)\}")
    for match in pattern.finditer(text):
        keys.update(part.strip() for part in match.group(1).split(",") if part.strip())
    return sorted(keys)


def bibliography_summary() -> dict[str, Any]:
    """Summarize the bibliography coverage."""
    bib_path = THESIS_DIR / "references.bib"
    bib_text = read_text(bib_path)
    bib_keys = sorted(set(re.findall(r"@\w+\{\s*([^,]+),", bib_text)))

    cited_keys: set[str] = set()
    per_chapter: dict[str, int] = {}
    for chapter_file in sorted(CHAPTERS_DIR.glob("*.tex")):
        keys = extract_cite_keys(read_text(chapter_file))
        per_chapter[chapter_file.name] = len(keys)
        cited_keys.update(keys)

    cited_sorted = sorted(cited_keys)
    missing = sorted(set(cited_sorted) - set(bib_keys))
    unused = sorted(set(bib_keys) - set(cited_sorted))

    return {
        "bib_path": bib_path,
        "total_entries": len(bib_keys),
        "cited_keys": cited_sorted,
        "cited_count": len(cited_sorted),
        "missing_keys": missing,
        "unused_count": len(unused),
        "unused_sample": unused[:15],
        "per_chapter": per_chapter,
    }


def classify_chapter_state(chapter_file: Path) -> tuple[bool, str]:
    """Classify a thesis chapter as front matter, stub, or complete."""
    front_matter = {
        "00_titlepage.tex",
        "00_approval.tex",
        "00_acknowledgements.tex",
        "00_abstract_gr.tex",
        "00_abstract_en.tex",
    }
    if chapter_file.name in front_matter:
        return False, "front-matter"

    words = word_count(chapter_file)
    is_stub = words < 80
    return is_stub, ("stub" if is_stub else "complete")


def chapter_status() -> list[dict[str, Any]]:
    """Collect a compact status view of all thesis chapter files."""
    status_rows = []
    for chapter_file in sorted(CHAPTERS_DIR.glob("*.tex")):
        text = read_text(chapter_file)
        words = word_count(chapter_file)
        cites = extract_cite_keys(text)
        is_stub, state = classify_chapter_state(chapter_file)
        status_rows.append(
            {
                "name": chapter_file.name,
                "path": chapter_file,
                "words": words,
                "citations": len(cites),
                "is_stub": is_stub,
                "state": state,
            }
        )
    return status_rows


def collect_numeric_values(
    rows: list[dict[str, Any]],
    key: str,
    *,
    nonnegative_only: bool = False,
) -> list[float]:
    """Collect numeric values from benchmark rows with optional filtering."""
    values: list[float] = []
    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if nonnegative_only and numeric < 0:
            continue
        values.append(numeric)
    return values


def codebase_stats() -> dict[str, Any]:
    """Collect repo statistics useful for the implementation chapter."""
    def count_lines(paths: list[Path]) -> int:
        total = 0
        for path in paths:
            try:
                total += sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
        return total

    src_py = sorted((ROOT / "src").rglob("*.py"))
    tests_py = sorted((ROOT / "tests").rglob("*.py"))
    ui_py = sorted((ROOT / "ui").rglob("*.py"))
    web_ts = sorted((ROOT / "webapp" / "src").rglob("*.ts")) + sorted((ROOT / "webapp" / "src").rglob("*.tsx"))

    module_dirs = [
        ROOT / "src" / "cube",
        ROOT / "src" / "thistlethwaite",
        ROOT / "src" / "kociemba",
        ROOT / "src" / "korf",
        ROOT / "src" / "evaluation",
        ROOT / "src" / "utils",
    ]
    modules = []
    for module_dir in module_dirs:
        files = sorted(module_dir.rglob("*.py"))
        modules.append(
            {
                "name": module_dir.name,
                "files": len(files),
                "lines": count_lines(files),
                "path": module_dir,
            }
        )

    return {
        "src_files": len(src_py),
        "src_lines": count_lines(src_py),
        "test_files": len(tests_py),
        "test_lines": count_lines(tests_py),
        "ui_files": len(ui_py),
        "ui_lines": count_lines(ui_py),
        "web_files": len(web_ts),
        "web_lines": count_lines(web_ts),
        "modules": modules,
    }


def load_benchmark_results() -> tuple[list[Path], list[dict[str, Any]]]:
    """Load all benchmark JSON files produced for the thesis evaluation."""
    bench_files = resolve_benchmark_sources(BENCHMARK_DIR)
    records: list[dict[str, Any]] = []
    for bench_file in bench_files:
        payload = load_normalized_benchmark_payload(bench_file)
        for result in payload.get("results", []):
            result["_source_file"] = relative(bench_file)
            records.append(result)
    return bench_files, records


def mean_or_none(values: list[float], clamp_min: float | None = None) -> float | None:
    """Return a rounded mean or None for empty sequences."""
    if not values:
        return None
    value = statistics.fmean(values)
    if clamp_min is not None:
        value = max(clamp_min, value)
    return round(value, 2)


def summarize_benchmarks() -> dict[str, Any]:
    """Aggregate the benchmark files into thesis-ready summary statistics."""
    bench_files, records = load_benchmark_results()
    if not bench_files:
        return {"files": [], "total_scrambles": 0, "algorithms": {}}

    summary: dict[str, Any] = {
        "files": [relative(path) for path in bench_files],
        "total_scrambles": len(records),
        "algorithms": {},
    }

    for algorithm in ALGORITHMS:
        by_depth: dict[int, list[dict[str, Any]]] = {}
        algo_records: list[dict[str, Any]] = []
        for record in records:
            algo_result = record.get(algorithm, {})
            depth = int(record.get("scramble_depth", 0))
            by_depth.setdefault(depth, []).append(algo_result)
            algo_records.append(algo_result)

        solved_records = [row for row in algo_records if row.get("solved")]
        summary["algorithms"][algorithm] = {
            "overall": {
                "total": len(algo_records),
                "solved": len(solved_records),
                "success_rate": round((len(solved_records) / len(algo_records)) * 100, 1) if algo_records else 0.0,
                "avg_solution_length": mean_or_none(collect_numeric_values(solved_records, "solution_length")),
                "avg_time_seconds": mean_or_none(collect_numeric_values(solved_records, "time_seconds")),
                "avg_memory_mb": mean_or_none(
                    collect_numeric_values(solved_records, "memory_mb", nonnegative_only=True),
                    clamp_min=0.0,
                ),
                "avg_nodes_explored": mean_or_none(collect_numeric_values(solved_records, "nodes_explored")),
            },
            "by_depth": {},
        }

        for depth in sorted(by_depth):
            rows = by_depth[depth]
            solved = [row for row in rows if row.get("solved")]
            summary["algorithms"][algorithm]["by_depth"][depth] = {
                "total": len(rows),
                "solved": len(solved),
                "success_rate": round((len(solved) / len(rows)) * 100, 1) if rows else 0.0,
                "avg_solution_length": mean_or_none(collect_numeric_values(solved, "solution_length")),
                "avg_time_seconds": mean_or_none(collect_numeric_values(solved, "time_seconds")),
                "avg_memory_mb": mean_or_none(
                    collect_numeric_values(solved, "memory_mb", nonnegative_only=True),
                    clamp_min=0.0,
                ),
                "avg_nodes_explored": mean_or_none(collect_numeric_values(solved, "nodes_explored")),
            }

    return summary


def toolchain_status() -> dict[str, Any]:
    """Detect local tooling required for a full thesis build."""
    backend = bibliography_backend()
    latexmk_available = shutil.which("latexmk") is not None
    xelatex_available = shutil.which("xelatex") is not None
    tectonic_available = shutil.which("tectonic") is not None
    bibliography_tool_available = shutil.which(backend) is not None
    xelatex_ready = xelatex_available and bibliography_tool_available
    local_tex_ready = (
        (latexmk_available and xelatex_ready)
        or xelatex_ready
        or (tectonic_available and (backend != "biber" or bibliography_tool_available))
    )
    docker_cli = shutil.which("docker") is not None
    docker_daemon = False
    if docker_cli:
        docker_daemon = (
            subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    return {
        "bibliography_backend": backend,
        "latexmk": latexmk_available,
        "xelatex": xelatex_available,
        "bibliography_tool": bibliography_tool_available,
        "tectonic": tectonic_available,
        "local_tex_ready": local_tex_ready,
        "docker_cli": docker_cli,
        "docker_daemon": docker_daemon,
    }


def build_status_data() -> dict[str, Any]:
    """Build the full status report payload."""
    chapters = chapter_status()
    bibliography = bibliography_summary()
    benchmarks = summarize_benchmarks()
    tools = toolchain_status()
    code_stats = codebase_stats()
    figures = collect_status_figures()

    remaining = [
        row["name"]
        for row in chapters
        if row["is_stub"] and row["name"] in {config.chapter_file.name for config in WORKFLOW_CONFIG.values()}
    ]

    return {
        "chapters": chapters,
        "bibliography": bibliography,
        "benchmarks": benchmarks,
        "toolchain": tools,
        "code_stats": code_stats,
        "figures": [relative(path) for path in figures],
        "remaining_targets": remaining,
    }


def collect_status_figures() -> list[Path]:
    """Collect thesis comparison figures from the current canonical locations."""
    figure_roots = (
        THESIS_DIR / "figures",
        ROOT / "figures",
    )
    figures: list[Path] = []
    seen: set[Path] = set()

    for root in figure_roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("fig*.png")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            figures.append(path)

    return figures


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    """Render a simple GitHub-flavored markdown table."""
    def render(item: Any) -> str:
        return "n/a" if item is None else str(item)

    header_line = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(render(item) for item in row) + " |" for row in rows]
    return "\n".join([header_line, divider, *body])


def format_status_markdown(data: dict[str, Any]) -> str:
    """Format the repo status report as markdown."""
    backend = data["toolchain"]["bibliography_backend"]
    chapter_rows = [
        [
            row["name"],
            row["words"],
            row["citations"],
            row["state"],
        ]
        for row in data["chapters"]
    ]

    bibliography = data["bibliography"]
    benchmark_rows = []
    for algorithm in ALGORITHMS:
        overall = data["benchmarks"]["algorithms"].get(algorithm, {}).get("overall", {})
        if overall:
            benchmark_rows.append(
                [
                    algorithm,
                    f"{overall['solved']}/{overall['total']}",
                    overall["success_rate"],
                    overall["avg_solution_length"],
                    overall["avg_time_seconds"],
                    overall["avg_memory_mb"],
                ]
            )

    tool_lines = [
        f"- `latexmk`: {'available' if data['toolchain']['latexmk'] else 'missing'}",
        f"- `xelatex`: {'available' if data['toolchain']['xelatex'] else 'missing'}",
        f"- `{backend}`: {'available' if data['toolchain']['bibliography_tool'] else 'missing'}",
        f"- `tectonic`: {'available' if data['toolchain']['tectonic'] else 'missing'}",
        f"- `docker` CLI: {'available' if data['toolchain']['docker_cli'] else 'missing'}",
        f"- Docker daemon: {'available' if data['toolchain']['docker_daemon'] else 'missing'}",
    ]

    code_stats = data["code_stats"]
    module_rows = [
        [module["name"], module["files"], module["lines"], relative(module["path"])]
        for module in code_stats["modules"]
    ]

    remaining_lines = [f"- `{name}`" for name in data["remaining_targets"]] or ["- None"]

    sections = [
        "# Thesis Workflow Status",
        "",
        "> Generated artifact, not source of truth. Re-run this command in the current environment before relying on the result.",
        "",
        "## Thesis Chapters",
        markdown_table(["File", "Words", "Citations", "State"], chapter_rows),
        "",
        "## Open Workflow Targets",
        *remaining_lines,
        "",
        "## Bibliography",
        f"- Entries in `thesis/references.bib`: {bibliography['total_entries']}",
        f"- Citation keys already used in chapters: {bibliography['cited_count']}",
        f"- Missing citation keys: {len(bibliography['missing_keys'])}",
        f"- Unused bibliography entries: {bibliography['unused_count']}",
    ]

    if bibliography["missing_keys"]:
        sections.extend(["- Missing keys detail: " + ", ".join(bibliography["missing_keys"])])

    figure_lines = [f"- `{path}`" for path in data["figures"]] or ["- No thesis comparison figures found."]

    sections.extend(
        [
            "",
            "## Benchmarks",
            f"- Benchmark files: {', '.join(data['benchmarks']['files']) if data['benchmarks']['files'] else 'none'}",
            f"- Total scrambles available: {data['benchmarks']['total_scrambles']}",
            markdown_table(
                ["Algorithm", "Solved", "Success %", "Avg Moves", "Avg Time (s)", "Avg Memory (MB)"],
                benchmark_rows,
            )
            if benchmark_rows
            else "- No benchmark data found.",
            "",
            "## Figures",
            *figure_lines,
            "",
            "## Toolchain",
            *tool_lines,
            "",
            "## Codebase Stats",
            f"- Python source files in `src/`: {code_stats['src_files']} ({code_stats['src_lines']} lines)",
            f"- Python test files in `tests/`: {code_stats['test_files']} ({code_stats['test_lines']} lines)",
            f"- UI files in `ui/`: {code_stats['ui_files']} ({code_stats['ui_lines']} lines)",
            f"- Web files in `webapp/src/`: {code_stats['web_files']} ({code_stats['web_lines']} lines)",
            markdown_table(["Module", "Files", "Lines", "Path"], module_rows),
            "",
            "## Recommended Next Step",
        ]
    )

    if data["remaining_targets"]:
        sections.append(
            f"- Generate packets for: {', '.join(sorted(key for key, cfg in WORKFLOW_CONFIG.items() if cfg.chapter_file.name in data['remaining_targets']))}"
        )
    elif data["toolchain"]["local_tex_ready"]:
        sections.append("- Run `python scripts/thesis_workflow.py build --mode auto` to verify or rebuild the final PDF.")
    elif data["toolchain"]["docker_daemon"]:
        sections.append("- Run `python scripts/thesis_workflow.py build --mode docker` to verify or rebuild the final PDF in Docker.")
    else:
        sections.append("- The manuscript is complete, but no thesis build path is available in this environment.")

    return "\n".join(sections) + "\n"


def candidate_citations(config: ChapterConfig) -> list[str]:
    """Extract candidate citation keys from a chapter spec."""
    if config.spec_file is None or not config.spec_file.exists():
        return []
    return extract_cite_keys(read_text(config.spec_file))


def list_local_papers(config: ChapterConfig) -> list[str]:
    """List local paper assets tied to a chapter packet."""
    papers: list[str] = []
    for paper_dir in config.paper_dirs:
        if not paper_dir.exists():
            continue
        for path in sorted(paper_dir.iterdir()):
            if path.is_file():
                papers.append(relative(path))
    return papers


def benchmark_overview_tables(benchmarks: dict[str, Any]) -> tuple[str, str]:
    """Create markdown tables for overall and depth-wise benchmark summaries."""
    overall_rows = []
    for algorithm in ALGORITHMS:
        overall = benchmarks["algorithms"].get(algorithm, {}).get("overall", {})
        if not overall:
            continue
        overall_rows.append(
            [
                algorithm,
                f"{overall['solved']}/{overall['total']}",
                overall["success_rate"],
                overall["avg_solution_length"],
                overall["avg_time_seconds"],
                overall["avg_memory_mb"],
                overall["avg_nodes_explored"],
            ]
        )

    overall_table = markdown_table(
        ["Algorithm", "Solved", "Success %", "Avg Moves", "Avg Time (s)", "Avg Memory (MB)", "Avg Nodes"],
        overall_rows,
    )

    depth_rows = []
    for depth in sorted(
        {
            depth
            for algorithm in ALGORITHMS
            for depth in benchmarks["algorithms"].get(algorithm, {}).get("by_depth", {})
        }
    ):
        for algorithm in ALGORITHMS:
            by_depth = benchmarks["algorithms"].get(algorithm, {}).get("by_depth", {}).get(depth)
            if by_depth is None:
                continue
            depth_rows.append(
                [
                    depth,
                    algorithm,
                    f"{by_depth['solved']}/{by_depth['total']}",
                    by_depth["success_rate"],
                    by_depth["avg_solution_length"],
                    by_depth["avg_time_seconds"],
                    by_depth["avg_nodes_explored"],
                ]
            )

    depth_table = markdown_table(
        ["Depth", "Algorithm", "Solved", "Success %", "Avg Moves", "Avg Time (s)", "Avg Nodes"],
        depth_rows,
    )
    return overall_table, depth_table


def supporting_file_lines(config: ChapterConfig) -> list[str]:
    """Render supporting file paths for a chapter packet."""
    lines = [f"- `{relative(config.chapter_file)}`"]
    if config.spec_file is not None:
        lines.append(f"- `{relative(config.spec_file)}`")
    lines.extend(f"- `{relative(path)}`" for path in config.supporting_files if path.exists())
    return lines


def chapter_excerpt(chapter_path: Path, limit: int = 80) -> str:
    """Return a short excerpt of the current chapter source."""
    lines = read_text(chapter_path).splitlines()
    return "\n".join(lines[:limit]).strip()


def build_packet_markdown(config: ChapterConfig) -> str:
    """Build a chapter packet with the evidence an agent should use."""
    bibliography = bibliography_summary()
    benchmarks = summarize_benchmarks()
    code_stats = codebase_stats()
    words = word_count(config.chapter_file)
    _, state = classify_chapter_state(config.chapter_file)
    current_citations = extract_cite_keys(read_text(config.chapter_file))
    suggested_citations = candidate_citations(config)
    papers = list_local_papers(config)

    sections = [
        f"# {config.title} Packet",
        "",
        "## Target",
        f"- Chapter key: `{config.key}`",
        f"- Chapter file: `{relative(config.chapter_file)}`",
        f"- Current word count: {words}",
        f"- Current citation count: {len(current_citations)}",
        f"- Current state: {state}",
        "",
        "## Files To Read First",
        *supporting_file_lines(config),
        "",
        "## Suggested Citations From Spec",
    ]

    if suggested_citations:
        sections.extend(f"- `{key}`" for key in suggested_citations)
    else:
        sections.append("- No explicit citation keys extracted from the spec.")

    missing_suggested = sorted(set(suggested_citations) - set(bibliography["cited_keys"]) - set(bibliography["missing_keys"]))
    if missing_suggested:
        sections.extend(["", "## Suggested Citations Not Yet Used Anywhere", *(f"- `{key}`" for key in missing_suggested)])

    if papers:
        sections.extend(["", "## Local Papers And Notes", *(f"- `{path}`" for path in papers[:40])])

    if config.uses_benchmarks and benchmarks["total_scrambles"]:
        overall_table, depth_table = benchmark_overview_tables(benchmarks)
        sections.extend(
            [
                "",
                "## Benchmark Inputs",
                f"- Source files: {', '.join(benchmarks['files'])}",
                f"- Total scrambles: {benchmarks['total_scrambles']}",
                "",
                "### Overall Summary",
                overall_table,
                "",
                "### By Depth",
                depth_table,
            ]
        )

    if config.key == "08_implementation":
        module_rows = [
            [module["name"], module["files"], module["lines"], relative(module["path"])]
            for module in code_stats["modules"]
        ]
        sections.extend(
            [
                "",
                "## Codebase Snapshot",
                f"- Python source files in `src/`: {code_stats['src_files']} ({code_stats['src_lines']} lines)",
                f"- Test files in `tests/`: {code_stats['test_files']} ({code_stats['test_lines']} lines)",
                f"- Streamlit UI files in `ui/`: {code_stats['ui_files']} ({code_stats['ui_lines']} lines)",
                f"- Next.js source files in `webapp/src/`: {code_stats['web_files']} ({code_stats['web_lines']} lines)",
                markdown_table(["Module", "Files", "Lines", "Path"], module_rows),
            ]
        )

    if config.figure_paths:
        sections.extend(["", "## Figures / Diagrams", *(f"- `{relative(path)}`" for path in config.figure_paths if path.exists())])

    sections.extend(
        [
            "",
            "## Existing Chapter Source",
            "```tex",
            chapter_excerpt(config.chapter_file) or "% Empty chapter",
            "```",
            "",
            "## Writing Checklist",
            *(f"- {item}" for item in config.checklist),
            "",
            "## Agent Operating Notes",
            "- Keep edits focused on the target chapter and `thesis/references.bib` unless the packet requires another file.",
            "- Use only numbers present in the benchmark JSON files or clearly derivable from them.",
            "- Preserve Greek academic style in the LaTeX chapters.",
            "- Add figure and table references only after verifying the asset paths exist.",
        ]
    )

    return "\n".join(sections) + "\n"


def format_validation_markdown(data: dict[str, Any]) -> str:
    """Render a lightweight validation report."""
    issues = []
    backend = data["toolchain"]["bibliography_backend"]
    local_tex_ready = data["toolchain"]["local_tex_ready"]
    docker_ready = data["toolchain"]["docker_daemon"]

    if not local_tex_ready and not docker_ready:
        issues.append(
            f"No thesis build path is ready. Install `latexmk` + `xelatex` + `{backend}`, install `tectonic`, or start Docker Desktop and use Docker mode."
        )
    elif not local_tex_ready and docker_ready:
        issues.append("Local TeX tooling is missing, but Docker mode can still build the final thesis PDF.")
    if data["bibliography"]["missing_keys"]:
        issues.append(
            "Some citation keys used in chapters are missing from `thesis/references.bib`: "
            + ", ".join(data["bibliography"]["missing_keys"])
        )
    if not data["benchmarks"]["files"]:
        issues.append("No benchmark JSON files were found for the evaluation chapter.")
    if data["remaining_targets"]:
        issues.append("Stub workflow targets remain: " + ", ".join(data["remaining_targets"]))

    sections = [
        "# Thesis Workflow Validation",
        "",
        "> Generated artifact, not source of truth. Re-run this command in the current environment before relying on the result.",
        "",
        "## Metadata",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- Host: {socket.gethostname()}",
        f"- Platform: {platform.platform()}",
        f"- Python: {platform.python_version()}",
        "",
        "## Checks",
        f"- Local `latexmk`: {'pass' if data['toolchain']['latexmk'] else 'fail'}",
        f"- Local `xelatex`: {'pass' if data['toolchain']['xelatex'] else 'fail'}",
        f"- Local `{backend}`: {'pass' if data['toolchain']['bibliography_tool'] else 'fail'}",
        f"- Local `tectonic`: {'pass' if data['toolchain']['tectonic'] else 'fail'}",
        f"- Docker CLI available: {'pass' if data['toolchain']['docker_cli'] else 'fail'}",
        f"- Docker daemon ready: {'pass' if data['toolchain']['docker_daemon'] else 'fail'}",
        f"- Thesis build path ready: {'pass' if (local_tex_ready or docker_ready) else 'fail'}",
        f"- Benchmark JSON files present: {'pass' if data['benchmarks']['files'] else 'fail'}",
        f"- Missing citation keys: {'pass' if not data['bibliography']['missing_keys'] else 'fail'}",
        f"- Open workflow targets: {'pass' if not data['remaining_targets'] else 'fail'}",
        "",
        "## Issues",
    ]

    if issues:
        sections.extend(f"- {issue}" for issue in issues)
    else:
        sections.append("- No blocking issues found in the lightweight workflow checks.")

    sections.extend(
        [
            "",
            "## Next Action",
            "- If open workflow targets remain, generate packets with `python scripts/thesis_workflow.py packets --remaining`.",
            "- Build or rebuild the thesis with `python scripts/thesis_workflow.py build --mode auto`.",
        ]
    )

    return "\n".join(sections) + "\n"


def clean_thesis_artifacts() -> None:
    """Remove common LaTeX auxiliary files from the thesis directory."""
    patterns = (
        "*.aux",
        "*.bbl",
        "*.bcf",
        "*.blg",
        "*.fdb_latexmk",
        "*.fls",
        "*.lof",
        "*.log",
        "*.lot",
        "*.out",
        "*.run.xml",
        "*.synctex.gz",
        "*.toc",
        "*.xdv",
    )
    for pattern in patterns:
        for path in THESIS_DIR.glob(pattern):
            if path.is_file():
                path.unlink()

    for aux_file in CHAPTERS_DIR.glob("*.aux"):
        if aux_file.is_file():
            aux_file.unlink()
    for pattern in ("*.bbl", "*.blg", "*.bcf"):
        for path in CHAPTERS_DIR.glob(pattern):
            if path.is_file():
                path.unlink()


def run_build_command(command: list[str], cwd: Path) -> None:
    """Run a build command and raise a readable error on failure."""
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def build_with_tectonic(backend: str, bibliography_tool: bool) -> None:
    """Build with Tectonic, using Biber explicitly when biblatex requires it."""
    tectonic_command = ["tectonic", "--keep-intermediates", "--keep-logs", "main.tex"]
    tectonic_manual_pass = ["tectonic", "--keep-intermediates", "--keep-logs", "--reruns", "0", "main.tex"]
    tectonic_tex_pass = [
        "tectonic",
        "--keep-intermediates",
        "--keep-logs",
        "--reruns",
        "0",
        "--pass",
        "tex",
        "main.tex",
    ]
    tectonic_bibtex_pass = [
        "tectonic",
        "--keep-intermediates",
        "--keep-logs",
        "--reruns",
        "0",
        "--pass",
        "bibtex_first",
        "main.tex",
    ]
    if backend == "biber":
        if not bibliography_tool:
            raise SystemExit("Tectonic builds with `backend=biber` require `biber` on PATH.")
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        run_build_command(["biber", "main"], THESIS_DIR)
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        return
    if backend == "bibtex":
        # Tectonic can run its bundled BibTeX engine via `--pass bibtex_first`,
        # while the normal TeX pass is still needed at the end so the PDF is
        # regenerated after references and citations have settled.
        run_build_command(tectonic_tex_pass, THESIS_DIR)
        run_build_command(tectonic_bibtex_pass, THESIS_DIR)
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        return
    if bibliography_tool:
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        run_build_command([backend, "main"], THESIS_DIR)
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        run_build_command(tectonic_manual_pass, THESIS_DIR)
        return

    run_build_command(tectonic_command, THESIS_DIR)


def build_thesis(mode: str, image: str, clean: bool) -> None:
    """Build the thesis PDF using the selected toolchain."""
    tools = toolchain_status()
    backend = tools["bibliography_backend"]
    local_tex_ready = tools["local_tex_ready"]
    docker_ready = tools["docker_daemon"]

    if clean:
        clean_thesis_artifacts()

    if mode == "auto":
        if local_tex_ready:
            mode = "local"
        elif docker_ready:
            mode = "docker"
        else:
            raise SystemExit(
                f"No usable build path found. Install `latexmk` + `xelatex` + `{backend}`, install `tectonic`, or start Docker Desktop and retry."
            )

    if mode == "local":
        if tools["latexmk"] and tools["xelatex"]:
            run_build_command(
                ["latexmk", "-xelatex", "-interaction=nonstopmode", "-file-line-error", "main.tex"],
                THESIS_DIR,
            )
        elif tools["xelatex"] and tools["bibliography_tool"]:
            run_build_command(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], THESIS_DIR)
            run_build_command([backend, "main"], THESIS_DIR)
            run_build_command(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], THESIS_DIR)
            run_build_command(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], THESIS_DIR)
        elif tools["tectonic"]:
            build_with_tectonic(backend, tools["bibliography_tool"])
        else:
            raise SystemExit(f"Local build requires `latexmk` + `xelatex`, manual `xelatex` + `{backend}`, or `tectonic` on PATH.")
    elif mode == "docker":
        if not tools["docker_cli"]:
            raise SystemExit("Docker mode requires the `docker` CLI.")
        if not docker_ready:
            raise SystemExit("Docker mode requires a running Docker daemon. Start Docker Desktop and retry.")
        run_build_command(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{ROOT}:/workspace",
                "-w",
                "/workspace/thesis",
                image,
                "latexmk",
                "-xelatex",
                "-interaction=nonstopmode",
                "-file-line-error",
                "main.tex",
            ],
            ROOT,
        )
    else:
        raise ValueError(f"Unsupported build mode: {mode}")

    pdf_path = THESIS_DIR / "main.pdf"
    if not pdf_path.exists():
        raise SystemExit("Build completed without producing thesis/main.pdf.")
    print(f"Built {relative(pdf_path)}")


def write_or_print(text: str, output: Path | None) -> None:
    """Write to a file or print to stdout."""
    if output is None:
        print(text, end="")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {relative(output)}")


def generate_status(output: Path | None) -> None:
    """Generate the repo status report."""
    data = build_status_data()
    report = format_status_markdown(data)
    write_or_print(report, output)


def generate_packet(chapter_key: str, output: Path | None) -> None:
    """Generate a packet for a specific chapter."""
    config = WORKFLOW_CONFIG[chapter_key]
    packet = build_packet_markdown(config)
    if output is None:
        ensure_output_dir()
        output = GENERATED_DIR / f"{chapter_key}_packet.md"
    write_or_print(packet, output)


def generate_packets(remaining_only: bool) -> None:
    """Generate packets for all configured chapters or only the remaining ones."""
    status_rows = {row["name"]: row for row in chapter_status()}
    keys = []
    for key, config in WORKFLOW_CONFIG.items():
        chapter_row = status_rows.get(config.chapter_file.name)
        if remaining_only and chapter_row and not chapter_row["is_stub"]:
            continue
        keys.append(key)

    if not keys:
        print("No matching chapter packets to generate.")
        return

    ensure_output_dir()
    for key in keys:
        generate_packet(key, GENERATED_DIR / f"{key}_packet.md")


def validate(output: Path | None) -> None:
    """Run lightweight workflow validation."""
    data = build_status_data()
    report = format_validation_markdown(data)
    write_or_print(report, output)


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    if args.command == "status":
        generate_status(args.output)
    elif args.command == "packet":
        generate_packet(args.chapter, args.output)
    elif args.command == "packets":
        generate_packets(args.remaining)
    elif args.command == "validate":
        validate(args.output)
    elif args.command == "build":
        build_thesis(args.mode, args.image, args.clean)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
