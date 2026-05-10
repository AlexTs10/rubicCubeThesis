# Remaining Non-Local Audit Blockers - 2026-05-10 23:17

The local source-owned findings from `chatgpt-pro-audit-20260510-2317` have
local fixes in this pass. The following items remain outside the repository's
authority or require heavyweight companion artifacts/campaigns.

## Official Approval Metadata

- Audit target: `submission_readiness`
- File: `thesis/chapters/00_approval.tex`
- Status: non-local blocker.
- Reason: the approval/signature page still needs final committee names,
  academic titles, and examination date from the University of Patras. These
  values should not be invented in source.

## Canonical Native-Exact Companion Artifact

- Audit target: `canonical_reproducibility`
- Files: `REPRODUCIBILITY.md`, `data/pattern_databases/corner_db.pkl`
- Status: documented companion-artifact requirement.
- Reason: the source audit ZIP intentionally excludes the generated corner PDB
  cache. The source-contained validation proves the smaller native-exact smoke
  tier; exact canonical reruns require regenerating or supplying the cache with
  a checksum manifest.

## Full Benchmark Campaign Upgrade

- Audit target: `benchmark_methodology`
- File: `thesis/chapters/07_evaluation.tex`
- Status: local wording narrowed; full campaign remains non-local.
- Reason: the thesis now labels timings as one-run observations on a fixed
  corpus. A statistically stronger campaign would require repeated trials,
  confidence intervals, cold/warm separation, and external-backend provenance.

## Final Submission Package Label

- Audit target: `submission_packaging`
- File: `README.md`
- Status: blocked by official approval metadata.
- Reason: the repository should remain labeled as a technical review package
  until the approval/signature page is complete.
