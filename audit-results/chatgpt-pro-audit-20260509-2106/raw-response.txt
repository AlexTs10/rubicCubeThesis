## Audit basis

I audited the extracted uploaded ZIP only. I did not use GitHub or any external repository. I verified these executable checks in the extracted repository:

`python -m pytest tests -q` → **286 passed, 1 skipped, 28 deselected**.
`python scripts/verify_notebooks.py` → all 6 notebooks passed structural verification.
`python scripts/verification/native_exact_validation.py --preset source-zip` → **261 cases, 0 failures**.
`python scripts/thesis_workflow.py validate` and `python scripts/thesis_workflow.py build --mode auto` failed in this audit environment because no usable thesis build path was available: `bibtex`, `tectonic`, Docker CLI, and Docker daemon were unavailable.

---

# 1. Critical blockers

### 1.1 Critical — Approval/signature page is not final-submission ready

**File:** `thesis/chapters/00_approval.tex`
**Location:** lines 33–36, 42–44, 50
**Problem:** The approval page explicitly states that two committee members and the examination date are still to be filled from the Secretariat record. Lines 43–44 contain placeholder committee-member text, and line 50 contains `\dotfill` for the examination date.
**Why it matters:** This is an administrative blocker for a final signed institutional thesis copy. The repository README also acknowledges this as not yet finalized.
**Exact fix recommendation:** Replace the two placeholder committee entries with official names/titles and replace `\dotfill` with the official examination date, or replace the whole page with the institutionally signed approval page.
**Verification steps:** Search the final source and PDF for `Ονοματεπώνυμο μέλους επιτροπής`, `\dotfill`, and missing date placeholders; rebuild the PDF and confirm the approval page contains the official committee and date.

### 1.2 Critical — Thesis cannot be independently rebuilt in the audited environment

**File:** `thesis/README.md`; `scripts/thesis_workflow.py`; `thesis/main.tex`
**Location:** `thesis/README.md` lines 32–42 and 67–71; `scripts/thesis_workflow.py` lines 878–888 and 1044–1062; `thesis/main.tex` lines 220–223
**Problem:** The documented build path requires a TeX/BibTeX/Tectonic/Docker path. In this audit environment, `python scripts/thesis_workflow.py validate` failed because `bibtex`, `tectonic`, Docker CLI, and Docker daemon were unavailable, and `build --mode auto` exited with “No usable build path found.”
**Why it matters:** The checked-in PDF is inspectable, but the source package is not self-contained for independent PDF reproduction unless the reviewer has the required host toolchain or a running Docker environment. For submission/review reproducibility, this is a serious gap.
**Exact fix recommendation:** Add a CI-validated reproducible thesis build path, preferably a pinned container build that can be invoked without relying on host TeX state, and include a successful build log/artifact hash. Alternatively, document exact host package installation commands and verify `build --mode auto` in a clean review environment.
**Verification steps:** From a clean machine/container, run `python scripts/thesis_workflow.py validate` and `python scripts/thesis_workflow.py build --mode auto`; confirm both exit 0 and regenerate `thesis/main.pdf`.

### 1.3 High — Canonical native validation is not reproducible from the source ZIP alone, and documentation understates one prerequisite

**File:** `data/README.md`; `results/validation/native_exact/README.md`; `scripts/verification/native_exact_validation.py`
**Location:** `data/README.md` lines 36–68; `results/validation/native_exact/README.md` lines 25–30; `scripts/verification/native_exact_validation.py` lines 26–37, 248–267, 465–477
**Problem:** Documentation correctly says the canonical native exact validation requires `data/pattern_databases/corner_db.pkl`, but the script also requires an external optimal oracle for 12 oracle-dependent validation cases. Running the canonical preset in the audited source-only environment failed with the script’s own prerequisite error for the external oracle.
**Why it matters:** The thesis cites the 3,513-case canonical native-validation corpus. The smaller source-ZIP smoke check passes, but it is not equivalent to the canonical evidence. Reviewers need both prerequisites stated explicitly.
**Exact fix recommendation:** Update `data/README.md`, `results/validation/native_exact/README.md`, Appendix A, and the CLI help text to state that canonical validation requires both the generated/supplied corner DB and the optional `RubikOptimal` oracle backend. Provide either a companion artifact recipe or a one-command prerequisite check listing both missing items.
**Verification steps:** In a clean source-ZIP environment, run `python scripts/verification/native_exact_validation.py --preset canonical`; verify the failure message lists both missing prerequisites when absent. Then install/provide both and verify the canonical run reproduces the checked-in canonical report.

---

# 2. Thesis writing issues

### 2.1 Medium — Abstract and conclusion overstate the external-backend pytest profile

