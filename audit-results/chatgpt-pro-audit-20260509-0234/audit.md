Audit source: extracted ZIP only (`/mnt/data/repo-audit-20260509-0127.zip`). No external repository was used.

I verified real files and ran key setup commands where feasible. The strongest blockers are: Python verification is not actually fast from a clean ZIP, the webapp dependency lock cannot install cleanly, and a major native-corner-PDB validation claim is not reproducible from the ZIP as shipped.

## 1. Critical blockers

### C1 — Default Python verification is not reproducible/fast

* **Severity:** Critical
* **File:** `tests/unit/test_kociemba.py`; `src/kociemba/pruning.py`; `pytest.ini`; `README.md`; `verify_setup.py`
* **Location:** `tests/unit/test_kociemba.py:224-255`, `src/kociemba/pruning.py:64-115`, `src/kociemba/pruning.py:136-199`, `pytest.ini:1-7`, `README.md:102-104`, `verify_setup.py:345-358`
* **Problem:** The repository claims the default profile excludes heavyweight cache-building tests, but `TestPruningTables` is unmarked and calls `tables.load(max_depth=8)`, which can generate large pruning tables. In my clean extracted run, `python verify_setup.py` did not complete within the verifier timeout path, and `pytest -vv -m "not slow and not external and not cache_building"` reached `tests/unit/test_kociemba.py::TestPruningTables::test_pruning_tables_loading` and stalled on pruning table generation.
* **Why it matters:** The stated reproducibility path is a core thesis claim. A supervisor/reviewer cannot accept “fast verification passed” if the uploaded source does not reproduce it.
* **Exact fix:** Mark `TestPruningTables` and related full pruning-table generation tests with `@pytest.mark.cache_building`, or replace them with tiny mocked/fixture-backed pruning tables. Keep only cheap API-shape tests in the default suite.
* **Verification steps:** Freshly extract the ZIP, remove generated caches, then run `python -m pytest tests -q` and `python verify_setup.py`. Both must finish within `FAST_TEST_TIMEOUT_SECONDS=300` without generating large Kociemba pruning caches.

### C2 — Webapp clean install/build fails despite README claim

* **Severity:** Critical
* **File:** `webapp/package.json`; `webapp/package-lock.json`; `README.md`
* **Location:** `webapp/package.json:16-19`, `webapp/package-lock.json:15-18`, `webapp/package-lock.json:5011-5018`, `README.md:105`
* **Problem:** `README.md:105` claims `cd webapp && npm ci && npm run build` succeeds from a clean install. The checked dependency graph has `react@^19.2.4` and `lucide-react@0.294.0`; the lockfile states `lucide-react` peers require React `^16.5.1 || ^17.0.0 || ^18.0.0`. `npm ci` fails with a peer dependency conflict.
* **Why it matters:** The demonstration frontend is not reproducible from the ZIP. This directly contradicts the setup documentation.
* **Exact fix:** Either upgrade `lucide-react` to a React-19-compatible release and regenerate `package-lock.json`, or downgrade `react`, `react-dom`, and any React-19-dependent packages to a consistent React 18 stack.
* **Verification steps:** Run `cd webapp && rm -rf node_modules && npm ci && npm run build`.

### C3 — Native corner-PDB validation claim is not reproducible from the ZIP

* **Severity:** Critical
* **File:** `results/validation/native_exact/MANIFEST.json`; `results/validation/native_exact/native_exact_validation_20260322_144046.json`; `scripts/verification/native_exact_validation.py`; `src/korf/native_coordinate_heuristic.py`; `data/README.md`
* **Location:** `MANIFEST.json:5-12`, `MANIFEST.json:62-65`, `native_exact_validation_20260322_144046.json:6-8`, `scripts/verification/native_exact_validation.py:209-213`, `scripts/verification/native_exact_validation.py:286-295`, `src/korf/native_coordinate_heuristic.py:86-87`, `src/korf/native_coordinate_heuristic.py:199-210`, `data/README.md:13-18`, `data/README.md:36-47`
* **Problem:** The manifest claims the canonical run used the “full native corner pattern database enabled,” and the thesis relies on the improvement from 3 failures to 1. The ZIP does not contain `data/pattern_databases/corner_db.pkl`, `edge1_db.pkl`, or `edge2_db.pkl`. The heuristic loader silently returns `None` if the corner DB is missing, and the validation report records only `disable_corner_db=false`, not whether the full DB was actually loaded.
* **Why it matters:** A central validation claim cannot be independently regenerated from the uploaded source artifact. Worse, a clean rerun can silently degrade while still appearing “enabled” in config.
* **Exact fix:** Either include the required complete PDB artifact, or make the canonical validation preset fail hard when `corner_db.pkl` is missing. Add `corner_db_loaded: true/false` and `corner_db_complete: true/false` to every validation report.
* **Verification steps:** In a clean extraction, run `test -f data/pattern_databases/corner_db.pkl`; then run `python scripts/verification/native_exact_validation.py --preset canonical --output-dir <tmp>` and assert the new report contains `corner_db_loaded: true`.

