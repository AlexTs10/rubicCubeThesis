# Remaining Non-Local Audit Blockers - 2026-05-10 15:46

Latest audit thread: https://chatgpt.com/c/6a007a20-d010-83eb-a085-45617ef853ea

## Still Blocked Outside Safe Local Edits

- `thesis/chapters/00_approval.tex` and rebuilt `thesis/main.pdf`: final University of Patras committee member names/titles and official examination date are still required. These cannot be invented locally.
- `.github/workflows/thesis-build.yml` coverage gate: raising from 49% to 65% requires a focused test expansion across evaluation, Kociemba, Korf, and Thistlethwaite modules. Raising the gate without those tests would intentionally break validation.
- `thesis/chapters/07_evaluation.tex` and `results/benchmarks/thesis/*`: repeated-run benchmarks, confidence intervals, cold/warm separation, verified optimal-distance grouping, and isolated peak-RSS measurement require a new experimental campaign.
- `results/validation/native_exact/*`: canonical native-exact reproduction from only submitted artifacts still requires a generated `data/pattern_databases/corner_db.pkl` companion cache and the optional `RubikOptimal` oracle.
- `results/benchmarks/thesis/thesis_results_combined.json`: closing upstream provenance requires an exact external backend source archive/commit/tag and license artifact. The currently installed wheel metadata does not expose that identity, so it should not be fabricated.
- `thesis/main.pdf`: the current XeLaTeX/Tectonic path can carry richer document metadata, but fully tagged/accessible PDF output may require a different institutional PDF workflow or post-processing tool.

## Local Mitigations Applied In This Loop

- Saved the full audit artifacts under `audit-results/chatgpt-pro-audit-20260510-1546/`.
- Added a scheduled/manual expanded CI validation job for opt-in `slow`, `external`, and `cache_building` tests.
- Added a containerized webapp review path so reviewers do not have to manually discover Node 24.9/npm 11.6.
- Added richer thesis PDF metadata support and documented the tagging limitation separately from metadata.