**File:** `thesis/chapters/00_abstract_en.tex`; `thesis/chapters/00_abstract_gr.tex`; `thesis/chapters/09_conclusions.tex`; `pytest.ini`; `tests/integration/test_native_exact_oracle_agreement.py`
**Location:** `00_abstract_en.tex` lines 31–34; `00_abstract_gr.tex` lines 31–34; `09_conclusions.tex` lines 89–98; `pytest.ini` lines 1–7; `test_native_exact_oracle_agreement.py` lines 19–23
**Problem:** The thesis says the implementation has separate fast, slow, external-backend, and cache-building validation profiles. `pytest.ini` defines an `external` marker, but the external-oracle agreement test is only guarded by `skipif`; it is not marked `external`. Running `python -m pytest tests -q -m external` selected zero tests and exited with code 5.
**Why it matters:** This is a mismatch between thesis prose, test configuration, and actual test discoverability.
**Exact fix recommendation:** Add `pytestmark = pytest.mark.external` or `@pytest.mark.external` to the external-oracle agreement test, and document the required `RUN_NATIVE_ORACLE_TESTS=1` environment variable. Alternatively, revise the thesis wording to say the external-oracle check is an opt-in environment-gated integration test rather than a pytest marker profile.
**Verification steps:** Run `python -m pytest tests -q -m external`; it should collect the external test and either run it when prerequisites are present or skip it explicitly when prerequisites are absent, without selecting zero tests.

### 2.2 Medium — Appendix B RubikCube code snippet is stale relative to actual implementation

**File:** `thesis/chapters/appendix_b.tex`; `src/cube/rubik_cube.py`
**Location:** `appendix_b.tex` lines 8–28; `rubik_cube.py` lines 67–93
**Problem:** Appendix B shows a simplified constructor without structural validation, optional legal-state validation, type normalization, or scramble metadata. The actual implementation includes `validate_legal`, `_validate_state`, `_validate_legal_state`, and `_scramble_*` metadata.
**Why it matters:** The appendix is presented as representative implementation code. As written, it under-represents important correctness and reproducibility features in the actual class.
**Exact fix recommendation:** Either update the snippet to match `src/cube/rubik_cube.py` lines 67–93, or explicitly label the listing as “simplified excerpt; validation and scramble metadata omitted.”
**Verification steps:** Compare Appendix B listing against the actual constructor and confirm the discrepancy is removed or clearly disclosed.

### 2.3 Medium — Appendix B overstates admissibility of the IDA* bound

**File:** `thesis/chapters/appendix_b.tex`; `src/korf/a_star.py`
**Location:** `appendix_b.tex` line 34; `a_star.py` lines 4–8
**Problem:** Appendix B says the IDA* bound is initialized from an “admissible heuristic estimate.” The implementation’s own A* module states optimality is guaranteed only when the supplied heuristic is proven admissible, and lightweight demo heuristics do not provide that guarantee.
**Why it matters:** This wording can mislead readers into thinking every heuristic used by the educational IDA*/A* paths is admissible.
**Exact fix recommendation:** Change the sentence to: “The bound is initialized from the configured heuristic estimate; optimality claims require the supplied heuristic to be a proven admissible lower bound.”
**Verification steps:** Search Appendix B for “admissible heuristic estimate” and confirm the revised wording aligns with `src/korf/a_star.py`.

### 2.4 Low — Appendix A contains ambiguous/nonexistent bare paths for benchmark depth files

**File:** `thesis/chapters/appendix_a.tex`
**Location:** lines 159–166
**Problem:** The first per-depth benchmark path is written with the full directory, but the following entries are written as `thesis_bench_d10.json`, `thesis_bench_d15.json`, and `thesis_bench_d20.json` without the `results/benchmarks/thesis/` prefix.
**Why it matters:** A reviewer following the appendix literally may look for files in the wrong location.
**Exact fix recommendation:** Rewrite all four entries as full paths under `results/benchmarks/thesis/`.
**Verification steps:** Confirm every path listed in Appendix A exists relative to the repository root.

### 2.5 Low — Appendix A says the repository uses Tectonic, but the documented workflow is broader

**File:** `thesis/chapters/appendix_a.tex`; `thesis/README.md`
**Location:** `appendix_a.tex` line 174; `thesis/README.md` lines 32–42
**Problem:** Appendix A says, “Στο αποθετήριο χρησιμοποιείται `tectonic`.” The current thesis README says the preferred review build is `python scripts/thesis_workflow.py build --mode auto`, preferring `latexmk -xelatex`, then manual XeLaTeX + bibliography, then Tectonic, then Docker.
**Why it matters:** The appendix gives an outdated or overly narrow description of the build workflow.
**Exact fix recommendation:** Replace the line with a description of the auto workflow and its fallback order.
**Verification steps:** Confirm Appendix A and `thesis/README.md` describe the same build path.

### 2.6 Low — Subjective academic tone in Chapter 7 summary

