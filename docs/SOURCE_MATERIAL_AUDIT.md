# Source Material Import Audit

Generated for the repository migration from `/Users/alextoska/rubicCubeThesis`
into the main working repository at `/Users/alextoska/Desktop/rubicCubeThesis`.

## Imported Source Material

The complete source-plan folder was copied into this repository:

- `thesis_input_initial_plan/ΑΛΓΟΡΙΘΜΟΙ ΒΕΛΤΙΣΤΗΣ ΕΠΙΛΥΣΗΣ ΓΙΑ ΤΟΝ ΚΥΒΟ ΤΟΥ RUBIK.pdf`
- `thesis_input_initial_plan/table contents.md`
- `thesis_input_initial_plan/Comprehensive Academic Bibliography for Rubik's Cube Thesis.md`
- `thesis_input_initial_plan/compass_artifact_wf-40c0a645-be74-4936-8ae4-df78b1d70eaf_text_markdown.md`
- `thesis_input_initial_plan/Link and Extra Resources.md`
- `thesis_input_initial_plan/roadmap.md`
- `thesis_input_initial_plan/code phases with links.md`

PDF metadata for the original University topic document:

- Pages: 2
- Page size: A4
- SHA-256: `9a1464d2b55156310b2fc8ac3dd9d5c60936c0cee1d7bacf079c75509befa9fa`

The source PDF is a topic/plan document, not a full thesis manuscript. Its
explicit implementation goals are:

- implement Thistlethwaite, Kociemba, and Korf-style solvers in Python and/or
  Prolog;
- implement a distance-to-solved estimator;
- design heuristics for optimal solving with A* or a variant;
- run the implementation on a conventional computer;
- write the thesis around the implementation, evidence, and limitations.

## Current Repository Artifacts Covering The Plan

| Source-plan requirement | Current artifact |
| --- | --- |
| Core cube model and Singmaster moves | `src/cube/`, `tests/unit/test_rubik_cube.py`, `tests/unit/test_moves.py`, `tests/test_facelet_cubie_conversion.py` |
| Thistlethwaite implementation | `src/thistlethwaite/`, `tests/unit/test_thistlethwaite.py`, `tests/unit/test_thistlethwaite_tables.py` |
| Kociemba implementation | `src/kociemba/`, `tests/unit/test_kociemba.py`, `tests/unit/test_move_pruning_conventions.py` |
| Korf / exact optimal search path | `src/korf/optimal_solver.py`, `src/korf/native_exact_solver.py`, `tests/unit/test_optimal_solver.py`, `tests/unit/test_native_exact_solver.py`, `tests/integration/test_native_exact_oracle_agreement.py` |
| A* and IDA* variants | `src/korf/a_star.py`, `tests/unit/test_a_star_solvers.py` |
| Distance estimator and heuristics | `src/korf/distance_estimator.py`, `src/korf/composite_heuristic.py`, `tests/unit/test_distance_estimator.py`, `tests/unit/test_composite_heuristic.py` |
| Benchmark/evaluation evidence | `src/evaluation/`, `scripts/benchmarks/`, `results/benchmarks/thesis/`, `tests/unit/test_algorithm_comparison.py`, `tests/unit/test_benchmark_artifacts.py` |
| Written thesis | `thesis/main.tex`, `thesis/chapters/`, `thesis/references.bib`, `thesis/main.pdf` |
| Reproducibility and mapping | `README.md`, `REPRODUCIBILITY.md`, `docs/CODE_TO_THESIS_MAPPING.md`, `REPRODUCIBILITY_MANIFEST.json` |

## Old Directory Items Not Imported

The older directory also contains legacy top-level scripts, reports, task notes,
benchmark CSV/JSON files, and demo screenshots. These were intentionally not
copied into the main repository because the current repository already has
newer source-defined equivalents:

- old `tasks/` notes are superseded by the current implementation, tests, and
  thesis workflow;
- old top-level benchmark scripts are superseded by `scripts/benchmarks/`;
- old `TESTING_REPORT.md`, `results/validation_report.md`, and
  `results/comprehensive_test_*` outputs are historical snapshots, not current
  evidence;
- old `thesis_data_*.csv/json`, `thesis_benchmark_table.tex`, and
  screenshots are superseded by `results/benchmarks/thesis/` and
  `thesis/figures/`;
- old implementation files are behind the current `src/`, `tests/`, `ui/`, and
  `webapp/` trees.

Bringing those historical outputs into this repository would increase noise and
risk conflicting claims. The original source-plan folder is the only migrated
material that should remain as provenance.

## Known Non-Repo Blocker

The thesis can be built as a technical-review PDF from source, but the approval
page still needs official University of Patras committee names and examination
date before this repository can honestly be called a final signed submission
bundle.
