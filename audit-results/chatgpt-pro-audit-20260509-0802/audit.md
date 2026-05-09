I audited the extracted ZIP only. I did not use GitHub or external repositories. I verified the benchmark arithmetic against the checked-in JSON, checked citation-key resolution, inspected the LaTeX source, README/setup files, solver code, UI code, validation artifacts, and ran representative reproducibility commands.

Positive checks worth noting before the findings: Chapter 7’s main numerical benchmark tables match `results/benchmarks/thesis/thesis_results_combined.json`; I found no missing BibTeX citation keys; figure paths referenced by `\includegraphics` exist; `webapp` can pass `npm test` and `npm run build` after `npm ci`. The blockers below are therefore not about fabricated benchmark numbers, but about submission readiness, reproducibility, stale claims, and code/test robustness.

## 1. Critical blockers

### CB1 — Final institutional front matter is not submission-ready

Severity: **critical**
File/location: `thesis/main.tex`, lines 173–180; supporting file `thesis/chapters/00_approval.tex`, lines 36–44
Problem: `main.tex` explicitly excludes the formal approval/signature page, and the approval page still contains placeholder committee-member rows plus a dotted examination date.
Why it matters: This is a hard submission blocker for a university thesis. A PDF without the required approval/signature front matter is a review build, not a final institutional submission.
Exact fix: Fill in all official committee names/titles and examination date in `00_approval.tex`; include `\input{chapters/00_approval}` after the title page and before acknowledgements if required by the department; rebuild and inspect the PDF front matter.
Verification: Rebuild `thesis/main.pdf`; confirm the approval page appears, has no placeholder “Μέλος Εξεταστικής Επιτροπής” rows, and has a real examination date.

### CB2 — Documented default test command does not complete reliably

Severity: **critical**
File/location: `tests/unit/test_thistlethwaite.py`, lines 504–558; `README.md`, lines 34 and 127–128; `pytest.ini`, lines 1–7
Problem: The README’s default command `python -m pytest tests -q` is described as the supported fast profile, but unmarked Thistlethwaite solver-quality/integration tests run slow pure solver calls with no `max_time`. In audit, `python -m pytest tests --collect-only -q` collected `287/297` active tests, but `python -m pytest tests -q` did not complete; `timeout 120 python -m pytest tests/unit/test_thistlethwaite.py -q` stopped after 26 dots.
Why it matters: A thesis artifact’s “fast reproducibility profile” must be runnable by reviewers. A default test suite that can hang or exceed practical review time undermines reproducibility claims.
Exact fix: Mark `test_solution_length_bound`, `test_solution_correctness`, and `test_integration_example` as `@pytest.mark.slow`, or reduce them to deterministic small smoke tests with explicit `max_time`, fewer seeds, and timeout-safe assertions. Keep heavyweight quality checks in an opt-in profile.
Verification: Run `python -m pytest tests --collect-only -q` and `python -m pytest tests -q` in a clean environment; both should complete within the documented fast-profile runtime.

### CB3 — The documented thesis build path was not usable in the audit environment

Severity: **major**
File/location: `thesis/README.md`, lines 35–43; `README.md`, lines 49–53 and 130–131
Problem: The documented review-build path is `python scripts/thesis_workflow.py build --mode auto`, with fallback to local TeX, Tectonic, or Docker. In the audit environment, `python scripts/thesis_workflow.py validate --output /tmp/validation.md` reported “Thesis build path ready: fail,” and `python scripts/thesis_workflow.py build --mode auto` returned: “No usable build path found.”
Why it matters: The checked-in PDF exists, but a reproducibility auditor must be able to rebuild it or have a fully specified build environment. The repository currently depends on host tooling availability.
Exact fix: Provide a reviewer-proof build route: either a pinned container workflow with clear Docker prerequisite checks, or a lockfile/environment script that installs TeX/Tectonic/BibTeX dependencies. Add CI-style build verification or a documented expected failure mode when Docker/TeX are unavailable.
Verification: From a clean machine/container, run `python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md` and `python scripts/thesis_workflow.py build --mode auto`; both should report a usable build path and produce `thesis/main.pdf`.

## 2. Thesis writing issues

### TW1 — Abstracts read like implementation changelogs rather than thesis abstracts

Severity: **medium**
File/location: `thesis/chapters/00_abstract_en.tex`, lines 14–24 and 31–35; `thesis/chapters/00_abstract_gr.tex`, lines 14–26 and 33–37
Problem: Both abstracts contain dense implementation-state details about native exact paths, external backend caveats, corner PDB support, timeout edge cases, and repository internals.
Why it matters: A thesis abstract should communicate problem, method, main results, and contribution concisely. Excessive repository-status detail weakens academic tone and readability.
Exact fix: Move backend/corpus caveats to Chapters 7–8. Keep the abstract to one concise paragraph on methods plus one concise paragraph on results, with only the central quantitative results.
Verification: Re-read both abstracts independently of the repository; a non-repository reviewer should understand the contribution without parsing implementation history.

### TW2 — Stale test-count claim in Chapter 8