**File:** `thesis/chapters/07_evaluation.tex`
**Location:** lines 405–408
**Problem:** The phrase “αποδίδει εντυπωσιακά καλά” is promotional/subjective.
**Why it matters:** Academic conclusions should use neutral, evidence-based phrasing.
**Exact fix recommendation:** Replace with a quantitative formulation, e.g., “ολοκληρώνει όλες τις περιπτώσεις έως ζητούμενο μήκος 15, ενώ στο ζητούμενο μήκος 20 εμφανίζει 3 timeout αποτυχίες.”
**Verification steps:** Search for “εντυπωσιακά” and confirm the wording is neutralized.

---

# 3. Technical/code issues

### 3.1 Medium — No coverage threshold; several substantial modules have 0% or very low coverage

**File:** `pytest.ini`; multiple `src/` modules
**Location:** `pytest.ini` lines 1–7; coverage report from `python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered`
**Problem:** The default tests pass, but coverage is only **50% total**. Major modules have 0% coverage: `src/cube/visualization.py`, `src/evaluation/statistics.py`, `src/evaluation/validation.py`, and `src/evaluation/visualizations.py`. Important solver-support modules are also low, including `src/kociemba/pruning.py` at 12%, `src/kociemba/moves.py` at 21%, `src/korf/corner_database.py` at 19%, and `src/thistlethwaite/tables.py` at 29%. There is no coverage threshold in `pytest.ini`.
**Why it matters:** The thesis makes strong implementation and reproducibility claims; passing tests alone do not exercise large parts of the benchmark/statistics/visualization and solver-support code.
**Exact fix recommendation:** Add tests for evaluation/statistics/visualization generation and low-level solver tables/pruning logic. Add a conservative threshold first, e.g. `--cov-fail-under=65`, then raise it as coverage improves.
**Verification steps:** Run `python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered`; confirm the new tests cover previously untested modules and the configured threshold passes.

### 3.2 Medium — `verify_setup.py` suggests a non-hash install command that conflicts with README

**File:** `verify_setup.py`; `README.md`
**Location:** `verify_setup.py` lines 146–190, especially line 188; `README.md` lines 28–45
**Problem:** README instructs installation with `python -m pip install --require-hashes -r requirements.lock`, but `verify_setup.py` tells users to run `pip install -r requirements.lock` when packages are missing.
**Why it matters:** This weakens the hash-locked reproducibility story and may lead reviewers to install a non-verified environment.
**Exact fix recommendation:** Change the error message to `python -m pip install --require-hashes -r requirements.lock`, and optionally mention the editable install command from README.
**Verification steps:** Trigger a missing-package check and confirm the printed remediation command includes `--require-hashes`.

### 3.3 Low — External exact backend wrapper prints a misleading solver banner

**File:** `src/korf/optimal_solver.py`
**Location:** lines 221–246
**Problem:** The verbose banner says “KORF'S OPTIMAL SOLVER (IDA* with Pattern Databases)” even though the file-level docstring correctly says this module wraps an optional external `RubikOptimal` backend.
**Why it matters:** Logs/demos can mislead readers into thinking the repository directly implements the heavy Korf optimal solver used in the benchmark. The thesis itself is more careful than this runtime banner.
**Exact fix recommendation:** Change the banner to “External RubikOptimal exact backend wrapper” and include backend package/version/provenance in verbose stats.
**Verification steps:** Run a verbose solve with the backend available and confirm the printed header clearly identifies the external backend.

### 3.4 Low — Stale “For now, simplified check” comment in Thistlethwaite phase goal check

**File:** `src/thistlethwaite/solver.py`
**Location:** lines 324–332
**Problem:** The code comments say “For now, simplified check” immediately before the phase-1 goal predicate.
**Why it matters:** Even if the predicate is intended and tested, this stale comment undermines confidence in the corrected Thistlethwaite implementation.
**Exact fix recommendation:** Replace the comment with a precise explanation of what `get_e_slice_coord() == 0` means, or add an assertion/test documenting the phase invariant.
**Verification steps:** Search for “For now, simplified check”; confirm it is removed or replaced by exact invariant documentation.

### 3.5 Low — Kociemba solver docstring has malformed indentation

**File:** `src/kociemba/solver.py`
**Location:** lines 306–315
**Problem:** The `timeout:` argument line is not indented consistently under `Args`, making `verbose` appear nested under `timeout`.
**Why it matters:** This is a documentation-quality defect in a core solver API.
**Exact fix recommendation:** Align `timeout:` with `cube:`, `max_phase1_depth:`, `max_phase2_depth:`, and `verbose:`.
**Verification steps:** Run a docstring linter or manually inspect the `solve()` docstring.

### 3.6 Low — Visualization CLI prints stale chapter recommendations

