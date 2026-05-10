# Remaining Non-Local Audit Blockers - 2026-05-10 21:46

Latest external audit: `audit-results/chatgpt-pro-audit-20260510-2146/`

The local pass addressed the actionable repository items from this audit:

- added focused evaluation tests and raised the CI coverage gate to 60%;
- added an explicit `webapp/README.md` note that the Next.js app is a
  synthetic preview and not benchmark or solver-correctness evidence;
- tightened the Chapter 7 Greek prose around JSON artifacts, benchmark corpus,
  backend wording, and logs.

The following blockers remain outside a safe local-only repair.

## Official Submission Metadata

- `thesis/chapters/00_approval.tex` still needs the official remaining
  committee names/titles and examination date from the University of Patras.
- `README.md` and `REPRODUCIBILITY.md` must keep the technical-review wording
  until the official approval page is complete.

## Benchmark Provenance

- `results/benchmarks/thesis/thesis_results_combined.json` still contains
  post-hoc benchmark environment metadata and incomplete upstream provenance for
  the external exact backend. A complete fix requires a rerun or signed archival
  reproduction log with the exact command, OS build, Python version, dependency
  lock hash, external wheel/source hash, upstream release/commit if available,
  hardware details, and timestamp.

## Native Exact Companion Artifact

- The full 3,513-case canonical native-exact validation still requires
  `data/pattern_databases/corner_db.pkl` as a companion cache, or a documented
  clean regeneration transcript with SHA-256, hardware, and timing evidence.
