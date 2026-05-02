# Thesis Audit Report

Date: 2026-03-21

Workspace: repository root

Update note, 2026-05-02: this file is a historical audit log. Some findings below have since been partially or fully addressed. Current documentation checks in this checkout found `40` Python files under `src/` and `285 tests collected` with `python -m pytest tests --collect-only -q`; use the repo README and fresh command output for final verification instead of treating this March 21 snapshot as current truth.

Scope:
- thesis manuscript source
- canonical benchmark data
- figure generation
- test/reproducibility story
- Streamlit and Next.js application evidence
- benchmark and workflow scripts

This document records the findings from a full verification pass so they can be fixed later in a controlled way. Nothing here should be treated as a proposed patch yet; this is an audit log.

## Executive Summary

The project is not in a catastrophic state. The core positive facts are:
- the thesis manuscript builds successfully from source
- the canonical benchmark JSON is internally consistent
- the committed thesis figures regenerate exactly from the canonical JSON
- the Next.js webapp builds successfully after installing dependencies
- the integration tests pass

However, the repository and the thesis are not cleanly submission-ready. The main problems are:
- incomplete front matter
- stale thesis claims and counts
- misleading or overstated technical claims in several chapters
- obsolete benchmark scripts that can generate incorrect or contradictory thesis data
- an unstable test/reproducibility story
- missing screenshot evidence

## What Was Verified

### Builds

Verified successfully:
- `python scripts/thesis_workflow.py build --mode auto --clean`
- `tectonic main.tex` from `thesis/`
- `npm ci && npm run build` from `webapp/`

Notes:
- the thesis workflow build currently succeeds
- direct `tectonic` compilation also succeeds
- the Next.js webapp builds to static output after dependencies are installed

### Benchmark Data

Verified:
- `results/benchmarks/thesis/thesis_results_combined.json` matches the concatenation of:
  - `results/benchmarks/thesis/thesis_bench_d5.json`
  - `results/benchmarks/thesis/thesis_bench_d10.json`
  - `results/benchmarks/thesis/thesis_bench_d15.json`
  - `results/benchmarks/thesis/thesis_bench_d20.json`
- the combined benchmark dataset contains 100 scrambles total
- all 297 successful stored solver outputs solve their recorded scrambles
- every stored `solution_length` matches the stored move list length

Verified benchmark summary values:
- Thistlethwaite: `100/100`, average solution length `23.62`, average time `1.24s`
- Kociemba: `100/100`, average solution length `14.33`, average time `4.62s`
- Korf: `97/100`, average solution length `9.12` on completed runs, average time `2.66s`

### Figures

Verified:
- all seven PNG figures under `thesis/figures/` regenerate from the canonical benchmark JSON
- regenerated outputs were byte-identical to committed outputs
- implementation diagrams referenced by the thesis exist under `figures/diagrams/`

### Tests

Verified:
- `python -m pytest tests/integration -q` -> `13 passed`
- `python -m pytest tests/test_facelet_cubie_conversion.py -q` -> `3 passed`
- `python -m pytest tests/unit/test_algorithm_comparison.py -q` -> `4 passed`
- `python -m pytest tests --collect-only -q` -> historical result was `269 tests collected`; current 2026-05-02 result is `285 tests collected`

Important caveats:
- bare `pytest -q` from repo root is not reliable
- `python -m pytest tests/unit -q` is flaky because at least one test is nondeterministic
- `verify_setup.py` runs the supported full test command with a generous timeout

## High-Priority Findings

### 1. Approval Page Is Incomplete

Severity: high

Files:
- `thesis/chapters/00_approval.tex`

Details:
- `thesis/chapters/00_approval.tex:30-32` still contains placeholders:
  - `Μέλος Εξεταστικής Επιτροπής`
  - `Μέλος Εξεταστικής Επιτροπής`
- `thesis/chapters/00_approval.tex:39` leaves the date incomplete:
  - `Πάτρα, \hspace{2cm} 2026`

Impact:
- if this is intended to be a submission-ready thesis, the front matter is incomplete
- this issue also appears in the built PDF

Recommended later fix:
- replace placeholder committee members with real names
- fill the approval date properly or reword the page if it is intentionally pre-defense

### 2. Conclusions Overstate What Was Fully Achieved

Severity: high

Files:
- `thesis/chapters/01_introduction.tex`
- `thesis/chapters/05_korf.tex`
- `thesis/chapters/07_evaluation.tex`
- `thesis/chapters/09_conclusions.tex`

Details:
- `thesis/chapters/01_introduction.tex:52-58` preserves the original assignment goals:
  - implement Thistlethwaite, Kociemba, Korf
  - implement a component that computes distance from solved
  - find a suitable heuristic for optimal solving with A* or variant