**File:** `src/evaluation/visualizations.py`
**Location:** lines 428–448
**Problem:** The CLI output recommends figures for “Chapter 5” and “Chapter 6,” while the benchmark evaluation is Chapter 7 in the thesis.
**Why it matters:** This is confusing for maintainers regenerating thesis figures.
**Exact fix recommendation:** Update the printed chapter references to the current thesis chapter structure, or remove hard-coded chapter numbers.
**Verification steps:** Run `python -m src.evaluation.visualizations <results_file.json>` and confirm the printed guidance references the current chapter structure.

---

# 4. Research/experimental issues

### 4.1 High — Benchmark statistics are single-run, batch-amortized observations without confidence intervals

**File:** `thesis/chapters/07_evaluation.tex`; `results/benchmarks/thesis/thesis_results_combined.json`
**Location:** `07_evaluation.tex` lines 125–136 and 380–395; JSON metadata lines 24–26 and 120–145
**Problem:** The thesis correctly discloses that the artifact has no repeated runs, confidence intervals, or separate cold/warm measurements. Metadata also records reused solver instances and no benchmark warm start.
**Why it matters:** The reported runtime means are useful for this fixed artifact but weak for general performance claims.
**Exact fix recommendation:** Add a secondary benchmark artifact with repeated runs per scramble, explicit warmup policy, confidence intervals, and isolated cold-start versus warm-start timing. If not added, keep all performance language strictly limited to the fixed corpus and platform.
**Verification steps:** Regenerate benchmark JSON with fields such as `repeat_id`, `warmup_policy`, `cold_start`, `confidence_interval`, and per-run samples; verify Chapter 7 tables/figures use or explicitly exclude those fields.

### 4.2 Medium — Legacy benchmark corpus contains redundant adjacent same-face moves

**File:** `results/benchmarks/thesis/thesis_results_combined.json`; `thesis/chapters/07_evaluation.tex`
**Location:** JSON lines 115–119 and first example lines 162–169; `07_evaluation.tex` lines 88–90
**Problem:** The benchmark metadata says the corpus was generated with `legacy_random_all_moves_redundant_allowed`, and the thesis discloses that requested scramble length is not verified depth. I counted 78 of 100 rows with adjacent same-face moves; the first row includes `F ... F' F` style redundancy.
**Why it matters:** The corpus is valid as a fixed comparison corpus, but it is weaker evidence for claims by true optimal depth or uniformly sampled states.
**Exact fix recommendation:** Add a secondary non-redundant benchmark corpus generated with `random_no_consecutive_same_face_moves`, or report redundancy counts and group results by verified optimal depth rather than only requested length.
**Verification steps:** Regenerate or add a corpus whose metadata states no adjacent same-face moves; programmatically verify no adjacent moves share the same face, and update Chapter 7 tables accordingly.

### 4.3 Medium — `scramble_id` is reused across depths in the combined benchmark JSON

**File:** `results/benchmarks/thesis/thesis_results_combined.json`; `thesis/chapters/07_evaluation.tex`
**Location:** JSON lines 162, 2345, 5249, 8759 show repeated `"scramble_id": 0`; `07_evaluation.tex` line 75
**Problem:** `scramble_id` is not globally unique in the combined JSON; it repeats for each requested depth. The thesis schema table lists `scramble_id, requested_scramble_length` together, but the JSON lacks a single globally unique `case_id`.
**Why it matters:** Downstream analysis can accidentally join or group by `scramble_id` alone and mix cases across depths.
**Exact fix recommendation:** Add a `case_id` such as `d5_000`, `d10_000`, etc., to every combined-row record, or rename `scramble_id` to `scramble_id_within_depth` and update docs.
**Verification steps:** Validate uniqueness with a script checking `case_id` uniqueness across the 100 combined rows; update Chapter 7 schema to document it.

### 4.4 Medium — Official reproduction commands omit figure regeneration

**File:** `thesis/chapters/appendix_a.tex`; `src/evaluation/visualizations.py`
**Location:** `appendix_a.tex` lines 98–114; `visualizations.py` lines 113–167 and 428–440
**Problem:** Appendix A’s reproduction sequence regenerates benchmark JSON and LaTeX tables, but does not include the command to regenerate the thesis figures. The visualization module has a CLI and generates `fig1`–`fig7`, but the official appendix workflow does not call it.
**Why it matters:** Figures are part of the thesis results; reproducibility should include their regeneration path, not only table generation.
**Exact fix recommendation:** Add an Appendix A command such as `python -m src.evaluation.visualizations results/benchmarks/thesis/thesis_results_combined.json thesis/figures`.
**Verification steps:** Run the documented command from a clean checkout and confirm `thesis/figures/fig1_...png` through `fig7_...png` are regenerated.

---

# 5. Citation/reference issues

### 5.1 Medium — Foundational Thistlethwaite citation is a secondary historical webpage but is keyed as if it were the 1981 source

