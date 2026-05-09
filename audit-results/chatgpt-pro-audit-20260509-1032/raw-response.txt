I audited the extracted ZIP as the only source of truth. The repository is substantially improved in transparency compared with a typical thesis/code artifact, but it is **not submission-ready** because final front matter is still missing, the thesis build path is not robust under the documented toolchain checks, cold-cache testing is not reliably fast, and some experimental claims still need tighter wording and reproduction support.

## 1. Critical blockers

### 1. Formal institutional front matter is incomplete and excluded from the thesis build

**Severity:** Critical
**Files / locations:** `thesis/main.tex:173-180`; `thesis/chapters/00_approval.tex:34-44`; `thesis/README.md:3`; `README.md:7-8`
**Problem:** The approval/signature page is explicitly excluded from `main.tex`, and `00_approval.tex` still contains placeholder committee members and a placeholder examination date.
**Why it matters:** This blocks final institutional submission. The repository itself admits the front matter is pending.
**Exact fix:** Fill official committee names and examination date in `00_approval.tex`, then include `\input{chapters/00_approval}` in `thesis/main.tex` immediately after the title page or wherever the institution requires it.
**Verification steps:** `grep -n "00_approval" thesis/main.tex`; confirm no `Μέλος Εξεταστικής Επιτροπής` placeholders or `\dotfill` date remain; rebuild and inspect the first pages of `thesis/main.pdf`.

### 2. Thesis build workflow has a local-mode prerequisite bug

**Severity:** Critical
**Files / locations:** `scripts/thesis_workflow.py:483-495`; `scripts/thesis_workflow.py:1035-1069`; `thesis/README.md:37-43`; `thesis/README.md:88-100`
**Problem:** `toolchain_status()` correctly requires a bibliography tool for local TeX readiness, but `build_thesis(mode="local")` still runs `latexmk -xelatex` whenever `latexmk` and `xelatex` exist, even if `bibtex` is absent. In the audit environment, `build --mode auto` reported no usable build path, while `build --mode local --clean` proceeded and failed at `bibtex`.
**Why it matters:** The documented build workflow is not prerequisite-safe. A reviewer can hit a raw LaTeX failure instead of a clear build-path error.
**Exact fix:** In the local branch, require `tools["bibliography_tool"]` before invoking `latexmk`, or call `latexmk` only through a checked path that guarantees the bibliography backend exists. Otherwise fall back to Tectonic/Docker or raise the same clear error used by `auto`.
**Verification steps:** Temporarily remove `bibtex` from `PATH` while leaving `latexmk` and `xelatex` available; run `python scripts/thesis_workflow.py build --mode local --clean`; expected result is a clear prerequisite failure, not `sh: 1: bibtex: not found`.

### 3. Default fast test profile can exceed setup time on a cold cache

**Severity:** Critical
**Files / locations:** `pytest.ini:1-7`; `verify_setup.py:24-29`; `verify_setup.py:349-398`; `tests/unit/test_kociemba.py:289-391`; `src/kociemba/solver.py:120-137`; `src/kociemba/pruning.py:119-123`
**Problem:** The default pytest marker excludes `cache_building`, but unmarked Kociemba solver tests still call `solve_cube()` and can trigger first-run move/pruning table generation. `verify_setup.py` gives the fast profile only 120 seconds.
**Why it matters:** Fresh reviewers and CI can fail or hang on the documented “fast” setup path. This is a reproducibility blocker.
**Exact fix:** Mark the full Kociemba solve tests at `tests/unit/test_kociemba.py:330-391` as `cache_building` or `slow`, or rewrite them to use prebuilt lightweight fixtures/mocks. Keep cold-cache generation in an explicit opt-in test.
**Verification steps:** Delete `data/kociemba/`; run `python -m pytest tests -q` and `python verify_setup.py`; both should complete within the documented fast timeout without generating large solver caches.

### 4. Canonical native exact validation cannot be reproduced from the ZIP alone

**Severity:** Critical
**Files / locations:** `data/README.md:36-48`; `data/README.md:56-65`; `results/validation/native_exact/README.md:5-38`; `results/validation/native_exact/MANIFEST.json:4-12`; `scripts/verification/native_exact_validation.py:247-255`
**Problem:** The canonical native exact validation requires `data/pattern_databases/corner_db.pkl`, but the ZIP intentionally omits that large cache. The source-ZIP preset is only a smoke validation and is explicitly not the canonical evidence.
**Why it matters:** The ZIP cannot independently regenerate one of the thesis validation claims without an external/generated artifact.
**Exact fix:** Either ship the required cache as a separate checked artifact with checksum and generation provenance, or downgrade the thesis claim to the source-ZIP reproducible preset. The preferred fix is to provide a reproducible cache-generation recipe plus expected SHA-256 and resource requirements.
**Verification steps:** From a clean ZIP extraction, run `python scripts/verification/native_exact_validation.py --preset canonical`; it should either pass from included artifacts or the thesis must explicitly say canonical reproduction requires an external generated cache.