- `thesis/chapters/09_conclusions.tex:6-10` rewrites those goals
- `thesis/chapters/09_conclusions.tex:13` then says the goals were achieved fully
- but the thesis itself states that the benchmarked Korf path is an external optimal backend:
  - `thesis/chapters/05_korf.tex:10-14`
  - `thesis/chapters/07_evaluation.tex:26-31`

Impact:
- the thesis risks claiming more native implementation completion than the code/evaluation path supports
- the “distance from solved” goal is also described in the thesis mostly as estimation, heuristics, and lower bounds, not clearly as an exact distance-computation component

Recommended later fix:
- restate the assignment goals precisely in the conclusions
- distinguish:
  - what was implemented natively in the repo
  - what was benchmarked through an external backend
  - what is heuristic or exploratory rather than exact

### 3. Obsolete Benchmark Scripts Can Produce Wrong Thesis Data

Severity: high

Files:
- `scripts/benchmarks/generate_thesis_data.py`
- `scripts/benchmarks/generate_complete_thesis_data.py`
- `scripts/benchmarks/regenerate_thesis_benchmarks.py`
- `src/kociemba/solver.py`

Details:

#### 3a. `generate_thesis_data.py` records Kociemba incorrectly

- `scripts/benchmarks/generate_thesis_data.py:99` calls `kociemba.solve(test_cube)`
- `scripts/benchmarks/generate_thesis_data.py:102` stores `len(solution)`
- but `src/kociemba/solver.py:186-206` documents that `solve()` returns:
  - `(solution, phase1_moves, phase2_moves)`
- therefore the script can record the tuple length instead of the number of solution moves

Impact:
- any `thesis_data_*.json` or CSV generated from this script is not trustworthy for Kociemba move counts

#### 3b. `generate_complete_thesis_data.py` is not the canonical thesis benchmark pipeline

- `scripts/benchmarks/generate_complete_thesis_data.py:3-4` says it compares only Thistlethwaite and Kociemba
- `scripts/benchmarks/generate_complete_thesis_data.py:173-177` hardcodes:
  - 10 scrambles per depth
  - 80 total tests
- `scripts/benchmarks/generate_complete_thesis_data.py:181` requires manual input before starting

Impact:
- it does not match the canonical thesis benchmark shape
- it does not match the 100-scramble, 3-algorithm dataset used in the thesis

#### 3c. Canonical thesis benchmark path

The only clean canonical regeneration path I found is:
- `scripts/benchmarks/regenerate_thesis_benchmarks.py`

The canonical data confirms:
- `results/benchmarks/thesis/thesis_results_combined.json:11` -> `total_scrambles_per_depth: 25`
- `results/benchmarks/thesis/thesis_results_combined.json:19` -> `korf_backend: "optimal_external"`

Recommended later fix:
- mark obsolete scripts clearly as legacy or remove them from thesis-facing docs
- make `regenerate_thesis_benchmarks.py` the only thesis benchmark regeneration path referenced in the manuscript and appendix

### 4. Thesis Uses External Korf Backend for Canonical Results

Severity: high

Files:
- `src/evaluation/algorithm_comparison.py`
- `results/benchmarks/thesis/thesis_results_combined.json`
- `thesis/chapters/05_korf.tex`
- `thesis/chapters/07_evaluation.tex`

Details:
- `src/evaluation/algorithm_comparison.py:173-183` auto-selects `KorfOptimalSolver()` when available
- it labels that backend as `optimal_external`
- the canonical benchmark metadata records:
  - `results/benchmarks/thesis/thesis_results_combined.json:19` -> `korf_backend: "optimal_external"`
  - `results/benchmarks/thesis/thesis_results_combined.json:21` -> `korf_guarantees_optimal: true`
- the manuscript acknowledges this in:
  - `thesis/chapters/05_korf.tex:10-14`
  - `thesis/chapters/07_evaluation.tex:26-31`

Impact:
- any thesis wording that implies the canonical Korf results are from the internal Python heuristic path is false

Recommended later fix:
- name the external backend explicitly in the thesis
- cite it properly
- explain exactly which results rely on it
- explain what remains native/research code inside the repo

### 5. Stale Counts and Repo Facts in the Thesis

Severity: high

Files:
- `thesis/chapters/08_implementation.tex`
- `thesis/chapters/01_introduction.tex`
- `thesis/chapters/00_abstract_en.tex`
- `thesis/chapters/00_abstract_gr.tex`

Details:

#### 5a. Source file counts and LOC are stale