**File:** `thesis/references.bib`; thesis chapters citing `thistlethwaite1981`
**Location:** `references.bib` lines 25–30
**Problem:** The bibliography entry `thistlethwaite1981` is authored by Jaap Scherphuis and explicitly described as a historical summary of Thistlethwaite’s algorithm, not a primary Thistlethwaite publication.
**Why it matters:** A reviewer may object that a foundational algorithm is cited through a secondary webpage while the key name and thesis prose imply a 1981 primary source.
**Exact fix recommendation:** Rename the key to reflect the actual source, e.g. `scherphuis_thistlethwaite_summary`, and in the thesis text write “as summarized by Scherphuis” where appropriate. Add a primary or stronger historical source if available.
**Verification steps:** Run `python scripts/thesis_workflow.py status` after citation-key changes and confirm missing citation keys remain 0.

---

# 6. Reproducibility/setup issues

### 6.1 High — Documented external pytest marker profile is empty

**File:** `pytest.ini`; `tests/integration/test_native_exact_oracle_agreement.py`; `README.md`; `thesis/chapters/appendix_a.tex`
**Location:** `pytest.ini` lines 1–7; `test_native_exact_oracle_agreement.py` lines 19–23; `README.md` lines 58 and 152–154; `appendix_a.tex` lines 46–50
**Problem:** The repository documents an opt-in `external` pytest profile, but `python -m pytest tests -q -m external` selected zero tests and exited with code 5.
**Why it matters:** Reviewers following the documented command cannot validate the external-backend test profile.
**Exact fix recommendation:** Mark the external-oracle test with `@pytest.mark.external` and keep the environment/backend skip guard.
**Verification steps:** Run `python -m pytest tests -q -m external`; confirm at least one test is collected and either passes or skips for a stated prerequisite.

### 6.2 Medium — Benchmark runtime artifact lacks full original runtime lock metadata

**File:** `results/benchmarks/thesis/thesis_results_combined.json`; `thesis/chapters/07_evaluation.tex`
**Location:** JSON lines 120–145 and 147–158; `07_evaluation.tex` lines 132–136
**Problem:** The JSON states that package/environment metadata were added post hoc and that the original benchmark did not record full hardware/package metadata, wheel hash, or upstream commit hash for the external backend.
**Why it matters:** This limits exact replayability of the benchmark run, especially for the external optimal backend.
**Exact fix recommendation:** Update the benchmark runner to write full package lock metadata, backend wheel hash, upstream commit or immutable artifact identifier where available, OS/kernel details, CPU governor if relevant, and command-line arguments at run time.
**Verification steps:** Regenerate benchmark JSON and verify these fields are present as original run metadata, not post-hoc notes.

### 6.3 Medium — Source-ZIP native smoke validation is much smaller than the canonical claim

**File:** `scripts/verification/native_exact_validation.py`; `results/validation/native_exact/README.md`; `thesis/chapters/00_abstract_en.tex`
**Location:** `native_exact_validation.py` lines 26–38 and 397–404; `results/validation/native_exact/README.md` lines 25–45; `00_abstract_en.tex` lines 36–42
**Problem:** The source-ZIP preset is described as a smaller contained smoke check and passes 261 cases, while the thesis claim concerns a 3,513-case canonical corpus. This distinction is present but easy to miss in the abstract-level reproducibility prose.
**Why it matters:** A reviewer may run the source-ZIP smoke preset and mistakenly believe it reproduces the full canonical native-validation evidence.
**Exact fix recommendation:** Add a short table in Appendix A separating “source-contained smoke validation: 261 cases” from “canonical validation: 3,513 cases, requires corner DB + external oracle.”
**Verification steps:** Run both commands in a prepared environment and confirm the reported case counts match the table.

---

# 7. Submission polish issues

### 7.1 Low — README says review-ready, but the formal approval page is still a template

**File:** `README.md`; `thesis/README.md`; `thesis/chapters/00_approval.tex`
**Location:** `README.md` line 8; `thesis/README.md` line 3; `00_approval.tex` lines 33–50
**Problem:** The README correctly discloses the issue, but “review-ready” sits beside a non-final approval page.
**Why it matters:** For a final submission package, this should be resolved or more prominently marked as “review draft, not final signed copy.”
**Exact fix recommendation:** Until the signed page is inserted, rename the status to “review draft” or “technical review-ready; administrative signature page pending.”
**Verification steps:** Confirm README and thesis front matter use consistent final/draft status wording.

---

# FIX_TARGETS