## 2. Thesis writing issues

### 5. “Depth” wording still conflates requested scramble length with verified optimal depth

**Severity:** High
**Files / locations:** `thesis/chapters/05_korf.tex:466-484`; `thesis/chapters/05_korf.tex:491-494`; `thesis/chapters/07_evaluation.tex:203-217`; `thesis/chapters/09_conclusions.tex:47-49`; `README.md:106`; `results/benchmarks/thesis/thesis_results_combined.json:115-119`
**Problem:** Several tables and conclusions still say “depth” for bins that the JSON metadata defines as requested scramble length, not verified optimal distance.
**Why it matters:** “Depth 20” reads like an optimal-distance claim, but the checked-in corpus contains redundant scrambles and verified depths often lower than requested length.
**Exact fix:** Replace “Βάθος”, “βάθος 15/20”, and “depth-20 cases” with “ζητούμενο μήκος scramble” or “requested scramble length” wherever the bin is generated length. Reserve “verified optimal depth” only for `verified_scramble_depth`.
**Verification steps:** `grep -R -n "Βάθος\\|βάθος\\|depth-20" thesis README.md`; confirm every remaining occurrence is either theoretical depth or explicitly verified depth.

### 6. Chapter 6 misstates the strict optimality route

**Severity:** High
**Files / locations:** `thesis/chapters/06_heuristics.tex:11-14`; `thesis/chapters/07_evaluation.tex:34-44`; `thesis/chapters/05_korf.tex:11-14`
**Problem:** Chapter 6 says strict optimality results rely on the exact Korf route with pattern databases from Chapter 5, while Chapter 7 says the official deep benchmark uses the external `RubiksCube-OptimalSolver` backend.
**Why it matters:** This creates a thesis-code mismatch about which implementation actually supports the benchmark optimality claim.
**Exact fix:** Rewrite Chapter 6 to state that strict benchmark optimality is based on the external exact benchmark backend, while the native exact route and pattern-database infrastructure are separately validated and exploratory/partial for deeper runs.
**Verification steps:** Re-read Chapters 5–7 and confirm they consistently distinguish native exact, theoretical PDB framework, and external exact benchmark backend.

### 7. Chapter 5 underreports memory for the full PDB heuristic

**Severity:** High
**Files / locations:** `thesis/chapters/05_korf.tex:252-276`; `src/korf/corner_database.py:8-15`; `src/korf/edge_database.py:4-12`; `src/korf/edge_database.py:278-280`; `src/korf/distance_estimator.py:171-199`
**Problem:** The equation uses `max(h_corner, h_edge1, h_edge2)`, but the table reports Pattern DB memory as `~44 MB`, which corresponds only to a compressed corner database, not the complete three-database setup.
**Why it matters:** The resource-cost claim is technically wrong for the implemented full PDB estimator.
**Exact fix:** Split the table row into “corner-only compressed ~44 MB”, “two edge DBs additional ~40 MB each compressed”, and “exact-safe byte storage roughly 84.1 MiB + 2 × 42.6 MB before overhead.”
**Verification steps:** Recompute from constants in `corner_database.py` and `edge_database.py`; confirm the thesis table no longer presents `~44 MB` as the whole PDB memory footprint.

### 8. Chapter 6 pseudocode uses a singular edge database although the implementation uses two

**Severity:** Medium
**Files / locations:** `thesis/chapters/06_heuristics.tex:232-233`; `thesis/chapters/06_heuristics.tex:327-342`; `src/korf/distance_estimator.py:9-11`; `src/korf/distance_estimator.py:171-199`
**Problem:** The chapter text says the implementation uses corner + two edge databases, but the pseudocode returns `max(corner_db, edge_db)`.
**Why it matters:** It is a small but concrete mismatch between explanation and implementation.
**Exact fix:** Change line 339 to `max(corner_db, edge1_db, edge2_db)`.
**Verification steps:** `grep -n "edge_db" thesis/chapters/06_heuristics.tex`; confirm the pseudocode uses both edge databases.

### 9. English code-switching is too dense in formal Greek thesis prose

**Severity:** Medium
**Files / locations:** `thesis/chapters/07_evaluation.tex:10-20`; `thesis/chapters/05_korf.tex:13-14`; `thesis/chapters/05_korf.tex:462-464`
**Problem:** Dense terms such as `benchmarks`, `solvers`, `solver instances`, `batch`, `lazy loading`, `batch-amortized timings`, and `steady-state solve times` are used directly in Greek prose.
**Why it matters:** The tone reads like engineering notes rather than a polished academic thesis.
**Exact fix:** Add a short terminology convention or glossary, then translate repeated terms after first mention, for example “δέσμη εκτελέσεων (batch)” and “χρόνοι μετά από προθέρμανση (steady-state timings).”
**Verification steps:** Re-read Chapters 5–7 after terminology normalization; verify English terms are either defined once or used only where technically necessary.

## 3. Technical/code issues

