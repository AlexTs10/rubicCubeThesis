# Remaining validation and audit notes

Audit source: `audit-results/chatgpt-pro-audit-20260509-0932/`

## Resolved in this loop

- Default pytest profile now excludes Kociemba move-table loading, native coordinate heuristic cache construction, and Thistlethwaite pattern-database loading tests.
- `verify_setup.py` now uses a 120 s fast-profile timeout and has an optional notebook smoke check.
- Canonical native exact validation now checks the required corner DB before constructing heavy heuristics and exits with a clear prerequisite message when it is absent.
- Source-ZIP native exact smoke validation still completes with 261 cases and 0 failures.
- Thistlethwaite and internal Kociemba solver APIs now verify returned move sequences even when `verbose=False`.
- Benchmark summary exports now include timeout/failure counts and timeout-capped timing metrics; benchmark JSON now includes environment metadata.
- README/data/thesis/notebook docs no longer present excluded generated workflow outputs or generated cache trees as current source-ZIP contents.
- `conj_twist` is excluded from audit manifests/packages as an ignored generated exact-solver data file.
- The overfull Chapter 7 robust summary table was rewritten with `tabularx`; the thesis build no longer reports that overfull hbox.
- Unused bibliography entries were removed; citation scan now reports 31 BibTeX keys, 31 cited keys, 0 missing, 0 unused.

## Remaining blockers or deferred items

- `thesis/main.tex` and `thesis/chapters/00_approval.tex`: final institutional approval/signature page still needs real committee names and examination date. This cannot be completed locally without authoritative university details.
- `npm audit --audit-level=moderate`: still reports a PostCSS advisory through Next.js. The proposed `npm audit fix --force` would downgrade Next to `9.3.3`, so it remains intentionally unapplied.
- `pyproject.toml` still exposes the source package as `src.*`. Renaming imports to a project-specific package remains a broad migration and was not mixed into this audit cleanup.
- Canonical native exact validation still depends on the generated `data/pattern_databases/corner_db.pkl` artifact. The command now fails fast when missing, but the heavy cache itself is still not included in source ZIPs.
- Benchmark data was not rerun with repeated trials, confidence intervals, isolated peak RSS, or cold/warm separation. The thesis and code now disclose/add supporting metrics, but the original benchmark artifact remains single-run.
- Notebook validation is currently a source smoke check, not full notebook execution.
- Thesis build still has non-fatal underfull hbox warnings in prose/list-of-table/bibliography lines.

## Validation run

- `python -m compileall -q src scripts verify_setup.py`: passed.
- `python -m pytest tests --collect-only -q`: passed; 276/299 collected, 23 deselected.
- `python -m pytest tests/unit/test_algorithm_comparison.py tests/unit/test_benchmark_artifacts.py tests/unit/test_kociemba.py::TestKociembaSolver::test_internal_backend_rejects_unverified_solution tests/unit/test_thistlethwaite.py::TestThistlethwaiteSolver::test_solver_rejects_unverified_solution_when_not_verbose -q`: passed; 12 passed.
- `python -m pytest tests -q`: passed; 275 passed, 1 skipped, 23 deselected in 18.06 s.
- `python verify_setup.py --notebooks`: passed; 8/8 checks.
- `python scripts/verify_notebooks.py`: passed; 6 notebooks parse with metadata.
- `python scripts/verification/native_exact_validation.py --preset canonical` with `corner_db.pkl` temporarily absent: expected failure, exit 2, clear prerequisite message.
- `python scripts/verification/native_exact_validation.py --preset source-zip --output-dir audit-results/native-exact-source-zip-smoke-20260509-0932`: passed; 261 cases, 0 failures.
- `python scripts/thesis_workflow.py build --mode auto`: passed; produced `thesis/main.pdf`.
- `cd webapp && npm run lint`: passed.
- `cd webapp && npm test`: passed; 7 tests.
- `cd webapp && npm run build`: passed.
- `cd webapp && npm audit --audit-level=moderate`: failed; PostCSS advisory through Next.js, unsafe downgrade suggested by npm.