Severity: **major**
File/location: `thesis/chapters/08_implementation.tex`, line 222
Problem: The thesis claims “291 συλλεγόμενα tests.” The current extracted ZIP collects `287/297 tests collected (10 deselected)` under the default marker profile.
Why it matters: This is a direct inconsistency between manuscript and repository state. Reviewers can reproduce the mismatch with a single command.
Exact fix: Replace the hard-coded number with the current collect result, or avoid fixed counts: “το ακριβές πλήθος αναπαράγεται με `pytest --collect-only`.”
Verification: Run `python -m pytest tests --collect-only -q`; update the manuscript to match the resulting count.

### TW3 — “Complete/comprehensive test suite” language is too strong

Severity: **medium**
File/location: `thesis/chapters/00_abstract_en.tex`, line 35; `thesis/chapters/00_abstract_gr.tex`, line 37; `thesis/chapters/09_conclusions.tex`, line 97
Problem: The thesis says “comprehensive test suite,” “πλήρη σουίτα δοκιμών,” and “ολοκληρωμένο test suite.” The default test command did not complete in audit, and canonical native validation requires a missing generated cache.
Why it matters: The repository has extensive tests, but “complete/full” implies stronger validation than the artifact currently supports from the ZIP alone.
Exact fix: Use “extensive test suite” and explicitly distinguish fast, slow, external, and cache-building validation profiles.
Verification: Confirm the wording no longer implies all validation is runnable from the source ZIP without opt-in caches/backends.

### TW4 — “3,501 states up to depth 3” is mathematically ambiguous

Severity: **minor**
File/location: `thesis/chapters/00_abstract_en.tex`, line 31; `thesis/chapters/00_abstract_gr.tex`, line 33; `scripts/verification/native_exact_validation.py`, lines 88–122
Problem: The validation generator excludes the solved root state from the corpus; it appends only successor states. The thesis says “3,501 unique states up to depth 3,” which normally sounds like depths 0–3.
Why it matters: For exact-distance validation, whether the root state is included should be unambiguous.
Exact fix: Rephrase to “3,501 non-solved states at depths 1–3” or include the solved state and report 3,502 states if that is the intended convention.
Verification: Run `len(generate_exhaustive_corpus(3))`; confirm the thesis wording matches the generator’s inclusion/exclusion convention.

### TW5 — Practical recommendation for Kociemba remains too broad in the conclusion

Severity: **medium**
File/location: `thesis/chapters/09_conclusions.tex`, line 172; supporting limitation text `thesis/chapters/07_evaluation.tex`, lines 343–352
Problem: The conclusion says, “Για πρακτικές εφαρμογές αυτός είναι ο Kociemba.” Earlier sections qualify the result to the fixed corpus and platform, but the final sentence reads as a general recommendation.
Why it matters: The experiments are single-machine, 100-scramble, legacy requested-length benchmarks. The final thesis claim should not overgeneralize.
Exact fix: Change to “Για τις πρακτικές εφαρμογές που μοιάζουν με το συγκεκριμένο corpus και τους μετρημένους περιορισμούς, η καλύτερη επιλογή είναι ο Kociemba.”
Verification: Ensure every recommendation sentence is scoped to corpus, timeout, backend, and platform.

### TW6 — Benchmark schema description is too generic for reproducibility

Severity: **minor**
File/location: `thesis/chapters/07_evaluation.tex`, lines 64–72; actual schema example `results/benchmarks/thesis/thesis_results_combined.json`, lines 133–208
Problem: Chapter 7 describes conceptual fields but not the actual JSON field names (`solved`, `time_seconds`, `solution_length`, `memory_mb`, `nodes_explored`, `backend`, etc.).
Why it matters: A reproducibility reader should be able to map manuscript claims directly to machine-readable artifacts.
Exact fix: Add a small schema table with exact field names and meanings.
Verification: Cross-check the schema table against `thesis_results_combined.json`.

## 3. Technical/code issues

### TC1 — Streamlit comparison page can crash on solver failure

Severity: **major**
File/location: `ui/pages/2_Comparison.py`, lines 235–244; source return values in `src/evaluation/algorithm_comparison.py`, lines 332–344 and 404–416
Problem: Failure rows format `algo_result.memory_mb` with `:.2f`, but Thistlethwaite/Kociemba no-solution results set `memory_mb=None`.
Why it matters: A failed solver case should display as a failure, not crash the comparison UI.
Exact fix: Add a safe formatter such as `format_mb(value): return "N/A" if value is None else f"{value:.2f}"`, and use it in both solved and failed branches.
Verification: Force a no-solution/timeout result and run the Streamlit comparison page; it should render “N/A” instead of raising `TypeError`.

### TC2 — Benchmark timing uses wall-clock `time.time()` instead of monotonic/performance timing