### 10. Kociemba timeout does not enforce a true wall-clock solve budget

**Severity:** High
**Files / locations:** `src/kociemba/solver.py:335-359`; `src/kociemba/solver.py:420-429`; `src/kociemba/solver.py:139-141`
**Problem:** The timeout is checked after `_initialize()`, so table generation/loading can exceed the requested timeout. Phase 2 then computes `remaining_time = timeout - phase1_time`, which ignores initialization time.
**Why it matters:** API timeout semantics are misleading, and benchmark timing interpretation becomes weaker.
**Exact fix:** Use a single deadline from the beginning of `solve()`, pass remaining budget through initialization, Phase 1, and Phase 2, and compute Phase 2 budget from total elapsed time rather than only Phase 1 time.
**Verification steps:** Add a unit test that monkeypatches `_initialize()` to sleep longer than timeout; `solve(timeout=0.05)` should return within the timeout plus documented grace.

### 11. `solve_cube()` creates a fresh solver every call

**Severity:** Medium
**Files / locations:** `src/kociemba/solver.py:740-767`
**Problem:** The convenience function constructs `KociembaSolver()` on every invocation. This defeats solver reuse and can repeatedly load or generate tables in tests and demos.
**Why it matters:** It worsens cold-start performance and contributes to the fast-test reproducibility problem.
**Exact fix:** Add an optional solver argument, a module-level cached solver, or remove `solve_cube()` from default tests in favor of a shared solver fixture.
**Verification steps:** Instrument `_initialize()` and run repeated `solve_cube()` calls; initialization should not repeat unless explicitly requested.

### 12. `verify_setup.py` does not verify thesis or webapp artifact builds

**Severity:** Medium
**Files / locations:** `verify_setup.py:531-539`; `verify_setup.py:566-568`; `README.md:33-37`; `README.md:144-145`
**Problem:** `verify_setup.py` can print “Setup is complete” after Python checks only. It does not run `scripts/thesis_workflow.py validate/build` or `webapp` build/test commands.
**Why it matters:** A reviewer can believe the full repository is reproducible even when the thesis or preview app build path is broken or untested.
**Exact fix:** Add artifact checks, for example `--all-artifacts`, that run thesis workflow validation and `cd webapp && npm ci && npm test && npm run build`, or rename the script to `verify_python_setup.py`.
**Verification steps:** Run `python verify_setup.py` in an environment without `bibtex`; it should not report full repository setup as complete unless thesis build validation is clearly out of scope.

### 13. Project dependencies are not cleanly separated into runtime/test/UI/benchmark extras

**Severity:** Medium
**Files / locations:** `pyproject.toml:11-25`; `requirements.txt:1-42`; `README.md:41-44`
**Problem:** `pyproject.toml` installs test tools, plotting libraries, Streamlit, and the external exact backend as base dependencies, and `RubikOptimal` is unversioned there.
**Why it matters:** The core package install is heavier and less reproducible than necessary. It also blurs which dependencies are needed for core solving versus thesis benchmarks.
**Exact fix:** Define optional extras such as `[test]`, `[ui]`, `[benchmark]`, `[external-exact]`, and `[dev]`; pin `RubikOptimal>=1.1.0` in the relevant extra or rely on a generated lock file.
**Verification steps:** `pip install -e .` should install only core solver dependencies; `pip install -e ".[benchmark,external-exact]"` should install the full thesis benchmark stack.

## 4. Research/experimental issues

### 14. Legacy benchmark corpus is heavily redundant

**Severity:** High
**Files / locations:** `results/benchmarks/thesis/thesis_results_combined.json:117-119`; `results/benchmarks/thesis/thesis_results_combined.json:141-149`; `results/benchmarks/thesis/thesis_results_combined.json:207-229`; `thesis/chapters/07_evaluation.tex:88-90`
**Problem:** The JSON metadata says the corpus allows adjacent same-face moves and cancellations. The first record is requested length 5 but contains adjacent `F'`, `F` and has verified depth 3. A full scan of the JSON found 78/100 scrambles with adjacent same-face moves and 79 completed exact cases with verified depth lower than requested length.
**Why it matters:** The experiment is valid as a fixed legacy corpus, but not as evidence about uniform exact-depth strata.
**Exact fix:** Regenerate a corpus with no consecutive same-face moves and, if claiming depth, bin cases by verified optimal depth. Keep the legacy corpus only as an archival comparison.
**Verification steps:** Run a script over `scramble_moves` to reject adjacent same-face moves and compare `verified_scramble_depth` against requested length; update Chapter 7 tables to use the corrected bins.

### 15. Timing statistics are single-run and batch-amortized