### C4 — Approval page is not submission-ready

* **Severity:** Critical
* **File:** `thesis/chapters/00_approval.tex`
* **Location:** `thesis/chapters/00_approval.tex:35-44`
* **Problem:** Two committee members remain as generic placeholders, and the examination date is `\dotfill`.
* **Why it matters:** This is a formal thesis submission blocker.
* **Exact fix:** Replace placeholder committee entries with actual names/titles and set the actual examination/submission date, or remove the approval page if the institution requires it to remain blank until signing.
* **Verification steps:** Rebuild `thesis/main.pdf` and visually inspect the approval page.

## 2. Thesis writing issues

### W1 — Greek thesis text contains an English verb in a Greek sentence

* **Severity:** Minor
* **File:** `thesis/chapters/08_implementation.tex`
* **Location:** `thesis/chapters/08_implementation.tex:125`
* **Problem:** The sentence says “Η κύρια κλάση orchestrates τις τέσσερις φάσεις.”
* **Why it matters:** This is visibly unpolished and weakens academic tone.
* **Exact fix:** Replace with “Η κύρια κλάση ενορχηστρώνει τις τέσσερις φάσεις” or “συντονίζει τις τέσσερις φάσεις.”
* **Verification steps:** Search for `orchestrates` and rebuild the PDF.

### W2 — Abstract overstates the IDA* vs A* conclusion

* **Severity:** Major
* **File:** `thesis/chapters/00_abstract_en.tex`; `thesis/chapters/00_abstract_gr.tex`
* **Location:** `00_abstract_en.tex:32`, `00_abstract_gr.tex:34`
* **Problem:** The abstracts claim IDA* outperforms A* for cube solving due to lower memory requirements. The repository supports a much narrower claim: the implemented IDA* path has lower memory behavior than the included A* demo/baseline under the repository’s tested conditions.
* **Why it matters:** A broad algorithmic claim needs broader evidence than this repository provides.
* **Exact fix:** Reword to: “In the implemented benchmark/baseline comparison, IDA* exhibits substantially lower memory usage than the included A* implementation, at the cost of repeated node expansions.”
* **Verification steps:** Check the abstract text and ensure it matches the actual experiments and `src/korf/heuristics.py:4-7`.

### W3 — Test-suite claims are repeated in thesis text but contradicted by actual default tests

* **Severity:** Major
* **File:** `thesis/chapters/00_abstract_en.tex`; `thesis/chapters/00_abstract_gr.tex`; `thesis/chapters/01_introduction.tex`; `thesis/chapters/08_implementation.tex`; `thesis/chapters/appendix_a.tex`
* **Location:** `00_abstract_en.tex:35`, `00_abstract_gr.tex:37`, `01_introduction.tex:80`, `08_implementation.tex:221-227`, `appendix_a.tex:135-136`
* **Problem:** The text says heavyweight cache-building tests are excluded from the default fast profile, but `tests/unit/test_kociemba.py:224-255` still performs heavyweight pruning-table loading in the default profile.
* **Why it matters:** The thesis makes a reproducibility claim that reviewers can disprove by running the ZIP.
* **Exact fix:** First fix the test markers; then update these thesis claims only after the clean default run passes.
* **Verification steps:** Run `python -m pytest tests -q`; then rebuild the thesis and confirm the statements remain true.

### W4 — Evaluation limitation language is too strong