Severity: **medium**
File/location: `src/evaluation/algorithm_comparison.py`, lines 323–330, 389–400, and 462–479
Problem: Benchmark elapsed times are measured with `time.time()`.
Why it matters: Wall-clock time can move due to system clock adjustments. Benchmarking should use monotonic high-resolution timers.
Exact fix: Replace timing pairs with `time.perf_counter()` or `time.perf_counter_ns()` and record the timing method in exported metadata.
Verification: Run benchmark tests and confirm all elapsed timing uses `perf_counter` and exported metadata states the timing source.

### TC3 — Webapp tests are only static smoke/regex tests

Severity: **medium**
File/location: `webapp/tests/smoke.test.mjs`, lines 8–37
Problem: The tests only verify file existence and source regexes. They do not execute `solveCube`, cube transforms, inverse moves, or page behavior.
Why it matters: The Next.js app can build while solver-preview logic is broken.
Exact fix: Add executable unit tests for `applyMoves`, `inverseMoves`, `isSolved`, `solveCube`, timeout behavior, and comparison aggregation.
Verification: Run `cd webapp && npm test`; tests should fail on intentionally broken cube/solver logic.

### TC4 — Kociemba source documentation conflicts with benchmark results

Severity: **minor**
File/location: `src/kociemba/solver.py`, line 18; supporting result text `thesis/chapters/07_evaluation.tex`, lines 294–298
Problem: The docstring says Kociemba is “typically <19 moves in practice,” while the thesis benchmark reports about 20–22 moves at requested lengths 15 and 20.
Why it matters: Source documentation should not contradict the submitted experimental results.
Exact fix: Reword to “near-optimal in practice; this thesis corpus reports means up to about 22 moves at requested length 20.”
Verification: Search for “<19” and confirm no unsupported move-count claim remains.

### TC5 — Korf wrapper documentation overstates implementation ownership and has stale performance claims

Severity: **minor**
File/location: `src/korf/optimal_solver.py`, lines 1–24 and 82–99
Problem: The module says it “implements an optimal solver” and lists broad PyPy/CPython runtime estimates, while the actual class lazily delegates to the optional `RubikOptimal` backend.
Why it matters: The thesis is careful to distinguish native exact solving from external exact backend usage; code documentation should match that distinction.
Exact fix: Rewrite the docstring as “wrapper around optional RubikOptimal backend” and remove or source/qualify the runtime estimates.
Verification: Read the docstring and class constructor together; they should describe the same implementation path.

### TC6 — Bare `except:` in Streamlit move parser

Severity: **minor**
File/location: `ui/pages/1_Single_Solver.py`, lines 138–143
Problem: The custom-sequence parser catches all exceptions.
Why it matters: This hides real programming errors as “Invalid move,” making UI bugs harder to debug.
Exact fix: Catch the specific exception raised by invalid moves, or validate against the legal move set before applying. Log unexpected exceptions separately.
Verification: Inject a non-move-related failure and confirm it is not swallowed as a user input error.

### TC7 — Package architecture uses `src` as the importable package name

Severity: **minor**
File/location: `pyproject.toml`, lines 12–13
Problem: The package finder exports `src*`, and the code imports modules as `src...`.
Why it matters: A package literally named `src` is nonstandard and can conflict with other projects or confuse installed-package usage.
Exact fix: Rename the import package to a project-specific name such as `rubik_cube_thesis`, or switch to a conventional `src/packagename/` layout.
Verification: Install in a clean venv and confirm imports use the project package name rather than `src`.

## 4. Research/experimental issues

### RE1 — The benchmark corpus is small and legacy-generated, but recommendations are broad

Severity: **major**
File/location: `thesis/chapters/07_evaluation.tex`, lines 48–78 and 323–339; JSON metadata `results/benchmarks/thesis/thesis_results_combined.json`, lines 115–119
Problem: The final corpus is 100 scrambles and explicitly legacy-generated with adjacent same-face redundancies/cancellations allowed. The recommendations table still presents algorithm choices in broad use-case terms.
Why it matters: The corpus compares algorithms on requested scramble length, not uniformly sampled exact-depth states or hard instances.
Exact fix: Scope every recommendation to “this fixed legacy corpus under these resource limits,” or rerun a larger controlled corpus with no redundant adjacent faces and exact-depth/hard-instance strata.
Verification: Check that Chapter 7 recommendation text and table captions explicitly mention corpus limitations.

### RE2 — Timing experiment lacks repetitions, confidence intervals, and cold/warm separation

Severity: **medium**
File/location: `thesis/chapters/07_evaluation.tex`, lines 10–20, 112–116, and 164–168; JSON metadata `results/benchmarks/thesis/thesis_results_combined.json`, lines 24–26
Problem: Solver instances are reused, first timed calls include lazy loading, and results appear to be single-run observations per scramble rather than repeated measurements with uncertainty estimates.
Why it matters: Mean runtime comparisons are sensitive to one-time initialization, order effects, and platform noise.
Exact fix: Add repeated runs, randomized solver order, cold-start/warm-start separation, and bootstrap confidence intervals or at least standard errors.
Verification: Export repeated-timing metadata and update Chapter 7 tables to include uncertainty or explicitly state single-run limitations.

### RE3 — Memory conclusions rely on shared-process RSS delta, not isolated peak memory

