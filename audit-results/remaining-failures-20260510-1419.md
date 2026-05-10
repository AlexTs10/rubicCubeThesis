# Remaining Audit Findings - 2026-05-10 14:19

The 2026-05-10 14:19 ChatGPT Pro audit produced a mix of local quick fixes, non-local institutional blockers, and larger research/reproducibility work.

## Non-local institutional blocker

- `thesis/chapters/00_approval.tex`: the final approval page still requires official committee member names, titles, signatures, and examination date. These cannot be invented locally and must come from the institutional record.

## Larger local/research work not completed in this loop

- `README.md` / `tests/`: the coverage gate remains too low for a strict thesis review. The next local slice should add focused tests for evaluation statistics, validation reporting, visualization data preparation, and benchmark export logic, then raise the gate in stages.
- `results/benchmarks/thesis/thesis_results_combined.json`: the canonical corpus still documents `legacy_random_all_moves_redundant_allowed`. A stronger submission needs a regenerated benchmark with a stricter scramble policy or an additional verified optimal-distance-stratified benchmark, followed by updated Chapter 7 tables/figures.
- `results/benchmarks/thesis/thesis_results_combined.json`: timing methodology still needs warmup, repeated runs, runtime package snapshot, and medians/IQRs or confidence intervals generated from repeated runs.
- `results/benchmarks/thesis/thesis_results_combined.json`: external backend provenance still needs wheel filename/hash, PyPI artifact URL/version, upstream commit or release tag, and formal license evidence.
- `results/validation/native_exact/README.md`: the source-ZIP native-exact profile is reproducible, but the full canonical 3,513-case validation still needs deterministic cache regeneration, a hashed external cache artifact, or narrowed thesis claims.

## Local fixes applied from this audit

- `.github/workflows/thesis-build.yml`: webapp validation now reads the Node version from `.nvmrc` and activates npm 11.6.0 before `npm ci`.
- `thesis/chapters/07_evaluation.tex`: corrected the duplicated/mismatched Greek phrase.
- `thesis/chapters/00_approval.tex`: tightened vertical spacing to keep the approval/signature block on one page.