- `thesis/chapters/08_implementation.tex:10` says `src/` contains `36` Python files
- March 21 audit count was `37`
- current 2026-05-02 repo count is `40` Python files under `src/`, excluding `__pycache__`

Current module LOC measured on 2026-05-02:
- `src/cube`: `1553`
- `src/thistlethwaite`: `2111`
- `src/kociemba`: `2310`
- `src/korf`: `4868`
- `src/evaluation`: `2169`
- `src/` total: `13042`

Thesis table currently says:
- `cube 1470`
- `thistlethwaite 1751`
- `kociemba 2112`
- `korf 3534`
- `evaluation 1965`

#### 5b. Test count is stale

- `thesis/chapters/08_implementation.tex:204` used to lag the current test count
- `thesis/chapters/00_abstract_en.tex:31` used to lag the current test count
- `thesis/chapters/00_abstract_gr.tex` also used to lag the current test count
- March 21 audit collection:
  - `python -m pytest tests --collect-only -q` -> `269 tests collected`
- current 2026-05-02 collection:
  - `python -m pytest tests --collect-only -q` -> `285 tests collected`

#### 5c. Code-size claim is stale

- `thesis/chapters/01_introduction.tex:69` says “approximately 8,000 lines of code”
- March 21 `src/` total measured during audit: `11,587` lines
- current 2026-05-02 `src/` total measured during documentation patch: `13,042` lines

Impact:
- these inaccuracies reduce credibility even where the core thesis argument is correct

Recommended later fix:
- update all counts from current repo state
- or remove precise counts and use softer wording if you do not want to maintain them

### 6. Kociemba Chapter Contains Stale or Internally Contradictory Claims

Severity: high

Files:
- `thesis/chapters/00_abstract_en.tex`
- `thesis/chapters/00_abstract_gr.tex`
- `thesis/chapters/04_kociemba.tex`
- `thesis/chapters/07_evaluation.tex`

Details:
- `thesis/chapters/00_abstract_en.tex:13` says Kociemba achieves solutions “under 19 moves”
- `thesis/chapters/04_kociemba.tex:8` says practical implementations achieve `< 20` moves
- `thesis/chapters/04_kociemba.tex:376-379` says:
  - typical solution quality `14-20`
  - reliability `98%` in benchmarks
- but the actual evaluation chapter reports:
  - `100%` success for Kociemba across the full benchmark
  - `21.96` average solution length at depth 20
  - see `thesis/chapters/07_evaluation.tex:131-134`

Impact:
- the Kociemba chapter is partly stale relative to the final benchmark corpus
- the thesis mixes literature-style general statements with repo-specific measured claims without clearly separating them

Recommended later fix:
- separate literature claims from measured results
- remove the `98%` benchmark claim
- soften “under 19” or qualify it explicitly as literature/typical external implementations, not your final measured corpus

### 7. Chapter 6 Contains a Risky Additive-PDB Claim

Severity: high

Files:
- `thesis/chapters/06_heuristics.tex`
- `thesis/chapters/05_korf.tex`

Details:
- `thesis/chapters/06_heuristics.tex:255-260` says that because PDBs are disjoint, the distances can be summed
- the same thesis defines the PDB heuristic in the Korf chapter as:
  - `h_PDB(s) = max(h_corner(s), h_edge1(s), h_edge2(s))`
  - `thesis/chapters/05_korf.tex:222-233`

Impact:
- as written, the heuristic theory chapter is too loose and can be challenged technically
- this is not just style; it is a theoretical correctness issue

Recommended later fix:
- either remove the additive Rubik-specific claim
- or rewrite it carefully with the exact admissibility conditions required

## Medium-Priority Findings

### 8. Composite Heuristic Is Oversold

Severity: medium

Files:
- `thesis/chapters/06_heuristics.tex`
- `thesis/chapters/09_conclusions.tex`

Details:
- Chapter 6 mostly frames the composite heuristic as exploratory and practical
- but:
  - `thesis/chapters/06_heuristics.tex:440-448` still calls it a key innovation
  - `thesis/chapters/09_conclusions.tex:81-99` calls it the most important research contribution

Impact:
- the thesis claims more research weight than is supported by dedicated experiments

Recommended later fix:
- downgrade the claim
- describe it as an exploratory heuristic design contribution unless you add strong experimental evidence

### 9. Figure 7 Caption Overclaims

Severity: medium

Files:
- `src/evaluation/visualizations.py`
- `thesis/chapters/07_evaluation.tex`

Details:
- `src/evaluation/visualizations.py:393-411` shows the plot is:
  - average solution length vs scramble depth
