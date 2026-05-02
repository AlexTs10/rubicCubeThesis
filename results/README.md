# Results Directory

This directory contains versioned benchmark artifacts and validation reports referenced by the thesis.

## Current Structure

```text
results/
├── benchmarks/
│   └── thesis/
└── validation/
    └── native_exact/
```

## Benchmarks

`results/benchmarks/thesis/` is the canonical location for the thesis benchmark corpus:

- `thesis_bench_d5.json`
- `thesis_bench_d10.json`
- `thesis_bench_d15.json`
- `thesis_bench_d20.json`
- `thesis_results_combined.json`

These files are the benchmark artifacts referenced in Chapter 7 and Appendix A.

`thesis_results_combined.json` is the final combined benchmark artifact. It contains 100 rows across requested scramble depths 5, 10, 15, and 20, with 25 scrambles per requested depth. Its metadata records `korf_backend: "optimal_external"`, `korf_guarantees_optimal: true`, and enforced Korf timeout handling. The per-depth files are the shards used to build that combined artifact.

## Validation

`results/validation/native_exact/` contains time-stamped native exact solver validation reports produced during the Path A / native-exact verification work.

The most relevant reports for the current thesis claims are the later March 22, 2026 runs, especially the corner-PDB-enabled validation outputs.

Use `results/validation/native_exact/MANIFEST.json` and `results/validation/native_exact/README.md` to identify which reports are canonical for the thesis and which older files are exploratory leftovers.

## Notes

- There is no active `results/reports/` tree in the current repository layout.
- Benchmark regeneration scripts live in `scripts/benchmarks/`.
- Validation scripts live in `scripts/verification/`.
- Keep thesis benchmark artifacts and validation reports separate; they support different claims.
- There is no top-level `TESTING_REPORT.md` in the current checkout; use the repo README verification snapshot and fresh command output instead of stale copied reports.