**Severity:** High
**Files / locations:** `results/benchmarks/thesis/thesis_results_combined.json:24-26`; `thesis/chapters/07_evaluation.tex:125-132`; `thesis/chapters/07_evaluation.tex:180-184`; `thesis/chapters/07_evaluation.tex:376-385`
**Problem:** The artifact contains no repetitions per scramble, no confidence intervals, and no clean cold/warm separation.
**Why it matters:** Mean timing comparisons are descriptive for this one run, not statistically robust performance claims.
**Exact fix:** Re-run with at least 5–10 repetitions per scramble, randomized solver order, explicit warmup, and separate cold-start/warm-start results. Report median, IQR, and confidence intervals.
**Verification steps:** New benchmark JSON should include `run_id`, repetition index, warmup flag, seed, and per-run environment metadata.

### 16. Memory measurements are process-level RSS deltas in a shared process

**Severity:** Medium
**Files / locations:** `src/evaluation/algorithm_comparison.py:253-260`; `thesis/chapters/07_evaluation.tex:75-81`; `thesis/chapters/07_evaluation.tex:150`; `thesis/chapters/07_evaluation.tex:384-385`
**Problem:** Memory is measured as RSS delta inside one shared sequential benchmark process with reused solver instances.
**Why it matters:** It is not an isolated peak-memory measurement per solver, so memory comparisons can be noisy or misleading.
**Exact fix:** Run each solver invocation in a subprocess and record peak RSS/high-water mark. Record whether caches were cold or warm.
**Verification steps:** New benchmark output should contain isolated peak RSS per solver/run and should not depend on solver order in a shared process.

### 17. External exact backend is central to the strongest optimality result but remains outside the repository implementation

**Severity:** High
**Files / locations:** `README.md:98-112`; `thesis/chapters/07_evaluation.tex:34-44`; `thesis/references.bib:157-162`; `pyproject.toml:21`
**Problem:** The official deep optimal benchmark depends on `RubikOptimal` / `RubiksCube-OptimalSolver`, not on the native solver. The repo documents this, but the benchmark’s strongest claim depends on an external package.
**Why it matters:** Reproducibility and implementation ownership are weaker than if the exact backend were fully vendored, checksummed, or reproduced through a locked container.
**Exact fix:** Provide a pinned external backend artifact with version, wheel hash or commit hash, license statement, and cache-generation provenance; otherwise frame the result as “external-backend baseline” throughout.
**Verification steps:** From a clean environment, install the locked backend, run a small exact benchmark subset, and confirm `backend: optimal_external` results match the canonical JSON schema and guarantees.

## 5. Citation/reference issues

### 18. Thistlethwaite is cited through a secondary web page

**Severity:** Medium
**Files / locations:** `thesis/references.bib:25-31`; `thesis/chapters/03_thistlethwaite.tex:8-16`; `thesis/chapters/02_background.tex:160`; `thesis/chapters/02_background.tex:237`
**Problem:** The bibliography key `thistlethwaite1981` is a Jaap Scherphuis web page, not a primary publication by Morwen Thistlethwaite.
**Why it matters:** Foundational algorithm history should use the strongest available source, or clearly label secondary sources.
**Exact fix:** Add a primary or archival Thistlethwaite source if available. If only secondary sources are used, state that explicitly in the thesis and avoid presenting the web page as the primary algorithm publication.
**Verification steps:** Inspect `references.bib`; confirm `thistlethwaite1981` is replaced or supplemented by a primary/archival reference.

### 19. NP-completeness citation is used too broadly for fixed 3×3 empirical cost

**Severity:** Medium
**Files / locations:** `thesis/chapters/07_evaluation.tex:156-162`; `thesis/chapters/07_evaluation.tex:333-340`; `thesis/references.bib:250-256`
**Problem:** The text uses the NP-completeness citation alongside IDA* cost to explain empirical timeout behavior on this fixed 3×3 benchmark.
**Why it matters:** The cited complexity result does not by itself substantiate the specific empirical runtime behavior of the fixed 3×3 corpus.
**Exact fix:** Use Korf/time-complexity references and the measured node counts for the empirical fixed-cube claim. Keep the NP-completeness citation only for broader generalized-cube complexity context.
**Verification steps:** Search for `demaine2018npcomplete`; confirm it is not used as direct evidence for fixed 3×3 timing or timeout claims.

### 20. External exact backend citation lacks archival precision

**Severity:** Medium
**Files / locations:** `thesis/references.bib:157-162`; `README.md:110-112`; `results/benchmarks/thesis/thesis_results_combined.json:120-134`
**Problem:** The backend reference gives a GitHub URL and package version note, but no commit hash, wheel hash, release archive, or license citation.
**Why it matters:** This is the most important external component in the optimal benchmark path. It needs reproducible citation and attribution.
**Exact fix:** Add a versioned release/tag/commit identifier, package hash, and formal license statement if available. Record the exact artifact in the reproducibility manifest.
**Verification steps:** `grep -n "kociemba_rubiks_optimal" thesis/references.bib`; confirm the entry contains a stable release identifier and artifact checksum/provenance.

## 6. Reproducibility/setup issues

### 21. Python lock file is not cryptographic and omits platform/toolchain constraints