Severity: **medium**
File/location: `thesis/chapters/07_evaluation.tex`, lines 108, 134, and 351–352; code `src/evaluation/algorithm_comparison.py`, lines 321, 354, 387, 427, 460, and 511
Problem: Memory is measured as before/after RSS delta inside a reused shared process.
Why it matters: RSS delta can miss peak memory and can be distorted by allocator reuse, lazy caches, and prior solver runs.
Exact fix: Measure each solver in an isolated subprocess and record peak RSS, or demote memory results to qualitative observations only.
Verification: Run the benchmark with isolated subprocess memory sampling and compare peak RSS values against current deltas.

### RE4 — Canonical native exact validation cannot be rerun from the source ZIP alone

Severity: **major**
File/location: `data/README.md`, lines 36–48; `results/validation/native_exact/MANIFEST.json`, lines 4–12 and 64–72; `src/korf/native_coordinate_heuristic.py`, lines 218–229
Problem: The canonical validation claim depends on `data/pattern_databases/corner_db.pkl`, which is intentionally excluded from the source ZIP. Running `python scripts/verification/native_exact_validation.py --preset canonical` fails hard without it.
Why it matters: The artifact preserves JSON evidence, but the strongest native-exact validation cannot be independently rerun from the uploaded ZIP without generating a large missing cache.
Exact fix: Either include the cache in a separate reproducibility artifact with checksum, or add a documented cache-generation time/storage estimate plus a smaller fully ZIP-contained validation preset.
Verification: From a clean extraction, run the documented canonical command; it should either complete after cache generation or clearly route through a documented prerequisite step.

## 5. Citation/reference issues

### CR1 — No missing citation keys, but bibliography contains many unused entries

Severity: **minor**
File/location: `thesis/references.bib`, lines 188–199 for unused Wikipedia entries; repository-wide citation scan found 63 BibTeX keys and 31 cited keys
Problem: The `.bib` file contains 32 unused entries, including `wiki_rubiks` and `wiki_optimal`. They are not cited in the thesis source.
Why it matters: Unused references clutter the bibliography source and increase the chance that weak/non-academic sources accidentally enter the final bibliography if `\nocite{*}` or style changes are introduced.
Exact fix: Remove unused references from `references.bib` or move them to `docs/notes/` as research notes.
Verification: Run a citation-key scan and confirm unused entries are intentional or removed.

### CR2 — Recent arXiv references lack full machine-readable arXiv metadata

Severity: **minor**
File/location: `thesis/references.bib`, lines 216–228 and 231–240
Problem: Recent arXiv/preprint references are stored mostly as `@article` entries with arXiv identifiers in `note` or `journal`, but without consistent `eprint`, `archivePrefix`, `primaryClass`, `url`, and `urldate` fields.
Why it matters: Academic references are more traceable and style-stable when preprints have structured arXiv metadata.
Exact fix: Convert arXiv entries to consistent BibTeX with `eprint`, `archivePrefix = {arXiv}`, `primaryClass`, `url`, and `urldate`.
Verification: Rebuild the bibliography and confirm arXiv entries render consistently.

## 6. Reproducibility/setup issues

### RS1 — Python dependency lock is not a reproducibility lock

Severity: **medium**
File/location: `README.md`, lines 41–44; `requirements.lock`, lines 1–60
Problem: The README correctly admits `requirements.lock` has no hashes, platform markers, Python ABI constraints, TeX/Tectonic versions, or Node/npm versions.
Why it matters: Exact reproduction can drift across platforms and package indexes, especially for native dependencies and thesis build tooling.
Exact fix: Add a hash-locked Python environment (`pip-tools --generate-hashes`, `uv.lock`, or equivalent), pin Node/npm via `.nvmrc`/`volta`, and pin TeX/Docker image versions.
Verification: Recreate the environment on a clean machine and verify dependency versions and hashes match the lock.

### RS2 — README contradicts itself about benchmark artifacts as source of truth

Severity: **medium**
File/location: `README.md`, lines 16–18
Problem: Line 16 says benchmark outputs under `results/benchmarks/thesis/` are “not the source of truth,” while line 18 says final thesis benchmark claims should use those checked-in benchmark artifacts.
Why it matters: Reviewers need a clear provenance model: source code/manuscript are source truth, but benchmark JSON is canonical evidence for Chapter 7.
Exact fix: Reword to: “Generated PDFs are not source truth; checked-in benchmark JSON artifacts are canonical evidence for the submitted Chapter 7 results and can be regenerated with the documented script.”
Verification: README should no longer contain contradictory instructions about benchmark artifact authority.

### RS3 — Committed validation snapshot is host-specific and can mislead reviewers

Severity: **minor**
File/location: `agent_workflow/generated/validation.md`, lines 5–24
Problem: The checked-in validation snapshot is from `Alexs-Laptop.local`, Python 3.14.0, and says “No blocking issues found,” while the current audit validation reported no thesis build path.
Why it matters: The file labels itself as generated, but reviewers may still read it as current evidence.
Exact fix: Either omit generated validation snapshots from the submission ZIP or regenerate them on the final review machine immediately before packaging.
Verification: Run `python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md` in the final environment and confirm the snapshot reflects that environment.

