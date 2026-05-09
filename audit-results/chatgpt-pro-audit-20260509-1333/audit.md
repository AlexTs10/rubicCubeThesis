# ChatGPT Pro Audit 2026-05-09 13:33

Source thread: https://chatgpt.com/c/69ff0621-40a8-83eb-9eef-44bd0f791b17

Uploaded ZIP: `repo-audit-20260509-1252.zip`

Note: ChatGPT UI copy failed with "Failed to copy to clipboard"; this file was transcribed from the visible ChatGPT accessibility tree.

## Audit Basis

ChatGPT Pro audited only `/mnt/data/repo-audit-20260509-1252.zip`, extracted locally. It did not use GitHub or external repositories. It verified the repository manifest, inspected the thesis PDF/source, checked LaTeX chapter files, reviewed Python implementation, benchmark scripts, validation artifacts, docs, README/setup files, and ran the default Python test suite.

Verified positives:
- Manifest hashes matched files in the ZIP.
- Default Python tests passed: `275 passed, 1 skipped, 28 deselected`.
- Thesis bibliography had no missing or unused cited BibTeX keys according to the repository workflow.
- Checked-in PDF rendered and did not show obvious unresolved citation placeholders.

## Critical Blockers

### CB-01 - Final institutional approval page is still excluded and contains placeholders

Severity: Critical external dependency / final submission blocker

Files: `thesis/main.tex`; `thesis/chapters/00_approval.tex`; `thesis/README.md`

Locations: `thesis/main.tex:173-180`; `thesis/chapters/00_approval.tex:30-44`; `thesis/README.md:1-4`

Problem: The thesis source explicitly excludes the formal approval/signature page, while `00_approval.tex` still contains placeholder committee entries and a placeholder date.

Why it matters: The repository may be academically and technically mature, but the thesis is not institutionally submission-ready until this page is completed and included. This is disclosed, but still a final submission blocker.

Exact fix: Fill official committee names, roles, and examination date; include approval page in `thesis/main.tex`; rebuild `thesis/main.pdf`; remove or update the warning in `thesis/README.md`.

Verification: Search for approval placeholders, rebuild, inspect generated PDF front matter.

## Thesis Writing Issues

### TW-01 - A* pseudocode is incomplete for graph-search optimality

Severity: Major

File: `thesis/chapters/02_background.tex`

Location: `thesis/chapters/02_background.tex:281-299`

Problem: A* pseudocode uses open/closed sets but does not show `g_score`, stale-entry checks, decrease-key/update logic, or reopening of improved states.

Exact fix: Revise pseudocode to maintain best known `g` per state, skip stale heap entries, update open entries on better paths, and reopen closed states when needed, or explicitly state a consistency assumption.

### TW-02 - Thistlethwaite memory claim conflicts with implementation and table description

Severity: Major

Files: `thesis/chapters/03_thistlethwaite.tex`; `src/thistlethwaite/tables.py`

Locations: `thesis/chapters/03_thistlethwaite.tex:262-278`; `thesis/chapters/03_thistlethwaite.tex:329-333`; `src/thistlethwaite/tables.py:561-641`; `src/thistlethwaite/tables.py:823-849`

Problem: Thesis claims approximately `1.2 MB for all PDBs`, but the same chapter lists a phase-3 exact table with `663,552` states stored as a Python `dict`, and implementation builds/loads that dictionary.

Exact fix: Distinguish compact NumPy coordinate tables from Python runtime overhead; report measured process RSS or serialized artifact size separately.

### TW-03 - Kociemba pruning tables are described as exact full-state minimum-distance tables, but implementation uses capped tables

Severity: Major

Files: `thesis/chapters/04_kociemba.tex`; `src/kociemba/pruning.py`; `src/kociemba/solver.py`

Locations: `thesis/chapters/04_kociemba.tex:203-204`; `src/kociemba/pruning.py:4-7`; `src/kociemba/pruning.py:64-71`; `src/kociemba/pruning.py:192-193`; `src/kociemba/solver.py:132-134`

Problem: Thesis says pruning tables store minimum distance from every state to the goal. Implementation documents and uses `max_depth`-capped BFS tables; unreached states are filled with cutoff value.

Exact fix: State that tables store exact distances for states reached within BFS cutoff and represent unreached states by cutoff, producing clipped pruning estimates.

### TW-04 - "Native" terminology is ambiguous

Severity: Minor

Files: `README.md`; `thesis/chapters/08_implementation.tex`; `src/kociemba/solver.py`