```json
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "thesis/chapters/00_approval.tex",
    "location": "lines 33-36, 42-44, 50",
    "issue": "Approval/signature page is not final-submission ready: two committee-member placeholders remain and the examination date is still a dotfill placeholder.",
    "exact_fix": "Replace both placeholder committee rows with official committee names/titles and replace the examination-date dotfill with the official date, or replace the page with the institutionally signed approval page.",
    "verification_steps": "Search the final sources and PDF for 'Ονοματεπώνυμο μέλους επιτροπής', '\\dotfill', and missing date placeholders; rebuild the PDF and confirm the approval page contains the official committee and date."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "thesis/README.md; scripts/thesis_workflow.py; thesis/main.tex",
    "location": "thesis/README.md lines 32-42 and 67-71; scripts/thesis_workflow.py lines 878-888 and 1044-1062; thesis/main.tex lines 220-223",
    "issue": "The thesis could not be independently rebuilt in the audited environment. The documented build path requires a usable TeX/BibTeX/Tectonic/Docker path, and validation/build failed because no such path was available.",
    "exact_fix": "Add a CI-validated reproducible build path, preferably a pinned container build, and include a successful build log/artifact hash; otherwise document exact host package installation and verify build --mode auto in a clean environment.",
    "verification_steps": "From a clean machine/container, run 'python scripts/thesis_workflow.py validate' and 'python scripts/thesis_workflow.py build --mode auto'; both should exit 0 and regenerate thesis/main.pdf."
  },
  {
    "severity": "High",
    "category": "Critical blockers",
    "file": "data/README.md; results/validation/native_exact/README.md; scripts/verification/native_exact_validation.py",
    "location": "data/README.md lines 36-68; results/validation/native_exact/README.md lines 25-30; scripts/verification/native_exact_validation.py lines 26-37, 248-267, 465-477",
    "issue": "Canonical native validation is not reproducible from the source ZIP alone and documentation understates that it requires both the corner_db.pkl cache and an external optimal oracle.",
    "exact_fix": "Update data/README.md, results/validation/native_exact/README.md, Appendix A, and CLI help to state that canonical validation requires both data/pattern_databases/corner_db.pkl and the optional RubikOptimal oracle backend.",
    "verification_steps": "Run 'python scripts/verification/native_exact_validation.py --preset canonical' without prerequisites and confirm the failure lists both missing prerequisites; then provide both prerequisites and confirm the canonical run reproduces the checked-in report."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex; thesis/chapters/09_conclusions.tex; pytest.ini; tests/integration/test_native_exact_oracle_agreement.py",
    "location": "00_abstract_en.tex lines 31-34; 00_abstract_gr.tex lines 31-34; 09_conclusions.tex lines 89-98; pytest.ini lines 1-7; test_native_exact_oracle_agreement.py lines 19-23",
    "issue": "The thesis says there is an external-backend validation profile, but the external pytest marker profile selects zero tests because the oracle-agreement test is not marked external.",
    "exact_fix": "Add pytest.mark.external to the external-oracle agreement test and document RUN_NATIVE_ORACLE_TESTS=1, or revise thesis wording to describe it as an environment-gated integration test rather than a marker profile.",
    "verification_steps": "Run 'python -m pytest tests -q -m external'; it should collect the external test and either run it when prerequisites exist or skip it explicitly."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/appendix_b.tex; src/cube/rubik_cube.py",
    "location": "appendix_b.tex lines 8-28; rubik_cube.py lines 67-93",
    "issue": "Appendix B shows a stale/simplified RubikCube constructor that omits actual validation and scramble metadata features.",
    "exact_fix": "Update the listing to match src/cube/rubik_cube.py lines 67-93, or explicitly label it as a simplified excerpt with validation and metadata omitted.",
    "verification_steps": "Compare Appendix B against the actual constructor and confirm either the code matches or the omission caveat is present."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/appendix_b.tex; src/korf/a_star.py",
    "location": "appendix_b.tex line 34; src/korf/a_star.py lines 4-8",
    "issue": "Appendix B says the IDA* bound is initialized from an admissible heuristic estimate, but the implementation states optimality is guaranteed only for proven admissible heuristics.",
    "exact_fix": "Change the wording to say the bound is initialized from the configured heuristic estimate and that optimality requires a proven admissible lower bound.",
    "verification_steps": "Search Appendix B for 'admissible heuristic estimate' and confirm the revised wording aligns with src/korf/a_star.py."
  },
  {
    "severity": "Low",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/appendix_a.tex",
    "location": "lines 159-166",
    "issue": "Appendix A lists d10/d15/d20 benchmark JSON filenames without the results/benchmarks/thesis/ directory prefix.",
    "exact_fix": "Rewrite all four per-depth benchmark entries as full paths under results/benchmarks/thesis/.",
    "verification_steps": "Check that every path listed in Appendix A exists relative to the repository root."
  },
  {
    "severity": "Low",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/appendix_a.tex; thesis/README.md",
    "location": "appendix_a.tex line 174; thesis/README.md lines 32-42",
    "issue": "Appendix A says the repository uses tectonic, but the documented current build workflow is build --mode auto with latexmk/manual XeLaTeX/Tectonic/Docker fallbacks.",
    "exact_fix": "Replace the Tectonic-only statement with the actual auto workflow and fallback order.",
    "verification_steps": "Confirm Appendix A and thesis/README.md describe the same build path."
  },
  {
    "severity": "Low",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 405-408",
    "issue": "The phrase 'αποδίδει εντυπωσιακά καλά' is subjective/promotional for academic writing.",
    "exact_fix": "Replace it with a neutral quantitative statement about success through requested length 15 and three timeouts at requested length 20.",
    "verification_steps": "Search for 'εντυπωσιακά' and confirm the wording is neutralized."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "pytest.ini; src/cube/visualization.py; src/evaluation/statistics.py; src/evaluation/validation.py; src/evaluation/visualizations.py; src/kociemba/pruning.py; src/kociemba/moves.py; src/korf/corner_database.py; src/thistlethwaite/tables.py",
    "location": "pytest.ini lines 1-7; coverage report from python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered",
    "issue": "No coverage threshold is configured and total source coverage is 50%; several substantial modules have 0% or very low coverage.",
    "exact_fix": "Add tests for evaluation/statistics/visualization generation and low-level solver table/pruning logic; add a conservative cov-fail-under threshold and raise it as coverage improves.",
    "verification_steps": "Run 'python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered' and confirm the new threshold passes and previously untested modules are covered."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "verify_setup.py; README.md",
    "location": "verify_setup.py lines 146-190, especially line 188; README.md lines 28-45",
    "issue": "verify_setup.py suggests 'pip install -r requirements.lock' when packages are missing, conflicting with README's hash-locked '--require-hashes' install command.",
    "exact_fix": "Change the remediation message to 'python -m pip install --require-hashes -r requirements.lock' and optionally mention the editable install command.",
    "verification_steps": "Trigger a missing-package check and confirm the printed remediation command includes '--require-hashes'."
  },
  {
    "severity": "Low",
    "category": "Technical/code issues",
    "file": "src/korf/optimal_solver.py",
    "location": "lines 221-246",
    "issue": "The verbose banner labels the external backend wrapper as 'KORF'S OPTIMAL SOLVER (IDA* with Pattern Databases)', which can mislead users about what is implemented locally.",
    "exact_fix": "Change the banner to identify the external RubikOptimal exact backend wrapper and include backend package/version/provenance in verbose stats.",
    "verification_steps": "Run a verbose solve with the backend available and confirm the printed header identifies the external backend."
  },
  {
    "severity": "Low",
    "category": "Technical/code issues",
    "file": "src/thistlethwaite/solver.py",
    "location": "lines 324-332",
    "issue": "A stale comment says 'For now, simplified check' before a phase-1 goal predicate.",
    "exact_fix": "Replace the comment with a precise invariant explanation for get_e_slice_coord() == 0 or add a test documenting the invariant.",
    "verification_steps": "Search for 'For now, simplified check' and confirm it is removed or replaced."
  },
  {
    "severity": "Low",
    "category": "Technical/code issues",
    "file": "src/kociemba/solver.py",
    "location": "lines 306-315",
    "issue": "The solve() docstring has malformed indentation: timeout is not aligned with the other Args entries.",
    "exact_fix": "Align timeout with cube, max_phase1_depth, max_phase2_depth, and verbose under Args.",
    "verification_steps": "Inspect the docstring or run a docstring linter to confirm the Args block is correctly formatted."
  },
  {
    "severity": "Low",
    "category": "Technical/code issues",
    "file": "src/evaluation/visualizations.py",
    "location": "lines 428-448",
    "issue": "The visualization CLI prints stale recommendations for Chapter 5 and Chapter 6 although the evaluation chapter is Chapter 7.",
    "exact_fix": "Update printed chapter references to the current thesis structure or remove hard-coded chapter numbers.",
    "verification_steps": "Run 'python -m src.evaluation.visualizations <results_file.json>' and confirm printed guidance references the current chapter structure."
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "07_evaluation.tex lines 125-136 and 380-395; JSON metadata lines 24-26 and 120-145",
    "issue": "Benchmark statistics are single-run, batch-amortized observations without repetitions, confidence intervals, or separated cold/warm timings.",
    "exact_fix": "Add a secondary benchmark artifact with repeated runs per scramble, explicit warmup policy, confidence intervals, and separated cold-start versus warm-start timings; otherwise keep performance claims limited to the fixed corpus/platform.",
    "verification_steps": "Regenerate benchmark JSON with repeat_id, warmup_policy, cold_start, confidence_interval, and per-run samples; verify Chapter 7 tables/figures use or explicitly exclude these fields."
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "JSON lines 115-119 and 162-169; 07_evaluation.tex lines 88-90",
    "issue": "The legacy benchmark corpus allows adjacent same-face redundancies and cancellations; 78 of 100 rows contain adjacent same-face moves.",
    "exact_fix": "Add a secondary non-redundant benchmark corpus or report redundancy counts and analyze results by verified optimal depth rather than only requested length.",
    "verification_steps": "Regenerate or add a corpus whose metadata states no adjacent same-face moves; programmatically verify this property and update Chapter 7 tables."
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "JSON lines 162, 2345, 5249, 8759; 07_evaluation.tex line 75",
    "issue": "scramble_id is reused across depths in the combined benchmark JSON and there is no globally unique case_id.",
    "exact_fix": "Add a globally unique case_id such as d5_000/d10_000 or rename scramble_id to scramble_id_within_depth and update documentation.",
    "verification_steps": "Validate uniqueness of case_id across all 100 combined rows and update the Chapter 7 schema."
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/appendix_a.tex; src/evaluation/visualizations.py",
    "location": "appendix_a.tex lines 98-114; visualizations.py lines 113-167 and 428-440",
    "issue": "The official reproduction commands regenerate benchmark JSON and LaTeX tables but omit thesis figure regeneration.",
    "exact_fix": "Add an Appendix A command such as 'python -m src.evaluation.visualizations results/benchmarks/thesis/thesis_results_combined.json thesis/figures'.",
    "verification_steps": "Run the documented command from a clean checkout and confirm fig1 through fig7 are regenerated under thesis/figures."
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "lines 25-30",
    "issue": "The foundational Thistlethwaite citation key thistlethwaite1981 points to a Scherphuis historical webpage, not a primary Thistlethwaite publication.",
    "exact_fix": "Rename the key to reflect the actual source, e.g. scherphuis_thistlethwaite_summary, and revise thesis prose to say the algorithm is summarized by Scherphuis where appropriate; add a stronger primary/historical source if available.",
    "verification_steps": "Run 'python scripts/thesis_workflow.py status' after citation-key changes and confirm missing citation keys remain 0."
  },
  {
    "severity": "High",
    "category": "Reproducibility/setup issues",
    "file": "pytest.ini; tests/integration/test_native_exact_oracle_agreement.py; README.md; thesis/chapters/appendix_a.tex",
    "location": "pytest.ini lines 1-7; test_native_exact_oracle_agreement.py lines 19-23; README.md lines 58 and 152-154; appendix_a.tex lines 46-50",
    "issue": "The documented external pytest marker profile is empty: python -m pytest tests -q -m external selected zero tests and exited with code 5.",
    "exact_fix": "Mark the external-oracle test with pytest.mark.external while keeping the environment/backend skip guard.",
    "verification_steps": "Run 'python -m pytest tests -q -m external' and confirm at least one test is collected and either passes or skips for a stated prerequisite."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "JSON lines 120-145 and 147-158; 07_evaluation.tex lines 132-136",
    "issue": "Benchmark runtime artifact lacks full original runtime lock metadata; some environment/backend metadata were added post hoc and no upstream commit hash is recorded for the external backend.",
    "exact_fix": "Update the benchmark runner to write full package lock metadata, backend wheel hash, upstream commit or immutable artifact identifier, OS/kernel details, CPU information, and command-line arguments at run time.",
    "verification_steps": "Regenerate benchmark JSON and verify these fields are present as original run metadata, not post-hoc notes."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "scripts/verification/native_exact_validation.py; results/validation/native_exact/README.md; thesis/chapters/00_abstract_en.tex",
    "location": "native_exact_validation.py lines 26-38 and 397-404; results/validation/native_exact/README.md lines 25-45; 00_abstract_en.tex lines 36-42",
    "issue": "The source-ZIP native smoke validation is much smaller than the 3,513-case canonical native-validation claim, and this distinction should be more visible.",
    "exact_fix": "Add an Appendix A table separating source-contained smoke validation of 261 cases from canonical validation of 3,513 cases requiring corner DB plus external oracle.",
    "verification_steps": "Run both validation commands in a prepared environment and confirm the reported case counts match the table."
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "README.md; thesis/README.md; thesis/chapters/00_approval.tex",
    "location": "README.md line 8; thesis/README.md line 3; 00_approval.tex lines 33-50",
    "issue": "README says review-ready while the formal approval page is still a template with administrative fields pending.",
    "exact_fix": "Until the signed page is inserted, change status wording to 'technical review-ready; administrative signature page pending' or equivalent.",
    "verification_steps": "Confirm README, thesis/README.md, and front matter use consistent final/draft status wording."
  }
]
```

## Scores

**Overall thesis quality score:** 78/100
Strong technical transparency and improved claim discipline, but the approval page, build reproducibility, validation-prerequisite documentation, and experimental limitations still need work.

**Technical quality score:** 76/100
Default tests pass and the source-ZIP native smoke validation passes, but coverage is uneven, the external marker profile is empty, and some logs/docs still blur local implementation versus external backend.

**Submission readiness score:** 62/100
The manuscript is close to reviewable as a technical draft, but it is not final-submission ready until the approval page is completed, the thesis build is reproducible for reviewers, and the canonical validation/benchmark reproduction paths are tightened.