**Severity:** Medium
**Files / locations:** `README.md:41-44`; `requirements.lock:1-80`; `REPRODUCIBILITY_MANIFEST.json:1-47`
**Problem:** The repository explicitly states that `requirements.lock` lacks hashes, platform markers, Python ABI constraints, and TeX/Tectonic versions.
**Why it matters:** Package integrity and cross-platform reproducibility are not fully locked.
**Exact fix:** Generate a hash-locked Python environment file, for example with `pip-tools --generate-hashes` or a modern lockfile, and record TeX/Tectonic/Docker image versions or digests.
**Verification steps:** `pip install --require-hashes -r requirements.lock` or the replacement lock should succeed; manifest should include TeX/Node/Python/package artifact versions.

### 22. Benchmark environment metadata was added post hoc

**Severity:** Medium
**Files / locations:** `results/benchmarks/thesis/thesis_results_combined.json:120-134`
**Problem:** The JSON says the original benchmark did not record full hardware/package metadata and that environment metadata was added post hoc.
**Why it matters:** The canonical benchmark artifact lacks fully contemporaneous run metadata.
**Exact fix:** Re-run canonical benchmarks with environment capture at benchmark start, including hardware, Python, package versions, cache state, solver backend versions, and artifact hash.
**Verification steps:** New JSON should not contain the post-hoc note and should include a `run_environment_captured_at_start` or equivalent field.

### 23. Source-ZIP smoke validation is clearly separated from canonical validation, but thesis claims still rely on non-ZIP artifacts

**Severity:** Medium
**Files / locations:** `data/README.md:56-65`; `results/validation/native_exact/README.md:51-56`; `results/validation/native_exact/MANIFEST.json:64-72`
**Problem:** The repository provides a source-ZIP smoke validation, but the thesis claims in the native exact manifest require a full corner DB that the ZIP does not contain.
**Why it matters:** Reviewers using only the submitted ZIP can validate the code path, but not the canonical native exact claim.
**Exact fix:** In the thesis and README, explicitly label which validation claims are reproducible from the source ZIP and which require external/generated cache artifacts.
**Verification steps:** Run both `--preset source-zip` and `--preset canonical` from a fresh ZIP; documentation should predict exactly which one passes and why.

## 7. Submission polish issues

### 24. Table formatting is inconsistent and uses vertical-rule tables despite booktabs-style tables elsewhere

**Severity:** Low
**Files / locations:** `thesis/chapters/02_background.tex:31-40`; `thesis/chapters/05_korf.tex:43-55`; `thesis/chapters/05_korf.tex:139-151`; `thesis/chapters/05_korf.tex:264-278`; `thesis/chapters/05_korf.tex:466-480`; `thesis/chapters/05_korf.tex:509-522`; `thesis/chapters/07_evaluation.tex:203-217`
**Problem:** Some tables use `|c|` vertical rules and `\hline`, while later evaluation tables use cleaner booktabs-style formatting.
**Why it matters:** The manuscript looks inconsistent and less polished.
**Exact fix:** Convert thesis tables to a consistent style, preferably `booktabs` without vertical rules, and align units/decimal formatting.
**Verification steps:** `grep -R -n "begin{tabular}{|" thesis`; expected result should be zero or only intentionally schematic mini-tables.

---

## FIX_TARGETS