Locations: `README.md:101`; `thesis/chapters/08_implementation.tex:119`; `src/kociemba/solver.py:36-39`; `src/kociemba/solver.py:95-98`

Problem: "Native" is used for the optional `kociemba` package backend while the repository also discusses repository-native exact Korf functionality.

Exact fix: In prose, rename to "optional PyPI/native-extension kociemba backend" or "external kociemba package backend"; keep code labels where required.

## Technical/Code Issues

### TC-01 - `AStarSolver` can overstate optimality guarantees

Severity: Major

File: `src/korf/a_star.py`

Locations: `src/korf/a_star.py:77-95`; `src/korf/a_star.py:141-220`; `src/korf/a_star.py:267-278`

Problem: `AStarSolver` accepts `heuristic_is_admissible=True` and reports an optimality guarantee, but implementation uses a closed set without maintaining best `g` scores or reopening states if a better path is discovered.

Exact fix: Add `best_g` tracking, stale heap-entry skipping, and reopen logic for improved paths. Alternatively require `heuristic_is_consistent=True` before reporting an optimality guarantee. Add regression tests.

### TC-02 - Canonical native-exact validation can silently degrade when oracle is unavailable

Severity: Major

Files: `scripts/verification/native_exact_validation.py`; `src/korf/optimal_solver.py`

Locations: `scripts/verification/native_exact_validation.py:155-197`; `scripts/verification/native_exact_validation.py:315-317`; `scripts/verification/native_exact_validation.py:442-453`; `src/korf/optimal_solver.py:55`

Problem: Canonical validation uses external optimal oracle only if `OPTIMAL_AVAILABLE` is true. If false, random generated cases can fall back to generated scramble length as expected depth.

Exact fix: For canonical preset, fail hard if oracle cases are requested and `OPTIMAL_AVAILABLE` is false, or skip oracle-dependent random cases with an explicit record.

## Research/Experimental Issues

### RE-01 - Canonical benchmark overwrite can fall back to heuristic Korf

Severity: Medium

Files: `scripts/benchmarks/regenerate_thesis_benchmarks.py`; `src/evaluation/algorithm_comparison.py`

Locations: `scripts/benchmarks/regenerate_thesis_benchmarks.py:51-55`; `scripts/benchmarks/regenerate_thesis_benchmarks.py:80-84`; `scripts/benchmarks/regenerate_thesis_benchmarks.py:232-239`; `src/evaluation/algorithm_comparison.py:202-240`; `src/evaluation/algorithm_comparison.py:795-838`

Problem: `--korf-backend auto` can fall back to heuristic Korf; `--overwrite-canonical` can still write artifacts that no longer support exact-backend claims.

Exact fix: When `--overwrite-canonical` is used, require `--korf-backend optimal` and assert resolved backend is `optimal_external` before writing canonical files.

### RE-02 - Original benchmark lacks full runtime metadata/provenance

Severity: Medium documented limitation

Files: `results/benchmarks/thesis/thesis_results_combined.json`; `thesis/chapters/07_evaluation.tex`

Locations: `results/benchmarks/thesis/thesis_results_combined.json:120-144`; `thesis/chapters/07_evaluation.tex:8-20`; `thesis/chapters/07_evaluation.tex:125-132`

Problem: Benchmark JSON says metadata is post-hoc archive metadata and original run did not record full hardware/package metadata or external backend wheel hash/upstream commit. Thesis does not make this provenance limitation as explicit as JSON.

Exact fix: Rerun canonical benchmarks with captured metadata or add explicit caveat in Chapter 7 and Appendix A matching JSON limitation.

## Citation/Reference Issues

### CR-01 - Pattern-database additivity explanation is mathematically oversimplified

Severity: Major

Files: `thesis/chapters/02_background.tex`; `thesis/chapters/06_heuristics.tex`

Locations: `thesis/chapters/02_background.tex:396-404`; `thesis/chapters/06_heuristics.tex:255-268`

Problem: Chapter 2 says estimates from disjoint PDBs can be summed while preserving admissibility when they cover disjoint subsets. Chapter 6 gives the more correct condition: additive PDBs require independent abstractions or cost partitioning.

Exact fix: Rewrite Chapter 2 so `max` over admissible PDBs is generally safe, while summation requires cost partitioning or operator-disjoint abstractions.

## Reproducibility/Setup Issues

### RS-01 - Python lock file is exact-version pinned but not hash-locked