## 7. Submission polish issues

### SP1 — README layout omits major repository directories

Severity: **minor**
File/location: `README.md`, lines 60–72
Problem: The repo layout lists `src`, `tests`, `demos`, `docs`, `papers`, `scripts`, `results`, `thesis`, and `agent_workflow`, but omits important top-level directories such as `ui/`, `webapp/`, `data/`, `docker/`, `figures/`, and `notebooks/`.
Why it matters: The README is the first reproducibility guide; missing directories make the artifact harder to navigate.
Exact fix: Update the layout block to include all major top-level directories and mark which are source, generated, optional, or presentation-only.
Verification: Compare `find . -maxdepth 1 -type d` against the README layout; every major directory should be accounted for.

### SP2 — Appendix setup command points to the default test profile that currently does not complete

Severity: **major**
File/location: `thesis/chapters/appendix_a.tex`, lines 35–39; related slow tests `tests/unit/test_thistlethwaite.py`, lines 504–558
Problem: Appendix A instructs reviewers to run `python -m pytest tests -q`, but that command did not complete in audit because long solver tests are included in the default profile.
Why it matters: The thesis’s own installation appendix should not direct reviewers to a command that fails or hangs in the submitted artifact.
Exact fix: First fix the test markers/timeouts, then keep the command; or change Appendix A to separate “fast smoke test” from “full validation.”
Verification: Execute Appendix A’s setup commands in order from a clean extraction.

## FIX_TARGETS