* **Severity:** Major
* **File:** `thesis/chapters/07_evaluation.tex`
* **Location:** `thesis/chapters/07_evaluation.tex:320-328`, especially `07_evaluation.tex:322`
* **Problem:** The text says 100 scrambles are enough for “clear conclusions.” Given the legacy redundant scramble corpus, no confidence intervals, and single-machine execution, this should be softened.
* **Why it matters:** The current phrasing overclaims statistical strength.
* **Exact fix:** Replace with “100 scrambles support indicative conclusions for this fixed corpus, not statistically general conclusions.” Add confidence intervals or bootstrap intervals if keeping stronger wording.
* **Verification steps:** Rebuild the PDF and confirm the limitation section no longer overstates the evidence.

## 3. Technical/code issues

### T1 — A*/IDA* code claims admissible/optimal use while heuristic module says the heuristics are not guaranteed lower bounds

* **Severity:** Major
* **File:** `src/korf/a_star.py`; `src/korf/heuristics.py`; `tests/unit/test_a_star_solvers.py`
* **Location:** `src/korf/a_star.py:4-10`, `src/korf/a_star.py:51-61`, `src/korf/a_star.py:271-276`, `src/korf/heuristics.py:4-7`, `tests/unit/test_a_star_solvers.py:73-107`, `tests/unit/test_a_star_solvers.py:195-220`
* **Problem:** `a_star.py` describes optimal solving with admissible heuristics, but the tested heuristics such as `manhattan_distance` come from a module that explicitly says the simple estimates are not guaranteed lower bounds.
* **Why it matters:** A* and IDA* optimality guarantees depend on admissibility. This is a mathematical correctness/documentation mismatch.
* **Exact fix:** Change `a_star.py` wording to “configurable heuristics; optimal only when the supplied heuristic is admissible.” Add a heuristic metadata flag or type wrapper indicating admissibility.
* **Verification steps:** Add tests that assert non-admissible heuristics are not advertised as optimal, and that optimality claims are restricted to proven admissible/PDB-backed heuristics.

### T2 — `PruningTables.load()` ignores requested depth after the instance is already loaded

* **Severity:** Major
* **File:** `src/kociemba/pruning.py`
* **Location:** `src/kociemba/pruning.py:64-73`, `src/kociemba/pruning.py:90-111`, `src/kociemba/pruning.py:337-354`
* **Problem:** If a `PruningTables` instance is already loaded, `load(max_depth=...)` returns immediately without checking whether the requested `max_depth` matches the loaded depth. The cache-file path checks depth, but the in-memory early return does not.
* **Why it matters:** A process can accidentally reuse shallower pruning tables for a deeper request. This undermines correctness and reproducibility of solver behavior.
* **Exact fix:** Replace the early return with a depth check: if already loaded and `self.max_depth != max_depth`, either raise `ValueError` or reload/regenerate.
* **Verification steps:** Add a unit test that loads a small-depth table fixture and then calls `load()` with a different `max_depth`, expecting a clear error or reload.

### T3 — Memory measurements are process-level RSS deltas from shared sequential solver runs

* **Severity:** Major
* **File:** `src/evaluation/algorithm_comparison.py`; `thesis/chapters/07_evaluation.tex`
* **Location:** `algorithm_comparison.py:315-356`, `algorithm_comparison.py:381-429`, `algorithm_comparison.py:454-513`, `algorithm_comparison.py:242-244`, `07_evaluation.tex:70-72`, `07_evaluation.tex:327`
* **Problem:** The benchmark records `mem_after - mem_before` from the same Python process while solver instances are reused. This produces noisy and order-dependent values, especially after caches are loaded.
* **Why it matters:** Memory comparisons in tables/figures can be misleading.
* **Exact fix:** Run each solver/scramble in an isolated subprocess and record peak RSS, or explicitly label the metric as process RSS delta and remove strong memory-comparison claims.
* **Verification steps:** Implement subprocess-based peak memory measurement and compare it against the current RSS-delta results.

### T4 — No frontend/UI tests or `npm test` script

* **Severity:** Minor
* **File:** `webapp/package.json`
* **Location:** `webapp/package.json:5-9`; absence of test files under `webapp/`
* **Problem:** The webapp has scripts for dev/build/start/lint but no test script, and no frontend test files were present.
* **Why it matters:** The thesis claims interactive web applications, but the frontend behavior has no automated regression coverage.
* **Exact fix:** Add at least smoke tests with Vitest/React Testing Library or Playwright, and add `"test": "..."` to `webapp/package.json`.
* **Verification steps:** Run `cd webapp && npm test` in CI or local verification.