Severity: Minor documented limitation

Files: `README.md`; `requirements.lock`

Locations: `README.md:39-43`; `requirements.lock:1-139`

Problem: README correctly discloses that `requirements.lock` pins versions but lacks cryptographic hashes.

Exact fix: Generate a hash-locked requirements file and update README command.

### RS-02 - Kociemba docs say cached tables are present, but source ZIP omits generated caches

Severity: Medium

Files: `docs/algorithms/kociemba.md`; `data/README.md`

Locations: `docs/algorithms/kociemba.md:29-33`; `docs/algorithms/kociemba.md:90-98`; `data/README.md:1-4`

Problem: Kociemba docs say cached tables are present under `data/kociemba/`, but `data/README.md` says generated cache trees are absent from source ZIP.

Exact fix: Say tables are generated locally and cached after first build, not shipped in source ZIP.

## Submission Polish Issues

### SP-01 - Kociemba docs give incorrect Phase-2 state-space number

Severity: Medium

Files: `docs/algorithms/kociemba.md`; `thesis/chapters/04_kociemba.tex`; `src/kociemba/solver.py`

Locations: `docs/algorithms/kociemba.md:19-27`; `thesis/chapters/04_kociemba.tex:31-45`; `src/kociemba/solver.py:10-18`

Problem: `docs/algorithms/kociemba.md` gives `39,038,976,000`, while thesis/code use the correct distinction between raw coordinate combinations and parity-valid Phase-2 states.

Exact fix: Replace with raw coordinate combinations `40,320 x 40,320 x 24 = 39,016,857,600`; parity-valid Phase-2 states `19,508,428,800`.

### SP-02 - Distance-estimator documentation is stale about nibble compression and memory size

Severity: Medium

Files: `docs/DISTANCE_ESTIMATOR_README.md`; `src/korf/pattern_database.py`; `data/README.md`

Locations: `docs/DISTANCE_ESTIMATOR_README.md:15-18`; `docs/DISTANCE_ESTIMATOR_README.md:149-182`; `docs/DISTANCE_ESTIMATOR_README.md:245-247`; `src/korf/pattern_database.py:8-12`; `src/korf/pattern_database.py:34-37`; `src/korf/pattern_database.py:50-53`; `data/README.md:50-54`

Problem: Documentation still describes nibble-compressed corner DB storage and about `44 MB`, while current implementation uses exact-safe byte storage with `255` sentinel and data README says corner cache is about `100 MB`.

Exact fix: Update docs to byte-per-entry exact-safe storage, `255` sentinel, historical legacy-nibble loader if relevant, and current expected cache size.

### SP-03 - Distance-estimator documentation overclaims admissibility of lightweight heuristics

Severity: Major

Files: `docs/DISTANCE_ESTIMATOR_README.md`; `src/korf/heuristics.py`; `thesis/chapters/06_heuristics.tex`

Locations: `docs/DISTANCE_ESTIMATOR_README.md:30-42`; `docs/DISTANCE_ESTIMATOR_README.md:203-210`; `docs/DISTANCE_ESTIMATOR_README.md:245-252`; `src/korf/heuristics.py:4-7`; `thesis/chapters/06_heuristics.tex:89-92`

Problem: Documentation says lightweight heuristics are made admissible, but implementation and thesis correctly state these simple heuristics are rough estimates and not blanket lower bounds.

Exact fix: Rewrite distance-estimator README to claim admissibility only for validated exact-safe PDB/native-coordinate heuristics under the documented combination rule; simple heuristics are exploratory/ranking estimates.

### SP-04 - Historical native-exact plan contains stale "currently uses nibble" statement

Severity: Minor

Files: `docs/PATH_A_NATIVE_EXACT_PLAN.md`; `src/korf/pattern_database.py`

Locations: `docs/PATH_A_NATIVE_EXACT_PLAN.md:1-7`; `docs/PATH_A_NATIVE_EXACT_PLAN.md:76-78`; `docs/PATH_A_NATIVE_EXACT_PLAN.md:532-559`; `src/korf/pattern_database.py:8-12`

Problem: Historical/current-state notes still say `pattern_database.py` currently uses nibble value `15` as sentinel. Current implementation says this was replaced by byte storage.

Exact fix: Change phrase to "originally used" or add resolved note pointing to byte-storage implementation.

## Scores

- Overall thesis quality score: 84/100
- Technical quality score: 78/100
- Submission readiness score: 66/100
