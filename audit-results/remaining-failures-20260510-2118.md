# Remaining Non-Local Audit Blockers - 2026-05-10 21:18

Latest external audit: `audit-results/chatgpt-pro-audit-20260510-2118/`

These targets are not safely fixable from the repository alone because they
require official institutional data, regenerated benchmark campaigns, companion
artifacts, or third-party provenance.

## Official Submission Metadata

- `thesis/chapters/00_approval.tex` still needs the official remaining
  committee names/titles and examination date from the University of Patras.
- `README.md` and `REPRODUCIBILITY.md` must keep the technical-review wording
  until that official approval page is complete.

## Larger Test And Benchmark Campaign

- Raising the coverage gate from 49% to 60% requires a dedicated test pass over
  evaluation/statistics/visualization and generated-table logic. This was not
  treated as a mechanical local edit because it changes the test campaign scope.
- Benchmark methodology targets require rerunning the canonical benchmark with
  repeated trials, warmup/cold-start separation, interval estimates, runtime
  environment capture, and/or isolated peak-RSS measurement.
- The canonical benchmark corpus remains the archived legacy corpus unless the
  full `thesis_bench_d*.json` set is regenerated and the thesis tables/figures
  are updated from that new campaign.

## External Artifacts

- Canonical native-exact validation still requires the omitted
  `data/pattern_databases/corner_db.pkl` companion cache or a documented clean
  generation run with SHA-256.
- The external `RubikOptimal` backend still lacks a complete upstream
  commit/tag or archived source/wheel provenance bundle beyond the installed
  metadata and file hashes already recorded.

## PDF Build Evidence

- Reviewer-independent PDF rebuild evidence depends on a Docker-enabled or CI
  environment and a recorded `thesis/main.pdf` SHA-256 from that run.