## 4. Research/experimental issues

### R1 — Canonical benchmark corpus contains many redundant/cancelling adjacent same-face moves

* **Severity:** Major
* **File:** `results/benchmarks/thesis/thesis_results_combined.json`; `thesis/chapters/07_evaluation.tex`
* **Location:** JSON metadata `thesis_results_combined.json:117-119`; example depth 5 `thesis_results_combined.json:123-131`; example depth 10 `thesis_results_combined.json:2306-2319`; example depth 15 `thesis_results_combined.json:5348-5365`; example depth 20 `thesis_results_combined.json:8720-8743`; thesis discussion `07_evaluation.tex:75-77`
* **Problem:** The benchmark metadata admits the corpus is `legacy_random_all_moves_redundant_allowed`. I counted adjacent same-face redundancy in 11/25 depth-5, 20/25 depth-10, 23/25 depth-15, and 24/25 depth-20 scrambles.
* **Why it matters:** Requested scramble length is not a reliable difficulty proxy. The benchmark is easier than the nominal depths suggest.
* **Exact fix:** Add a second canonical benchmark generated with `allow_redundant=False` and/or group results by verified optimal distance rather than requested scramble length.
* **Verification steps:** Run a script over `scramble_moves` that flags adjacent moves with the same first face letter and compare old vs new corpus distributions.

### R2 — Timing methodology mixes lazy-loading/preprocessing with solve timing

* **Severity:** Major
* **File:** `results/benchmarks/thesis/thesis_results_combined.json`; `thesis/chapters/07_evaluation.tex`
* **Location:** `thesis_results_combined.json:24-26`, `07_evaluation.tex:318-328`, especially `07_evaluation.tex:324`
* **Problem:** Metadata says solver instances are reused and heavy tables lazy-load inside the first timed solve call. The thesis acknowledges this, but the timing table still presents simple means by depth.
* **Why it matters:** First-solve initialization can distort per-depth comparisons.
* **Exact fix:** Report cold-start and warm-start timings separately, or perform a documented warmup before benchmark timing.
* **Verification steps:** Rerun benchmarks with one warmup solve per solver/backend and compare against the checked-in timing artifacts.

### R3 — Reported means lack uncertainty and successful-only filtering is not always explicit in table captions

* **Severity:** Minor
* **File:** `thesis/chapters/07_evaluation.tex`; `src/evaluation/algorithm_comparison.py`
* **Location:** `07_evaluation.tex:213-226`, `algorithm_comparison.py:645-654`, `algorithm_comparison.py:670-674`
* **Problem:** Tables report means without confidence intervals, medians, IQR, or standard deviations. The code computes summaries from successful solves only; for Korf depth 20 this excludes three 120-second failures from averages, while the table caption does not state “successful solves only.”
* **Why it matters:** Means over successful solves can understate practical runtime when failures/timeouts are part of the algorithm behavior.
* **Exact fix:** Add median/IQR/std or bootstrap confidence intervals, and explicitly label means as “successful solves only” where applicable. Also report timeout count beside timing means.
* **Verification steps:** Recompute stats from `thesis_results_combined.json` and update tables/captions.

## 5. Citation/reference issues

### CR1 — Bibliography source contains many unused entries and a duplicate DeepCubeA-style entry

* **Severity:** Minor
* **File:** `thesis/references.bib`
* **Location:** `references.bib:95-100`, `references.bib:134-141`, `references.bib:199-211`, `references.bib:217-225`, `references.bib:242-260`
* **Problem:** There are many unused BibTeX entries. `mcaleer2018solving` and `agostinelli2019deepcubea` describe the same Nature Machine Intelligence paper, but only `agostinelli2019deepcubea` is cited.
* **Why it matters:** The final bibliography generated by BibTeX may be clean, but source-level bibliography noise makes maintenance and review harder.
* **Exact fix:** Remove unused entries or move them to a separate literature notes file. Keep one canonical entry for the DeepCubeA paper.
* **Verification steps:** Run a citation audit script: collect `\cite{...}` keys from `thesis/chapters/*.tex`, compare against `references.bib`, and ensure no duplicate/unused thesis-bibliography entries remain unless intentionally kept.

