# Remaining validation and audit notes

Audit source: `audit-results/chatgpt-pro-audit-20260509-0802/`

## Resolved in this loop

- Default Python test profile no longer runs the slow pure-Thistlethwaite integration cases.
- The Streamlit comparison page now handles missing `memory_mb` values safely.
- Benchmark timing now uses `time.perf_counter()` and records timer/memory methodology metadata.
- Thesis Chapter 7 now lists the concrete benchmark JSON schema and scopes conclusions to the fixed corpus, backend, platform, and timeout policy.
- Abstracts and conclusions no longer overstate repository status or test-suite completeness.
- README, thesis README, Appendix A, and `data/README.md` now distinguish fast reviewer checks from slow/external/cache-building profiles.
- The source-ZIP validation path now has a lightweight native-exact smoke preset that does not require the omitted canonical corner database.
- Webapp tests now execute cube and solver-preview logic instead of only checking file text.
- Host-specific `agent_workflow/generated/` snapshots were removed and excluded from reproducibility manifests/packages.
- Recent arXiv bibliography entries now include structured arXiv metadata, and unused Wikipedia references were removed.

## Remaining blockers or deferred items

- `thesis/main.tex` / `thesis/chapters/00_approval.tex`: institutional front matter still needs real committee names, signatures, and examination date before final submission. This cannot be completed safely without authoritative university details.
- `npm audit --audit-level=moderate`: still reports `postcss <8.5.10` through the current Next.js dependency chain. The offered automated fix would force an unsafe downgrade to `next@9.3.3`, so it was intentionally not applied.
- `pyproject.toml`: the package is still named/imported as `src`. Renaming the installable package would be a broad import/API migration and was deferred rather than mixed into the audit cleanup commit.
- `requirements.lock`: remains a pinned package list, not a hash-locked cross-platform lock. Generating a hash lock needs a chosen lock tool and target platform policy.
- `results/benchmarks/thesis/thesis_results_combined.json`: benchmark measurements were not regenerated with repeated trials, confidence intervals, cold/warm separation, or isolated peak RSS. The thesis text now states the actual limitation instead of overstating the evidence.
- `data/pattern_databases/corner_db.pkl`: remains intentionally excluded from source ZIPs because it is generated/heavy. The documented mitigation is to regenerate it for canonical validation, while the new source-ZIP smoke preset verifies the archive without it.
- `python scripts/thesis_workflow.py build --mode auto`: passes, but LaTeX still reports non-fatal underfull/overfull boxes, including an overfull line around `thesis/chapters/07_evaluation.tex`.

## Validation run

- `python -m compileall -q src scripts verify_setup.py`: passed.
- `python -m pytest tests --collect-only -q`: passed; 284/297 collected, 13 deselected.
- `python -m pytest tests/unit/test_algorithm_comparison.py tests/unit/test_validation_dataset.py tests/unit/test_thistlethwaite.py -q`: passed; 34 passed, 3 deselected.
- `python -m pytest tests -q`: passed; 283 passed, 1 skipped, 13 deselected.
- `python scripts/verification/native_exact_validation.py --preset source-zip --output-dir audit-results/native-exact-source-zip-smoke-20260509-081858`: passed; 261 cases, 0 failures.
- `python verify_setup.py`: passed; 7/7 checks.
- `cd webapp && npm run lint`: passed.
- `cd webapp && npm test`: passed; 7 tests.
- `cd webapp && npm run build`: passed.
- `python scripts/thesis_workflow.py build --mode auto`: passed; produced `thesis/main.pdf`.
- `cd webapp && npm audit --audit-level=moderate`: failed; PostCSS advisory through Next.js, unsafe downgrade suggested by npm.