- but `thesis/chapters/07_evaluation.tex:251` captions it as overall algorithm performance and says Kociemba has the best total behavior

Impact:
- the figure supports a specific solution-length tradeoff, not general total performance

Recommended later fix:
- rename/caption the figure to reflect what it actually plots

### 10. Thesis Appendix Still Recommends Legacy Benchmark Scripts

Severity: medium

Files:
- `thesis/chapters/appendix_a.tex`

Details:
- `thesis/chapters/appendix_a.tex:87-89` recommends:
  - `generate_thesis_data.py`
  - `generate_complete_thesis_data.py`
  - `analyze_thesis_data.py`
- but the first two are not the canonical benchmark reproduction path

Impact:
- a reviewer can reproduce the wrong experiment from the appendix instructions

Recommended later fix:
- point appendix reproduction instructions to the canonical regeneration script only

### 11. Test/Reproducibility Story Is Still Confusing

Severity: medium

Files:
- `pytest.ini`
- `verify_setup.py`
- `tests/unit/test_algorithm_comparison.py`
- `tests/unit/test_a_star_solvers.py`
- `scripts/verification/test_optimal_interactive.py`

Details:

#### 11a. Bare `pytest` is not safe

- `pytest.ini` only contains async settings:
  - `pytest.ini:1-3`
- no `testpaths`
- no `pythonpath`
- bare `pytest -q` tries to collect extra verification scripts and hits import-path problems

#### 11b. `verify_setup.py` is not a real full-suite verification

- `verify_setup.py:275-285` runs only `tests/unit/test_rubik_cube.py`
- it then prints “All tests passed”

#### 11c. Optional-backend assumption in tests

- `tests/unit/test_algorithm_comparison.py:111` asserts `OPTIMAL_AVAILABLE is True`
- this can fail on a fresh machine without the optional solver backend installed

#### 11d. Flaky unit test

- `tests/unit/test_a_star_solvers.py:312-332` compares estimated A* vs IDA* memory
- `src/korf/a_star.py:441` hardcodes IDA* memory estimate to `0.1`
- I reproduced the target test 5 times and observed:
  - 4 passes
  - 1 failure

Observed failure:
- `AssertionError: assert 0.1 < (0.6 / 10)`

Impact:
- the repository does not currently support a clean, reviewer-friendly “run the tests” story

Recommended later fix:
- define a clear supported command, likely `python -m pytest tests -q`
- update `pytest.ini` so bare `pytest` behaves consistently
- fix or relax the flaky memory assertion
- decide whether optional-backend tests are required or should be skipped when unavailable

## Low-Priority Findings

### 12. Screenshot Evidence Is Missing

Severity: low

Files:
- `screenshots/README.md`

Details:
- `screenshots/README.md:11-38` and the rest of the file show that required screenshots are still “To be captured by user”
- no actual UI screenshot files are present

Impact:
- does not block thesis build
- does weaken appendix/demo/defense evidence if screenshots were intended to be part of the deliverable

Recommended later fix:
- capture the listed Streamlit and web UI screenshots

## Positive Findings Worth Preserving

These parts held up under audit:

- thesis benchmark data is coherent
- thesis figure assets are reproducible from the canonical JSON
- implementation diagrams exist
- thesis LaTeX build works
- Next.js webapp build works after dependency install
- integration tests pass cleanly

## Commands Used During Audit

Representative commands run:

```bash
python scripts/thesis_workflow.py status
python scripts/thesis_workflow.py validate
python scripts/thesis_workflow.py build --mode auto --clean
tectonic main.tex
python -m pytest tests --collect-only -q
python -m pytest tests/integration -q
python -m pytest tests/unit -q
python -m pytest tests/unit/test_algorithm_comparison.py -q
python -m pytest tests/test_facelet_cubie_conversion.py -q
npm ci
npm run build
python scripts/benchmarks/analyze_thesis_data.py
python scripts/benchmarks/generate_latex_tables.py
```

## Fix Order Recommendation

Suggested order for later remediation:

1. finish front matter
2. fix stale thesis numbers and Kociemba claims
3. fix Chapter 6 heuristic-theory wording
4. clarify the external Korf backend in the thesis
5. remove or quarantine legacy benchmark scripts from thesis-facing docs
6. clean up the test/reproducibility story
7. capture screenshots if needed

## Open Questions To Resolve Later

- Is the “distance from solved” component intended to be exact or heuristic in the final thesis framing?
- Is the final submission allowed to rely on the external Korf backend, or does the supervisor expect purely native implementation evidence?
- Do you want the repo to advertise only the canonical benchmark path and hide the legacy generators completely?
- Are screenshots required for the written thesis, or only for defense/demo materials?
