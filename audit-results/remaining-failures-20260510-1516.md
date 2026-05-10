# Remaining Non-Local Audit Blockers - 2026-05-10 15:16

Latest audit thread: https://chatgpt.com/c/6a00731e-ec5c-83eb-a68b-193962044ad6

## Still Blocked Outside Local Code Edits

- `thesis/chapters/00_approval.tex` and rebuilt `thesis/main.pdf`: final University of Patras committee member names/titles and official examination date are required. These cannot be invented locally.
- `results/benchmarks/thesis/*`: the audit asks for a second larger benchmark corpus with no consecutive same-face moves, multiple seeds, and recomputed Chapter 7 tables. That is a new experimental campaign, not a safe quick local patch.
- Timing evidence in `thesis/chapters/07_evaluation.tex`: repeated-trial benchmarks with warmup, cold/warm separation, and confidence intervals require a new benchmark run and regenerated result tables.
- Canonical native-exact validation: fully source-contained regeneration requires shipping or generating `data/pattern_databases/corner_db.pkl` as a companion artifact and having the optional `RubikOptimal` oracle available.
- External backend provenance: the installed `RubikOptimal 1.1.0` wheel metadata exposes package/file hashes but not a trustworthy upstream commit/tag. Do not fabricate `upstream_commit`; supply a matching upstream source artifact if this must be closed.

## Local Mitigations Applied In This Loop

- Clarified native versus external solver/backend claims in English and Greek abstracts.
- Added explicit Node/npm nvm/corepack setup before webapp `npm ci`.
- Added Docker-only thesis rebuild instructions.
- Added reproduction-tier tables mapping commands to required artifacts/backends and covered claims.
- Added a global webapp banner: "Synthetic preview only - not live solver telemetry."
- Clarified unsupported cube20.org ingestion in `src/korf/validation.py`.
