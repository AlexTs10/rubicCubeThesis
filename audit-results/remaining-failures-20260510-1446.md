# Remaining Audit Findings - 2026-05-10 14:46

## Non-local institutional blocker

- `thesis/chapters/00_approval.tex` and `README.md`: final submission still requires official committee names, titles, signatures, and examination date. These cannot be invented locally.

## Larger local/research work not completed in this loop

- Coverage remains below a stricter thesis-artifact bar. The current gate is still 49%; raising it to 65%+ requires focused test expansion for evaluation/statistics/validation/visualization and solver-support modules.
- `src/korf/validation.py::load_cube20_data()` remains a stub. Implementing this properly requires selecting and documenting an accepted cube20/known-distance input format plus fixtures.
- The main benchmark corpus still needs repeated runs, warmup/cold-start separation, statistical intervals, and stronger runtime provenance.
- Requested scramble length is still not equivalent to verified optimal depth; a future analysis should group exact-completed cases by `verified_scramble_depth`.
- Canonical native-exact validation still requires omitted/generated cache and optional oracle artifacts. The source-ZIP smoke profile remains reproducible, but the full canonical path needs deterministic cache generation, a hashed external artifact, or narrower claims.
- External backend provenance should be embedded directly in `results/benchmarks/thesis/thesis_results_combined.json`.
- The clean-machine thesis rebuild story still depends on TeX/Tectonic or Docker availability; the next stronger path is a documented container-first reviewer flow.

## Local fixes applied from this audit

- `thesis/chapters/07_evaluation.tex`: moved the timing-table caveat next to the timing table.
- `thesis/chapters/05_korf.tex`: changed pseudocode `None` returns to `\texttt{None}` and displayed the long native-exact file path.
- `webapp/package.json` and `webapp/package-lock.json`: relaxed Node/npm engines to tested major-version ranges while keeping `.nvmrc`/`packageManager` as the recommended pinned baseline.
- `verify_setup.py` and `README.md`: clarified that the default setup verifier is Python-only unless `--all-artifacts` is supplied.
- `docs/THESIS_OUTLINE.md` and `docs/PATH_A_NATIVE_EXACT_PLAN.md`: strengthened historical-document warnings.