```json
[
  {
    "severity": "critical",
    "category": "Critical blockers",
    "file": "thesis/main.tex",
    "location": "lines 173-180; supporting placeholders in thesis/chapters/00_approval.tex lines 36-44",
    "issue": "The formal approval/signature page is excluded from main.tex and the approval page still contains placeholder committee rows and an undated examination line.",
    "why_matters": "A final university thesis submission normally requires official approval/signature front matter; the current PDF is only a review build.",
    "exact_fix": "Fill all official committee names/titles and the examination date in thesis/chapters/00_approval.tex, then include \\input{chapters/00_approval} in main.tex after the title page and before acknowledgements if required by the institution.",
    "verification_steps": [
      "Rebuild thesis/main.pdf.",
      "Inspect the front matter and confirm the approval page appears.",
      "Confirm there are no placeholder committee rows or dotted date fields."
    ]
  },
  {
    "severity": "critical",
    "category": "Critical blockers",
    "file": "tests/unit/test_thistlethwaite.py",
    "location": "lines 504-558; README.md lines 34 and 127-128; pytest.ini lines 1-7",
    "issue": "The documented default fast test command includes long pure-Thistlethwaite solver tests with no explicit max_time and did not complete during audit.",
    "why_matters": "Reviewers must be able to run the supported fast reproducibility profile without hanging or excessive runtime.",
    "exact_fix": "Mark the long tests at lines 504-558 as @pytest.mark.slow or reduce them to bounded smoke tests with explicit max_time and fewer seeds.",
    "verification_steps": [
      "Run python -m pytest tests --collect-only -q.",
      "Run python -m pytest tests -q.",
      "Run timeout 120 python -m pytest tests/unit/test_thistlethwaite.py -q and confirm it completes or excludes slow tests."
    ]
  },
  {
    "severity": "major",
    "category": "Critical blockers",
    "file": "thesis/README.md",
    "location": "lines 35-43; README.md lines 49-53 and 130-131",
    "issue": "The documented review-build command depends on host TeX/Tectonic/Docker availability; in audit, build --mode auto reported no usable build path.",
    "why_matters": "A submitted reproducibility artifact should provide a reliable way to rebuild the PDF or clearly define the required external build environment.",
    "exact_fix": "Provide a pinned and tested container build route or a complete local toolchain installation recipe for TeX/Tectonic/BibTeX, and make validation report the expected build path.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md.",
      "Run python scripts/thesis_workflow.py build --mode auto.",
      "Confirm thesis/main.pdf is rebuilt successfully."
    ]
  },
  {
    "severity": "medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex",
    "location": "English lines 14-24 and 31-35; Greek lines 14-26 and 33-37",
    "issue": "The abstracts contain too much repository-status and backend implementation detail, making them read like changelogs rather than academic abstracts.",
    "why_matters": "The abstract should be concise, thesis-level, and accessible to examiners without requiring implementation-history context.",
    "exact_fix": "Move detailed backend/corpus/cache caveats into Chapters 7-8 and keep the abstracts focused on problem, methods, main quantitative results, and contribution.",
    "verification_steps": [
      "Read both abstracts without opening the repository.",
      "Confirm each abstract states problem, method, result, and contribution in concise academic prose."
    ]
  },
  {
    "severity": "major",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/08_implementation.tex",
    "location": "line 222",
    "issue": "The thesis claims 291 collected tests, but the current ZIP reports 287 active tests out of 297 collected with 10 deselected.",
    "why_matters": "This is a direct, reproducible inconsistency between the manuscript and current repository state.",
    "exact_fix": "Replace the fixed number with the current collect result or avoid hard-coded counts and instruct readers to regenerate the count with pytest --collect-only.",
    "verification_steps": [
      "Run python -m pytest tests --collect-only -q.",
      "Update the manuscript to match the reported count or remove the fixed number."
    ]
  },
  {
    "severity": "medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex; thesis/chapters/09_conclusions.tex",
    "location": "English abstract line 35; Greek abstract line 37; conclusions line 97",
    "issue": "The manuscript uses complete/comprehensive test-suite language that is stronger than the runnable artifact supports.",
    "why_matters": "The default tests did not complete in audit and canonical native validation requires a missing generated cache.",
    "exact_fix": "Use 'extensive test suite' and explicitly distinguish fast, slow, external, and cache-building validation profiles.",
    "verification_steps": [
      "Search the thesis for 'complete', 'comprehensive', 'πλήρη', and 'ολοκληρωμένο' near test-suite claims.",
      "Confirm the wording no longer implies all validation is immediately runnable from the source ZIP."
    ]
  },
  {
    "severity": "minor",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex",
    "location": "English line 31; Greek line 33; generator in scripts/verification/native_exact_validation.py lines 88-122",
    "issue": "The validation corpus is described as 3,501 states up to depth 3, but the generator excludes the solved root state and includes only successor states.",
    "why_matters": "Exact-depth validation counts should be mathematically unambiguous.",
    "exact_fix": "Rephrase as '3,501 non-solved states at depths 1-3' or include the solved state and update the count accordingly.",
    "verification_steps": [
      "Run a small script to evaluate len(generate_exhaustive_corpus(3)).",
      "Confirm the thesis wording matches the generator convention."
    ]
  },
  {
    "severity": "medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/09_conclusions.tex",
    "location": "line 172; supporting limitations in thesis/chapters/07_evaluation.tex lines 343-352",
    "issue": "The final conclusion states Kociemba is the practical-applications choice without enough immediate scoping to the fixed corpus and measured environment.",
    "why_matters": "The experiments are single-machine and limited to a 100-scramble legacy corpus.",
    "exact_fix": "Qualify the sentence to the measured corpus, timeouts, backend choices, and platform.",
    "verification_steps": [
      "Search for broad recommendation statements in Chapters 7 and 9.",
      "Confirm all are scoped to the benchmark corpus and environment."
    ]
  },
  {
    "severity": "minor",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 64-72; actual JSON fields in results/benchmarks/thesis/thesis_results_combined.json lines 133-208",
    "issue": "The benchmark schema is described conceptually but does not list the exact JSON field names used for reproduction.",
    "why_matters": "Readers should be able to map manuscript claims directly to machine-readable artifacts.",
    "exact_fix": "Add a schema table listing fields such as solved, time_seconds, solution_length, memory_mb, nodes_explored, backend, optimal_guaranteed, and verified_scramble_depth.",
    "verification_steps": [
      "Compare the schema table against thesis_results_combined.json.",
      "Confirm every Chapter 7 metric maps to a named JSON field."
    ]
  },
  {
    "severity": "major",
    "category": "Technical/code issues",
    "file": "ui/pages/2_Comparison.py",
    "location": "lines 235-244; None-producing sources in src/evaluation/algorithm_comparison.py lines 332-344 and 404-416",
    "issue": "The Streamlit comparison table formats memory_mb with :.2f even when failed Thistlethwaite/Kociemba results set memory_mb to None.",
    "why_matters": "A solver failure can crash the UI instead of rendering a failure row.",
    "exact_fix": "Add a safe memory formatter that returns 'N/A' for None and use it in solved and failed branches.",
    "verification_steps": [
      "Force a no_solution result for Thistlethwaite or Kociemba.",
      "Open the Streamlit comparison page.",
      "Confirm the table renders without TypeError."
    ]
  },
  {
    "severity": "medium",
    "category": "Technical/code issues",
    "file": "src/evaluation/algorithm_comparison.py",
    "location": "lines 323-330, 389-400, and 462-479",
    "issue": "Benchmark timing uses time.time() instead of a monotonic high-resolution timer.",
    "why_matters": "Wall-clock adjustments can corrupt elapsed-time measurements.",
    "exact_fix": "Replace timing pairs with time.perf_counter() or time.perf_counter_ns() and record the timing source in exported metadata.",
    "verification_steps": [
      "Search for time.time() in benchmark timing paths.",
      "Run benchmark unit tests and confirm exported metadata records the new timing method."
    ]
  },
  {
    "severity": "medium",
    "category": "Technical/code issues",
    "file": "webapp/tests/smoke.test.mjs",
    "location": "lines 8-37",
    "issue": "The Next.js tests only check file existence and regex strings rather than executing cube or solver-preview logic.",
    "why_matters": "The app can build while core demo behavior is broken.",
    "exact_fix": "Add executable tests for applyMoves, inverseMoves, isSolved, solveCube, timeout behavior, and comparison aggregation.",
    "verification_steps": [
      "Run cd webapp && npm test.",
      "Temporarily break inverseMoves or solveCube and confirm tests fail."
    ]
  },
  {
    "severity": "minor",
    "category": "Technical/code issues",
    "file": "src/kociemba/solver.py",
    "location": "line 18",
    "issue": "The docstring says Kociemba is typically under 19 moves, which conflicts with thesis benchmark discussion reporting about 20-22 moves at deeper requested lengths.",
    "why_matters": "Source documentation should be consistent with submitted experimental results.",
    "exact_fix": "Reword the docstring to state near-optimal behavior and reference the thesis corpus range instead of an unsupported <19 claim.",
    "verification_steps": [
      "Search the repository for '<19'.",
      "Confirm no unsupported Kociemba move-count claim remains."
    ]
  },
  {
    "severity": "minor",
    "category": "Technical/code issues",
    "file": "src/korf/optimal_solver.py",
    "location": "lines 1-24 and 82-99",
    "issue": "The module docstring overstates implementation ownership and includes stale broad performance estimates while the class delegates to an optional external RubikOptimal backend.",
    "why_matters": "The thesis carefully distinguishes native exact solving from the external exact benchmark backend; code documentation should do the same.",
    "exact_fix": "Rewrite the docstring as an external-backend wrapper description and remove or qualify the runtime estimates.",
    "verification_steps": [
      "Read the docstring and constructor together.",
      "Confirm both describe the same external-backend wrapper behavior."
    ]
  },
  {
    "severity": "minor",
    "category": "Technical/code issues",
    "file": "ui/pages/1_Single_Solver.py",
    "location": "lines 138-143",
    "issue": "The custom move parser catches all exceptions with a bare except.",
    "why_matters": "Unexpected programming errors are hidden as invalid user moves.",
    "exact_fix": "Catch only the invalid-move exception or validate moves against a legal move set before applying them.",
    "verification_steps": [
      "Inject a non-input-related failure in apply_move.",
      "Confirm the UI does not silently treat it as invalid input."
    ]
  },
  {
    "severity": "minor",
    "category": "Technical/code issues",
    "file": "pyproject.toml",
    "location": "lines 12-13",
    "issue": "The installable Python package is effectively named src, and code imports modules as src.*.",
    "why_matters": "A package literally named src is nonstandard and can confuse installed usage or conflict with other projects.",
    "exact_fix": "Rename the import package to a project-specific name such as rubik_cube_thesis or use a conventional src/packagename layout.",
    "verification_steps": [
      "Install the project in a clean virtualenv.",
      "Confirm imports use the project package name rather than src."
    ]
  },
  {
    "severity": "major",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 48-78 and 323-339; JSON metadata in results/benchmarks/thesis/thesis_results_combined.json lines 115-119",
    "issue": "The benchmark corpus is small and legacy-generated with redundant/canceling adjacent same-face moves allowed, but recommendations are presented in broad use-case terms.",
    "why_matters": "The corpus evaluates requested scramble length, not uniformly sampled exact-depth states or deliberately hard instances.",
    "exact_fix": "Scope all recommendations to the fixed legacy corpus and measured resource limits, or rerun a larger controlled corpus with exact-depth/hard-instance strata.",
    "verification_steps": [
      "Inspect Chapter 7 recommendations and captions.",
      "Confirm they mention fixed corpus, requested-length semantics, and resource limits."
    ]
  },
  {
    "severity": "medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 10-20, 112-116, and 164-168; JSON metadata lines 24-26",
    "issue": "Timing results are single-run, batch-amortized measurements without repetitions, confidence intervals, or cold/warm separation.",
    "why_matters": "Runtime comparisons can be distorted by lazy loading, solver order, and platform noise.",
    "exact_fix": "Add repeated runs, randomized order, cold-start/warm-start separation, and uncertainty estimates such as bootstrap confidence intervals.",
    "verification_steps": [
      "Run a repeated benchmark protocol.",
      "Confirm exported results include repetition count and uncertainty metrics."
    ]
  },
  {
    "severity": "medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 108, 134, and 351-352; code in src/evaluation/algorithm_comparison.py lines 321, 354, 387, 427, 460, and 511",
    "issue": "Memory results use shared-process RSS before/after deltas rather than isolated peak memory.",
    "why_matters": "RSS deltas can miss peak memory and are affected by allocator reuse and prior solver runs.",
    "exact_fix": "Measure each solver in an isolated subprocess and record peak RSS, or treat memory results as qualitative only.",
    "verification_steps": [
      "Implement isolated subprocess memory sampling.",
      "Compare peak-RSS results with existing delta measurements."
    ]
  },
  {
    "severity": "major",
    "category": "Research/experimental issues",
    "file": "data/README.md",
    "location": "lines 36-48; MANIFEST support in results/validation/native_exact/MANIFEST.json lines 4-12 and 64-72",
    "issue": "Canonical native exact validation requires data/pattern_databases/corner_db.pkl, which is intentionally absent from the source ZIP.",
    "why_matters": "The preserved JSON evidence exists, but the strongest native-exact validation cannot be rerun from the uploaded ZIP alone.",
    "exact_fix": "Ship the cache as a separate artifact with checksum or provide a fully documented cache-generation route plus a smaller ZIP-contained validation preset.",
    "verification_steps": [
      "From a clean extraction, run python scripts/verification/native_exact_validation.py --preset canonical --output-dir results/validation/native_exact.",
      "Confirm the command completes or clearly performs the documented cache generation first."
    ]
  },
  {
    "severity": "minor",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "lines 188-199; repository-wide citation scan found 63 BibTeX keys and 31 cited keys",
    "issue": "The bibliography contains 32 unused entries, including unused Wikipedia entries.",
    "why_matters": "Unused weak references clutter the bibliography source and may accidentally enter the final bibliography if citation style changes.",
    "exact_fix": "Remove unused references from references.bib or move them to docs/notes as research notes.",
    "verification_steps": [
      "Run a citation-key scan over thesis/chapters/*.tex and thesis/references.bib.",
      "Confirm unused entries are removed or intentionally documented."
    ]
  },
  {
    "severity": "minor",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "lines 216-228 and 231-240",
    "issue": "Recent arXiv/preprint entries lack consistent machine-readable arXiv metadata.",
    "why_matters": "Structured arXiv metadata improves traceability and bibliography style stability.",
    "exact_fix": "Add eprint, archivePrefix, primaryClass, url, and urldate fields to arXiv/preprint entries.",
    "verification_steps": [
      "Rebuild the bibliography.",
      "Confirm arXiv references render consistently and remain traceable."
    ]
  },
  {
    "severity": "medium",
    "category": "Reproducibility/setup issues",
    "file": "README.md",
    "location": "lines 41-44; requirements.lock lines 1-60",
    "issue": "requirements.lock is explicitly not a cryptographic or platform-complete reproducibility lock.",
    "why_matters": "Dependency resolution can drift across machines and package indexes.",
    "exact_fix": "Add hash-locked Python dependencies, pin Node/npm versions, and pin TeX/Docker build tooling.",
    "verification_steps": [
      "Create a clean environment from the lock.",
      "Verify package versions and hashes match the declared lock."
    ]
  },
  {
    "severity": "medium",
    "category": "Reproducibility/setup issues",
    "file": "README.md",
    "location": "lines 16-18",
    "issue": "The README says benchmark outputs are not the source of truth, then immediately says final benchmark claims should use the checked-in benchmark artifacts.",
    "why_matters": "Reviewers need a clear provenance model for manuscript source, generated PDF, and canonical benchmark evidence.",
    "exact_fix": "Clarify that source code/manuscript are source truth, while checked-in benchmark JSON is canonical evidence for Chapter 7 results and can be regenerated.",
    "verification_steps": [
      "Re-read README lines 16-18.",
      "Confirm there is no contradiction about benchmark artifact authority."
    ]
  },
  {
    "severity": "minor",
    "category": "Reproducibility/setup issues",
    "file": "agent_workflow/generated/validation.md",
    "location": "lines 5-24",
    "issue": "The committed validation snapshot is host-specific and says no blocking issues, but a current audit validation found no ready thesis build path.",
    "why_matters": "Generated validation snapshots can mislead reviewers if not regenerated on the final build machine.",
    "exact_fix": "Regenerate validation.md immediately before packaging or exclude generated workflow snapshots from the submission ZIP.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md.",
      "Confirm the file reflects the final review environment."
    ]
  },
  {
    "severity": "minor",
    "category": "Submission polish issues",
    "file": "README.md",
    "location": "lines 60-72",
    "issue": "The repository layout omits major directories such as ui, webapp, data, docker, figures, and notebooks.",
    "why_matters": "The README is the first navigation aid for examiners and reproducibility reviewers.",
    "exact_fix": "Update the layout block to include all major top-level directories and mark whether they are source, generated, optional, or presentation-only.",
    "verification_steps": [
      "Run find . -maxdepth 1 -type d on a clean extraction.",
      "Confirm each major directory appears in the README layout."
    ]
  },
  {
    "severity": "major",
    "category": "Submission polish issues",
    "file": "thesis/chapters/appendix_a.tex",
    "location": "lines 35-39; related long tests in tests/unit/test_thistlethwaite.py lines 504-558",
    "issue": "Appendix A instructs reviewers to run python -m pytest tests -q, but that default command did not complete during audit.",
    "why_matters": "The thesis installation appendix should provide commands that reviewers can actually run from the submitted ZIP.",
    "exact_fix": "Fix the default test profile by marking/bounding long tests, or split Appendix A into fast smoke-test and full validation commands.",
    "verification_steps": [
      "Follow Appendix A setup commands from a clean extraction.",
      "Confirm every listed command completes as documented."
    ]
  }
]
```

Overall thesis quality score: **78/100**
Technical quality score: **74/100**
Submission readiness score: **52/100**