## 6. Reproducibility/setup issues

### RS1 — Root README omits clean Python environment setup and does not reference `requirements.lock`

* **Severity:** Major
* **File:** `README.md`; `requirements.txt`; `requirements.lock`
* **Location:** `README.md:22-31`, `requirements.txt:1-42`, `requirements.lock:1-138`
* **Problem:** “Where To Start” gives verification commands but not virtualenv creation, dependency installation, or whether to use `requirements.txt` or `requirements.lock`.
* **Why it matters:** A clean reviewer cannot reliably reproduce the environment from the documented first steps.
* **Exact fix:** Add explicit commands: create venv, install from `requirements.lock` for exact reproduction or `requirements.txt` for flexible setup, then run verification. Also state the tested Python version.
* **Verification steps:** From a new environment, run only the README commands and confirm all commands pass.

### RS2 — Appendix reproducibility snapshot includes a commit hash that cannot be verified from the ZIP

* **Severity:** Major
* **File:** `thesis/chapters/appendix_a.tex`
* **Location:** `appendix_a.tex:117-142`, especially `appendix_a.tex:130-132`
* **Problem:** The appendix lists repository, branch, and commit hash `7c5a421`, but the uploaded ZIP has no `.git` directory, so the commit cannot be verified from the source of truth.
* **Why it matters:** The audit source is the ZIP, not GitHub. A reproducibility snapshot should be verifiable from the submitted artifact.
* **Exact fix:** Add an archive manifest with ZIP hash, file hash list, and generation date, or include a verified `REVISION`/`MANIFEST` file generated at packaging time.
* **Verification steps:** Run `test -d .git`; if false, verify the thesis snapshot from the added manifest instead.

### RS3 — Checked-in workflow validation artifact is environment-specific/stale

* **Severity:** Minor
* **File:** `agent_workflow/generated/validation.md`; `scripts/thesis_workflow.py`
* **Location:** `agent_workflow/generated/validation.md:3-16`, `scripts/thesis_workflow.py:873-910`
* **Problem:** The checked-in validation artifact reports one toolchain state, but the validation script recomputes environment-specific checks. The artifact has no timestamp or host/toolchain identity.
* **Why it matters:** Reviewers may confuse stale generated workflow output with current validation.
* **Exact fix:** Either stop tracking generated validation output or add timestamp, host/toolchain metadata, and a clear “generated, not source of truth” banner.
* **Verification steps:** Run `python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md` and confirm the output includes metadata and matches the current environment.

## 7. Submission polish issues

### SP1 — Final thesis progress checklist still has unchecked final-review items

* **Severity:** Minor
* **File:** `thesis/README.md`
* **Location:** `thesis/README.md:105-114`
* **Problem:** The progress tracker leaves final build-machine validation, front matter review, proofreading/formatting, and final PDF inspection unchecked.
* **Why it matters:** This confirms the thesis package itself says it has not passed final submission QA.
* **Exact fix:** Complete these checks and mark them done, or remove the checklist from the submission archive if it is only internal.
* **Verification steps:** Re-run validation/build, inspect PDF, then update the checklist.

### SP2 — LaTeX source suppresses warning/badness signals

* **Severity:** Minor
* **File:** `thesis/main.tex`; `thesis/main.log`
* **Location:** `main.tex:85-87`, `main.tex:95-97`, `main.log:911-933`
* **Problem:** The thesis uses `silence` filters and `\hbadness=10000`, which can hide formatting issues. The log still contains float-placement warnings.
* **Why it matters:** Final PDF polish should be judged with warnings visible, not suppressed.
* **Exact fix:** Remove warning filters and high badness suppression for the final QA build, then fix actual overfull/float/font warnings.
* **Verification steps:** Rebuild with warnings unsuppressed and confirm the log has no unresolved formatting warnings.

---

## FIX_TARGETS