```json
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "thesis/main.tex; thesis/chapters/00_approval.tex; thesis/README.md; README.md",
    "location": "thesis/main.tex:173-180; thesis/chapters/00_approval.tex:34-44; thesis/README.md:3; README.md:7-8",
    "issue": "Formal institutional approval page is incomplete and excluded from the thesis build.",
    "exact_fix": "Fill official committee names and examination date in thesis/chapters/00_approval.tex and include \\input{chapters/00_approval} in thesis/main.tex after the title page or at the institutionally required location.",
    "verification_steps": "Run grep -n \"00_approval\" thesis/main.tex; confirm no placeholder committee text or dotfill date remains; rebuild the thesis and inspect the first pages of thesis/main.pdf."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "scripts/thesis_workflow.py; thesis/README.md",
    "location": "scripts/thesis_workflow.py:483-495; scripts/thesis_workflow.py:1035-1069; thesis/README.md:37-43; thesis/README.md:88-100",
    "issue": "Local thesis build path invokes latexmk when bibtex is missing, despite toolchain_status marking local TeX as not ready.",
    "exact_fix": "Require tools[\"bibliography_tool\"] before invoking latexmk in build_thesis(mode=\"local\"), or route to Tectonic/Docker/clear prerequisite error when the bibliography backend is missing.",
    "verification_steps": "Remove bibtex from PATH while latexmk and xelatex remain available; run python scripts/thesis_workflow.py build --mode local --clean; verify it fails with a clear prerequisite message instead of running latexmk and producing a bibtex shell error."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "pytest.ini; verify_setup.py; tests/unit/test_kociemba.py; src/kociemba/solver.py; src/kociemba/pruning.py",
    "location": "pytest.ini:1-7; verify_setup.py:24-29; verify_setup.py:349-398; tests/unit/test_kociemba.py:289-391; src/kociemba/solver.py:120-137; src/kociemba/pruning.py:119-123",
    "issue": "Default fast pytest profile can trigger Kociemba table generation because unmarked solve tests call solve_cube on a cold cache.",
    "exact_fix": "Mark tests/unit/test_kociemba.py:330-391 as slow or cache_building, or rewrite them to use mocks/lightweight fixtures. Keep cold-cache generation in an explicit opt-in test profile.",
    "verification_steps": "Delete data/kociemba and run python -m pytest tests -q plus python verify_setup.py; both should complete within the documented fast timeout without generating large Kociemba caches."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "data/README.md; results/validation/native_exact/README.md; results/validation/native_exact/MANIFEST.json; scripts/verification/native_exact_validation.py",
    "location": "data/README.md:36-48; data/README.md:56-65; results/validation/native_exact/README.md:5-38; results/validation/native_exact/MANIFEST.json:4-12; scripts/verification/native_exact_validation.py:247-255",
    "issue": "Canonical native exact validation requires data/pattern_databases/corner_db.pkl, which is absent from the source ZIP.",
    "exact_fix": "Ship the required corner_db.pkl artifact separately with checksum/provenance, or downgrade thesis claims to the source-ZIP reproducible validation preset. Document the exact resource requirements for regenerating the cache.",
    "verification_steps": "From a clean ZIP extraction, run python scripts/verification/native_exact_validation.py --preset canonical; it should either pass from included artifacts or documentation must explicitly state the required external/generated cache."
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/05_korf.tex; thesis/chapters/07_evaluation.tex; thesis/chapters/09_conclusions.tex; README.md; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "thesis/chapters/05_korf.tex:466-484; thesis/chapters/05_korf.tex:491-494; thesis/chapters/07_evaluation.tex:203-217; thesis/chapters/09_conclusions.tex:47-49; README.md:106; results/benchmarks/thesis/thesis_results_combined.json:115-119",
    "issue": "The thesis still uses depth terminology for requested scramble-length bins.",
    "exact_fix": "Replace these instances with ζητούμενο μήκος scramble or requested scramble length. Use verified optimal depth only for verified_scramble_depth.",
    "verification_steps": "Run grep -R -n \"Βάθος\\|βάθος\\|depth-20\" thesis README.md and verify every remaining occurrence is theoretically correct or explicitly tied to verified_scramble_depth."
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/06_heuristics.tex; thesis/chapters/07_evaluation.tex; thesis/chapters/05_korf.tex",
    "location": "thesis/chapters/06_heuristics.tex:11-14; thesis/chapters/07_evaluation.tex:34-44; thesis/chapters/05_korf.tex:11-14",
    "issue": "Chapter 6 says strict optimality results rely on the exact Korf/PDB route, while Chapter 7 says the official benchmark uses the external exact backend.",
    "exact_fix": "Rewrite Chapter 6 to state that strict benchmark optimality relies on the external exact backend, while the native exact/PDB route is separately validated and not the deep benchmark source.",
    "verification_steps": "Re-read Chapters 5, 6, and 7 and confirm all three consistently distinguish native exact, theoretical PDB framework, and external benchmark backend."
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/05_korf.tex; src/korf/corner_database.py; src/korf/edge_database.py; src/korf/distance_estimator.py",
    "location": "thesis/chapters/05_korf.tex:252-276; src/korf/corner_database.py:8-15; src/korf/edge_database.py:4-12; src/korf/edge_database.py:278-280; src/korf/distance_estimator.py:171-199",
    "issue": "Chapter 5 reports Pattern DB memory as ~44 MB even though the described heuristic uses corner, edge1, and edge2 databases.",
    "exact_fix": "Separate corner-only compressed memory from full corner+edge1+edge2 memory and exact-safe byte storage. Update the table to show the aggregate cost.",
    "verification_steps": "Recompute memory from CORNER_DB_SIZE and the two 42,577,920-state edge databases; confirm the table no longer presents ~44 MB as the full PDB footprint."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/06_heuristics.tex; src/korf/distance_estimator.py",
    "location": "thesis/chapters/06_heuristics.tex:232-233; thesis/chapters/06_heuristics.tex:327-342; src/korf/distance_estimator.py:9-11; src/korf/distance_estimator.py:171-199",
    "issue": "Chapter 6 pseudocode returns max(corner_db, edge_db) although the implementation uses edge1 and edge2.",
    "exact_fix": "Change the pseudocode to max(corner_db, edge1_db, edge2_db).",
    "verification_steps": "Run grep -n \"edge_db\" thesis/chapters/06_heuristics.tex and confirm no singular edge_db remains in the PDB pseudocode."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex; thesis/chapters/05_korf.tex",
    "location": "thesis/chapters/07_evaluation.tex:10-20; thesis/chapters/05_korf.tex:13-14; thesis/chapters/05_korf.tex:462-464",
    "issue": "Dense English code-switching weakens the formal Greek academic tone.",
    "exact_fix": "Add a terminology convention/glossary and translate repeated terms after first definition, keeping English only where technically necessary.",
    "verification_steps": "Review Chapters 5-7 and confirm repeated terms such as batch, solver instance, lazy loading, benchmark, and steady-state are either defined once or consistently translated."
  },
  {
    "severity": "High",
    "category": "Technical/code issues",
    "file": "src/kociemba/solver.py",
    "location": "src/kociemba/solver.py:335-359; src/kociemba/solver.py:420-429; src/kociemba/solver.py:139-141",
    "issue": "Kociemba timeout is not a true wall-clock timeout because initialization time is checked only after table loading and Phase 2 budget ignores initialization.",
    "exact_fix": "Introduce a single solve deadline at the start of solve(), compute remaining time from that deadline for initialization, Phase 1, and Phase 2, and remove timeout - phase1_time as the Phase 2 budget calculation.",
    "verification_steps": "Add a unit test that monkeypatches _initialize() to exceed timeout; solve(timeout=0.05) should return within timeout plus documented grace."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/kociemba/solver.py",
    "location": "src/kociemba/solver.py:740-767",
    "issue": "solve_cube() creates a new KociembaSolver every call, preventing solver reuse.",
    "exact_fix": "Add an optional solver parameter or module-level cached solver, or remove solve_cube from fast tests in favor of a shared solver fixture.",
    "verification_steps": "Instrument _initialize() and run repeated solve_cube() calls; initialization should not repeat when using the shared solver path."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "verify_setup.py; README.md",
    "location": "verify_setup.py:531-539; verify_setup.py:566-568; README.md:33-37; README.md:144-145",
    "issue": "verify_setup.py does not verify thesis or webapp build artifacts but can still report setup complete.",
    "exact_fix": "Add artifact checks for scripts/thesis_workflow.py validate/build and webapp npm test/build, or rename the script to verify_python_setup.py and clearly document the narrower scope.",
    "verification_steps": "Run python verify_setup.py in an environment missing bibtex; it should not claim full repository setup is complete unless thesis validation is explicitly out of scope."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "pyproject.toml; requirements.txt; README.md",
    "location": "pyproject.toml:11-25; requirements.txt:1-42; README.md:41-44",
    "issue": "Runtime, test, UI, benchmark, and external exact backend dependencies are bundled together in base project dependencies.",
    "exact_fix": "Create optional extras for test, ui, benchmark, external-exact, and dev dependencies. Pin RubikOptimal in the appropriate extra or through a generated lockfile.",
    "verification_steps": "pip install -e . should install only core solver dependencies; pip install -e '.[benchmark,external-exact]' should install the full thesis benchmark stack."
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "results/benchmarks/thesis/thesis_results_combined.json:117-119; results/benchmarks/thesis/thesis_results_combined.json:141-149; results/benchmarks/thesis/thesis_results_combined.json:207-229; thesis/chapters/07_evaluation.tex:88-90",
    "issue": "Legacy benchmark corpus contains redundant scrambles and should not be interpreted as exact-depth strata.",
    "exact_fix": "Regenerate benchmark cases with no consecutive same-face moves and, for depth claims, bin by verified optimal depth rather than requested generation length.",
    "verification_steps": "Scan scramble_moves for adjacent same-face moves and compare requested_scramble_length against verified_scramble_depth; corrected corpus should pass the adjacency check and use verified-depth bins when claiming depth."
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "results/benchmarks/thesis/thesis_results_combined.json:24-26; thesis/chapters/07_evaluation.tex:125-132; thesis/chapters/07_evaluation.tex:180-184; thesis/chapters/07_evaluation.tex:376-385",
    "issue": "Benchmark timing data are single-run and batch-amortized, with no confidence intervals or cold/warm separation.",
    "exact_fix": "Repeat each scramble multiple times, randomize solver order, separate warmup from measured runs, and report median/IQR/confidence intervals.",
    "verification_steps": "New benchmark JSON should include repetition index, run_id, warmup flag, seed, and per-run environment metadata."
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "src/evaluation/algorithm_comparison.py; thesis/chapters/07_evaluation.tex",
    "location": "src/evaluation/algorithm_comparison.py:253-260; thesis/chapters/07_evaluation.tex:75-81; thesis/chapters/07_evaluation.tex:150; thesis/chapters/07_evaluation.tex:384-385",
    "issue": "Memory metric is process RSS delta in a shared benchmark process, not isolated peak memory per solver.",
    "exact_fix": "Run solver measurements in isolated subprocesses and record peak RSS/high-water mark with cache/warmup state.",
    "verification_steps": "New benchmark output should contain isolated peak RSS per solver invocation and should not depend on shared-process solver order."
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "README.md; thesis/chapters/07_evaluation.tex; thesis/references.bib; pyproject.toml",
    "location": "README.md:98-112; thesis/chapters/07_evaluation.tex:34-44; thesis/references.bib:157-162; pyproject.toml:21",
    "issue": "Strongest optimal benchmark claim depends on an external exact backend rather than the repository's native exact implementation.",
    "exact_fix": "Pin and document the external backend artifact with version, commit or wheel hash, license statement, and cache-generation provenance, or consistently frame the result as an external-backend baseline.",
    "verification_steps": "From a clean environment, install the locked backend and regenerate a benchmark subset with backend: optimal_external matching the canonical schema."
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; thesis/chapters/03_thistlethwaite.tex; thesis/chapters/02_background.tex",
    "location": "thesis/references.bib:25-31; thesis/chapters/03_thistlethwaite.tex:8-16; thesis/chapters/02_background.tex:160; thesis/chapters/02_background.tex:237",
    "issue": "Thistlethwaite algorithm is cited through a secondary web page rather than a primary or archival source.",
    "exact_fix": "Add a primary or archival Thistlethwaite reference if available; otherwise explicitly label the current source as a secondary historical summary.",
    "verification_steps": "Inspect thesis/references.bib and confirm thistlethwaite1981 is replaced or supplemented by a stronger source."
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/chapters/07_evaluation.tex; thesis/references.bib",
    "location": "thesis/chapters/07_evaluation.tex:156-162; thesis/chapters/07_evaluation.tex:333-340; thesis/references.bib:250-256",
    "issue": "NP-completeness citation is used too broadly to support empirical fixed-3x3 timeout behavior.",
    "exact_fix": "Use Korf/time-complexity references and measured node counts for fixed-cube empirical runtime claims; reserve demaine2018npcomplete for broader generalized-cube complexity context.",
    "verification_steps": "Search for demaine2018npcomplete and confirm it is not used as direct evidence for fixed 3x3 timing or timeout claims."
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; README.md; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "thesis/references.bib:157-162; README.md:110-112; results/benchmarks/thesis/thesis_results_combined.json:120-134",
    "issue": "External exact backend citation lacks a stable archived release, commit hash, wheel hash, or formal license statement.",
    "exact_fix": "Update the bibliography and reproducibility manifest with a versioned release/tag/commit, package hash, and license statement.",
    "verification_steps": "grep -n \"kociemba_rubiks_optimal\" thesis/references.bib and confirm the entry contains stable artifact provenance."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "README.md; requirements.lock; REPRODUCIBILITY_MANIFEST.json",
    "location": "README.md:41-44; requirements.lock:1-80; REPRODUCIBILITY_MANIFEST.json:1-47",
    "issue": "Python dependency snapshot is not cryptographic and omits platform, ABI, and TeX/Tectonic constraints.",
    "exact_fix": "Generate a hash-locked dependency file and record TeX/Tectonic/Docker image versions or digests in the reproducibility manifest.",
    "verification_steps": "pip install --require-hashes -r requirements.lock or the replacement lockfile should succeed; manifest should include full toolchain versions."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json",
    "location": "results/benchmarks/thesis/thesis_results_combined.json:120-134",
    "issue": "Canonical benchmark environment metadata was added post hoc rather than captured at benchmark start.",
    "exact_fix": "Re-run canonical benchmarks with environment capture at run start, including hardware, Python/package versions, cache state, backend version, and artifact hash.",
    "verification_steps": "New JSON should remove the post-hoc note and include an explicit run-start environment metadata field."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "data/README.md; results/validation/native_exact/README.md; results/validation/native_exact/MANIFEST.json",
    "location": "data/README.md:56-65; results/validation/native_exact/README.md:51-56; results/validation/native_exact/MANIFEST.json:64-72",
    "issue": "Source-ZIP smoke validation is executable, but thesis native exact claims rely on non-ZIP cache artifacts.",
    "exact_fix": "Explicitly label source-ZIP reproducible claims versus canonical cache-dependent claims in the thesis and README.",
    "verification_steps": "Run both --preset source-zip and --preset canonical from a clean ZIP; documentation should correctly predict which passes and which requires the full corner cache."
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "thesis/chapters/02_background.tex; thesis/chapters/05_korf.tex; thesis/chapters/07_evaluation.tex",
    "location": "thesis/chapters/02_background.tex:31-40; thesis/chapters/05_korf.tex:43-55; thesis/chapters/05_korf.tex:139-151; thesis/chapters/05_korf.tex:264-278; thesis/chapters/05_korf.tex:466-480; thesis/chapters/05_korf.tex:509-522; thesis/chapters/07_evaluation.tex:203-217",
    "issue": "Table formatting is inconsistent, mixing vertical-rule hline tables with cleaner booktabs-style tables.",
    "exact_fix": "Convert tables to a consistent booktabs style without vertical rules and standardize units/decimal formatting.",
    "verification_steps": "Run grep -R -n \"begin{tabular}{|\" thesis and verify no inconsistent vertical-rule tables remain except intentional schematic mini-tables."
  }
]
```

## Scores

**Overall thesis quality score:** 76/100
**Technical quality score:** 68/100
**Submission readiness score:** 42/100