```json
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "tests/unit/test_kociemba.py; src/kociemba/pruning.py; pytest.ini; README.md; verify_setup.py",
    "location": "tests/unit/test_kociemba.py:224-255; src/kociemba/pruning.py:64-115,136-199; pytest.ini:1-7; README.md:102-104; verify_setup.py:345-358",
    "issue": "The default fast test/verification profile still runs unmarked Kociemba pruning-table loading tests that can generate large pruning tables, contradicting the README and thesis reproducibility claims.",
    "exact_fix": "Mark the pruning-table generation tests with @pytest.mark.cache_building or replace them with tiny mocked/fixture-backed tests. Keep only cheap API tests in the default profile, then update README/thesis claims after the clean run passes.",
    "verification_steps": "Freshly extract the ZIP, remove generated caches, run `python -m pytest tests -q` and `python verify_setup.py`, and confirm both finish within FAST_TEST_TIMEOUT_SECONDS=300 without generating large pruning caches."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "webapp/package.json; webapp/package-lock.json; README.md",
    "location": "webapp/package.json:16-19; webapp/package-lock.json:15-18,5011-5018; README.md:105",
    "issue": "The README claims `npm ci && npm run build` succeeds, but the lockfile contains lucide-react@0.294.0 with a React <=18 peer requirement while the project uses React 19.2.4.",
    "exact_fix": "Upgrade lucide-react to a React-19-compatible release and regenerate package-lock.json, or downgrade React/ReactDOM and dependent packages to a consistent React 18 stack.",
    "verification_steps": "Run `cd webapp && rm -rf node_modules && npm ci && npm run build` from a clean extraction."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "results/validation/native_exact/MANIFEST.json; results/validation/native_exact/native_exact_validation_20260322_144046.json; scripts/verification/native_exact_validation.py; src/korf/native_coordinate_heuristic.py; data/README.md",
    "location": "MANIFEST.json:5-12,62-65; native_exact_validation_20260322_144046.json:6-8; scripts/verification/native_exact_validation.py:209-213,286-295; src/korf/native_coordinate_heuristic.py:86-87,199-210; data/README.md:13-18,36-47",
    "issue": "The canonical validation claims full native corner PDB enabled, but the ZIP does not include data/pattern_databases/corner_db.pkl and the loader silently falls back to no corner DB while reports record only disable_corner_db=false.",
    "exact_fix": "Include the required complete corner_db.pkl artifact or make the canonical preset fail if the file is missing. Add explicit corner_db_loaded and corner_db_complete fields to validation reports.",
    "verification_steps": "In a clean extraction, check `test -f data/pattern_databases/corner_db.pkl`; run `python scripts/verification/native_exact_validation.py --preset canonical --output-dir <tmp>` and assert the report contains `corner_db_loaded: true`."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "thesis/chapters/00_approval.tex",
    "location": "thesis/chapters/00_approval.tex:35-44",
    "issue": "The approval page still has two generic committee placeholders and a blank examination date.",
    "exact_fix": "Replace placeholders with actual committee member names/titles and set the examination/submission date, or remove the page if the institution requires a blank signing form.",
    "verification_steps": "Rebuild thesis/main.pdf and visually inspect the approval page."
  },
  {
    "severity": "Minor",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/08_implementation.tex",
    "location": "thesis/chapters/08_implementation.tex:125",
    "issue": "Greek academic prose contains the English verb `orchestrates` inside a Greek sentence.",
    "exact_fix": "Replace with Greek wording such as `Η κύρια κλάση ενορχηστρώνει τις τέσσερις φάσεις` or `συντονίζει τις τέσσερις φάσεις`.",
    "verification_steps": "Search for `orchestrates`, confirm it is gone, and rebuild the PDF."
  },
  {
    "severity": "Major",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex",
    "location": "00_abstract_en.tex:32; 00_abstract_gr.tex:34",
    "issue": "The abstracts overstate that IDA* outperforms A* for cube solving, while the repository only supports a narrower implementation-specific memory comparison.",
    "exact_fix": "Reword to state that in the implemented benchmark/baseline comparison IDA* exhibits lower memory usage than the included A* implementation, at the cost of repeated expansions.",
    "verification_steps": "Confirm the abstract wording matches actual evidence and does not imply a universal algorithmic proof."
  },
  {
    "severity": "Major",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex; thesis/chapters/01_introduction.tex; thesis/chapters/08_implementation.tex; thesis/chapters/appendix_a.tex",
    "location": "00_abstract_en.tex:35; 00_abstract_gr.tex:37; 01_introduction.tex:80; 08_implementation.tex:221-227; appendix_a.tex:135-136",
    "issue": "The thesis repeats that heavyweight cache-building tests are excluded from the default profile, but actual unmarked Kociemba pruning-table tests run in the default profile.",
    "exact_fix": "Fix the pytest markers first, then update all thesis claims to match the verified default command output.",
    "verification_steps": "Run `python -m pytest tests -q`; only after it passes quickly, rebuild the thesis and verify these statements."
  },
  {
    "severity": "Major",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "thesis/chapters/07_evaluation.tex:320-328, especially line 322",
    "issue": "The evaluation says 100 scrambles are enough for clear conclusions, which is too strong for a redundant legacy corpus with no uncertainty analysis.",
    "exact_fix": "Change the wording to `indicative conclusions for this fixed corpus` and add confidence intervals or bootstrap analysis if stronger conclusions are desired.",
    "verification_steps": "Rebuild the PDF and inspect the limitations section."
  },
  {
    "severity": "Major",
    "category": "Technical/code issues",
    "file": "src/korf/a_star.py; src/korf/heuristics.py; tests/unit/test_a_star_solvers.py",
    "location": "src/korf/a_star.py:4-10,51-61,271-276; src/korf/heuristics.py:4-7; tests/unit/test_a_star_solvers.py:73-107,195-220",
    "issue": "A*/IDA* documentation says admissible/optimal, but tested heuristics such as manhattan_distance come from a module explicitly saying these estimates are not guaranteed lower bounds.",
    "exact_fix": "Document that optimality holds only with proven admissible heuristics. Add heuristic metadata or a wrapper indicating admissibility and restrict optimality claims to PDB/native-exact heuristics.",
    "verification_steps": "Add tests ensuring non-admissible heuristics are not advertised as optimal and that optimality claims are only made for admissible heuristics."
  },
  {
    "severity": "Major",
    "category": "Technical/code issues",
    "file": "src/kociemba/pruning.py",
    "location": "src/kociemba/pruning.py:64-73,90-111,337-354",
    "issue": "PruningTables.load returns immediately when already loaded and does not check whether the requested max_depth matches the loaded max_depth.",
    "exact_fix": "Modify the early return to check self.max_depth against requested max_depth and either raise ValueError or reload/regenerate when they differ.",
    "verification_steps": "Add a unit test that loads with one max_depth and then calls load with a different max_depth, expecting a clear error or reload."
  },
  {
    "severity": "Major",
    "category": "Technical/code issues",
    "file": "src/evaluation/algorithm_comparison.py; thesis/chapters/07_evaluation.tex",
    "location": "algorithm_comparison.py:315-356,381-429,454-513,242-244; 07_evaluation.tex:70-72,327",
    "issue": "Memory is measured as process RSS delta in a shared sequential process with reused solver instances, making the memory results noisy and order-dependent.",
    "exact_fix": "Use isolated subprocesses and peak RSS per solver/scramble, or downgrade memory claims to clearly labeled process-level RSS deltas.",
    "verification_steps": "Implement subprocess peak-memory measurement and compare the new results with current RSS-delta artifacts."
  },
  {
    "severity": "Minor",
    "category": "Technical/code issues",
    "file": "webapp/package.json",
    "location": "webapp/package.json:5-9; no test/spec files found under webapp/",
    "issue": "The frontend has no automated test script or test files.",
    "exact_fix": "Add Vitest/React Testing Library or Playwright smoke tests and add an npm `test` script.",
    "verification_steps": "Run `cd webapp && npm test` successfully in a clean environment."
  },
  {
    "severity": "Major",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "thesis_results_combined.json:117-119,123-131,2306-2319,5348-5365,8720-8743; 07_evaluation.tex:75-77",
    "issue": "The canonical benchmark corpus is legacy redundant and contains adjacent same-face cancellations/redundancy in many scrambles, weakening requested-depth comparisons.",
    "exact_fix": "Add a second canonical corpus with allow_redundant=False and/or analyze results by verified optimal depth rather than requested scramble length.",
    "verification_steps": "Run a script over scramble_moves to count adjacent same-face pairs and compare distributions before and after regenerating the corpus."
  },
  {
    "severity": "Major",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "thesis_results_combined.json:24-26; 07_evaluation.tex:318-328, especially line 324",
    "issue": "Timing methodology includes lazy-loading/preprocessing in first timed solves while reusing solver instances, so cold-start and warm-start effects are mixed.",
    "exact_fix": "Report cold-start and warm-start timings separately or perform a documented warmup before timed benchmark runs.",
    "verification_steps": "Rerun benchmarks with explicit warmup and compare timing tables to the checked-in artifacts."
  },
  {
    "severity": "Minor",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; src/evaluation/algorithm_comparison.py",
    "location": "07_evaluation.tex:213-226; algorithm_comparison.py:645-654,670-674",
    "issue": "Timing and solution-length tables report means without uncertainty, and successful-only filtering for Korf timing is not explicit in the timing table caption.",
    "exact_fix": "Add median/IQR/std or bootstrap confidence intervals and label Korf means as successful-solve-only where applicable.",
    "verification_steps": "Recompute statistics from thesis_results_combined.json and update table captions and values."
  },
  {
    "severity": "Minor",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "references.bib:95-100,134-141,199-211,217-225,242-260",
    "issue": "The bibliography source contains many unused entries and duplicate coverage of the DeepCubeA/Nature Machine Intelligence paper.",
    "exact_fix": "Remove unused entries from the thesis bibliography or move them to separate literature notes; keep one canonical DeepCubeA entry.",
    "verification_steps": "Run a citation-key audit comparing citations in thesis/chapters/*.tex with entries in references.bib."
  },
  {
    "severity": "Major",
    "category": "Reproducibility/setup issues",
    "file": "README.md; requirements.txt; requirements.lock",
    "location": "README.md:22-31; requirements.txt:1-42; requirements.lock:1-138",
    "issue": "The start commands omit virtualenv/dependency installation and do not state whether requirements.txt or requirements.lock should be used.",
    "exact_fix": "Add clean setup instructions with Python version, venv creation, and either exact `pip install -r requirements.lock` or flexible `pip install -r requirements.txt` guidance.",
    "verification_steps": "Create a fresh environment and follow only the README instructions until verification succeeds."
  },
  {
    "severity": "Major",
    "category": "Reproducibility/setup issues",
    "file": "thesis/chapters/appendix_a.tex",
    "location": "appendix_a.tex:117-142, especially 130-132",
    "issue": "The reproducibility snapshot lists repository, branch, and commit hash, but the ZIP has no .git directory, so the commit cannot be verified from the submitted artifact.",
    "exact_fix": "Add a ZIP/archive manifest with archive hash, file hashes, packaging date, and revision information verifiable without .git.",
    "verification_steps": "Run `test -d .git`; if false, verify the thesis snapshot from the added manifest."
  },
  {
    "severity": "Minor",
    "category": "Reproducibility/setup issues",
    "file": "agent_workflow/generated/validation.md; scripts/thesis_workflow.py",
    "location": "agent_workflow/generated/validation.md:3-16; scripts/thesis_workflow.py:873-910",
    "issue": "The checked-in workflow validation output is environment-specific and lacks timestamp/host/toolchain metadata.",
    "exact_fix": "Stop tracking generated validation output or add a timestamp, host/toolchain identity, and a clear generated-artifact banner.",
    "verification_steps": "Run `python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md` and confirm the regenerated file includes metadata."
  },
  {
    "severity": "Minor",
    "category": "Submission polish issues",
    "file": "thesis/README.md",
    "location": "thesis/README.md:105-114",
    "issue": "The thesis progress tracker still has final validation, front matter review, proofreading, formatting, and PDF inspection unchecked.",
    "exact_fix": "Complete these checks and mark them done, or remove the internal checklist from the final submission archive.",
    "verification_steps": "Re-run validation/build, inspect the PDF, and update the checklist."
  },
  {
    "severity": "Minor",
    "category": "Submission polish issues",
    "file": "thesis/main.tex; thesis/main.log",
    "location": "main.tex:85-87,95-97; main.log:911-933",
    "issue": "LaTeX warning filters and high hbadness suppress formatting diagnostics; the log still contains float-placement warnings.",
    "exact_fix": "Remove warning suppression for final QA builds and fix any resulting overfull, font, or float warnings.",
    "verification_steps": "Rebuild the thesis with warnings unsuppressed and confirm the log has no unresolved formatting warnings."
  }
]
```

## Scores

* **Overall thesis quality score:** 68/100
* **Technical quality score:** 52/100
* **Submission readiness score:** 38/100
