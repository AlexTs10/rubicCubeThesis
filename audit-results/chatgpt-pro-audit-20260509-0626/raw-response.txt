Audit scope: extracted ZIP only. I did not use GitHub or external repositories. Static checks found no missing LaTeX citation keys and no missing thesis figure paths. The reproducibility manifest hashes matched 242/242 tracked files. Python source compilation passed. The Next.js app built and its tests passed after `npm ci`. The issues below are only issues I could locate in actual files.

## 1. Critical blockers

**CB-1 — Final institutional front matter is incomplete and excluded.**
Severity: Critical. File: `thesis/main.tex`, `thesis/chapters/00_approval.tex`, `README.md`, `thesis/README.md`. Location: `thesis/main.tex:174-180`, `thesis/chapters/00_approval.tex:36-44`, `README.md:7-8`, `thesis/README.md:3`. Problem: the approval/signature page is not included in the manuscript and still contains placeholder committee members/date. Why it matters: this is not submission-ready front matter. Exact fix: replace placeholders with official committee names/titles/date and include the approval page in `main.tex` in the institution-required position. Verification: rebuild `thesis/main.pdf` and inspect the first pages for the approval page and completed signatures/date.

**CB-2 — The documented thesis build path is not source-reproducible in the audited environment.**
Severity: Critical. File: `README.md`, `thesis/README.md`, `scripts/thesis_workflow.py`. Location: `README.md:28-38`, `thesis/README.md:39-43`, `scripts/thesis_workflow.py:482-516`, `scripts/thesis_workflow.py:1034-1052`. Problem: the documented command `python scripts/thesis_workflow.py build --mode auto` depends on local `latexmk/xelatex/bibtex`, `tectonic`, or Docker readiness; the workflow explicitly exits with “No usable build path found” if none is available. Why it matters: a thesis repository must provide a deterministic build route, not only a conditional one. Exact fix: add a pinned Docker/TeX build target or explicit install script that provides `xelatex` and `bibtex`/`tectonic`, then make `build --mode auto` pass from a clean checkout. Verification: run `python scripts/thesis_workflow.py validate --output ...` and `python scripts/thesis_workflow.py build --mode auto` on a clean machine.

**CB-3 — The claimed fast test profile still includes an unmarked heavyweight cache-building test.**
Severity: Critical. File: `tests/unit/test_native_coordinate_heuristic.py`, `src/korf/corner_database.py`, `pytest.ini`, `thesis/chapters/00_abstract_en.tex`, `thesis/chapters/08_implementation.tex`. Location: `tests/unit/test_native_coordinate_heuristic.py:122-131`, `src/korf/corner_database.py:8-16`, `src/korf/corner_database.py:266-336`, `pytest.ini:3-7`, `thesis/chapters/00_abstract_en.tex:35`, `thesis/chapters/08_implementation.tex:221-227`. Problem: `test_coordinate_heuristic_ignores_incomplete_corner_database` calls `create_corner_database(...)` but is not marked `cache_building`, while the thesis and README claim heavyweight cache-building tests are excluded by the default fast profile. Why it matters: this undermines the core reproducibility claim and can make `verify_setup.py` or default pytest runs hang or exceed practical runtime. Exact fix: mark this test with `@pytest.mark.cache_building`, or replace the real corner database generation with a tiny mocked incomplete database fixture. Verification: `python -m pytest tests --collect-only -q -m cache_building` should include this test; `python -m pytest tests/unit/test_native_coordinate_heuristic.py::test_coordinate_heuristic_ignores_incomplete_corner_database -q -m "not cache_building"` should deselect it.

**CB-4 — A native exact validation claim is stronger than the recorded evidence.**
Severity: Critical. File: `scripts/verification/native_exact_validation.py`, `results/validation/native_exact/native_exact_validation_20260322_144046.json`, `thesis/chapters/05_korf.tex`, `thesis/chapters/09_conclusions.tex`, `thesis/chapters/00_abstract_en.tex`, `thesis/chapters/00_abstract_gr.tex`. Location: `scripts/verification/native_exact_validation.py:125-167`, `scripts/verification/native_exact_validation.py:235-289`, `results/validation/native_exact/native_exact_validation_20260322_144046.json:39-70`, `thesis/chapters/05_korf.tex:73-79`, `thesis/chapters/09_conclusions.tex:52-61`, `thesis/chapters/00_abstract_en.tex:31`, `thesis/chapters/00_abstract_gr.tex:33`. Problem: the thesis states the remaining timeout is an “edge-dominated depth-8” case, but the JSON failure has `"oracle_stats": null`, and the validation script skips oracle verification when the native solver times out. For random oracle samples, the script labels `expected_depth=depth` from generated scramble length, not from an oracle-first exact distance. Why it matters: the “depth-8” and “edge-dominated” interpretation is not fully supported by the stored validation record. Exact fix: run the oracle independently for every oracle-sample case, including native timeouts, record `oracle_length` and `oracle_stats`, and compare native length against oracle length rather than generated scramble length. Verification: rerun the canonical validation and confirm every failure entry has oracle evidence or is explicitly labelled as unverified-depth.

## 2. Thesis writing issues

**TW-1 — Greek academic tone is inconsistent because of untranslated English technical phrases.**
Severity: Minor. File: `thesis/chapters/00_abstract_gr.tex`, `thesis/chapters/07_evaluation.tex`, `thesis/chapters/08_implementation.tex`. Location: `thesis/chapters/00_abstract_gr.tex:14`, `thesis/chapters/00_abstract_gr.tex:21-23`, `thesis/chapters/00_abstract_gr.tex:37`, `thesis/chapters/07_evaluation.tex:321`, `thesis/chapters/08_implementation.tex:217`. Problem: phrases such as “exact solver”, “benchmark”, “profile”, “cache-building tests”, “Use case”, “synthetic preview”, and “authoritative benchmark evidence” appear without consistent Greek translation or first-use definitions. Why it matters: the thesis reads partly like repository documentation rather than polished Greek academic prose. Exact fix: translate recurring terms or define them once in parentheses; replace `Use case` with `Περίπτωση χρήσης`; replace marketing-style English phrases with Greek academic equivalents. Verification: search the thesis for those terms and confirm each is either translated or deliberately defined.

**TW-2 — Chapter 7 contains revision-history language that should not appear in the final thesis.**
Severity: Major. File: `thesis/chapters/07_evaluation.tex`. Location: `thesis/chapters/07_evaluation.tex:125-133`, `thesis/chapters/07_evaluation.tex:217-224`, `thesis/chapters/07_evaluation.tex:345-347`. Problem: phrases such as “Μετά τη διόρθωση”, “παλαιότερη, λανθασμένη εικόνα”, and “αρχική, λανθασμένη εκδοχή” describe the correction process rather than the final result. Why it matters: final academic text should present validated findings, not expose internal debugging history unless placed in a methods appendix. Exact fix: rewrite these paragraphs as neutral final-result statements and move correction history, if needed, to an appendix or reproducibility note. Verification: `rg -n "διόρθωση|λανθασμένη|παλαιότερη|αρχική" thesis/chapters/07_evaluation.tex` should no longer return final-chapter process language.

## 3. Technical/code issues

**TC-1 — `ValidationDataset.generate_random_scrambles(seed=...)` is not reproducible.**
Severity: Major. File: `src/korf/validation.py`, `src/cube/rubik_cube.py`. Location: `src/korf/validation.py:68-94`, `src/cube/rubik_cube.py:258-299`. Problem: `generate_random_scrambles` calls `np.random.seed(seed)` but then calls `cube.scramble(..., seed=None)`, and `RubikCube.scramble` creates a new `PCG64(seed)` generator from `None`. Why it matters: the validation dataset API advertises a seed but does not produce deterministic datasets. Exact fix: create a local RNG from the provided seed and pass deterministic per-scramble seeds into `cube.scramble`; store the generated move sequences. Verification: generate two datasets with the same seed and assert identical `cube.state_key()` sequences.

**TC-2 — `ValidationDataset.save_to_file` destroys the dataset on round-trip.**
Severity: Major. File: `src/korf/validation.py`. Location: `src/korf/validation.py:96-152`. Problem: `load_from_file` expects `positions` entries with `moves` and `distance`, but `save_to_file` writes only `count`, an empty `positions` list, and a note. Why it matters: saved validation datasets cannot be reloaded, so persistence is misleading and unusable for reproducible validation. Exact fix: serialize either the scramble move sequence or a full cube-state encoding plus distance for every position. Add a save-load equality test. Verification: save a dataset with two positions, reload it, and assert same length, distances, and cube states.

**TC-3 — `load_cube20_data` is advertised but unimplemented and silently returns an empty dataset.**
Severity: Major. File: `src/korf/validation.py`. Location: `src/korf/validation.py:1-12`, `src/korf/validation.py:354-396`. Problem: the module advertises “Load validation data from cube20.org,” but the function prints that the parser is not implemented and returns an empty `ValidationDataset`. Why it matters: callers can believe external optimal-distance validation has loaded when in fact no positions were loaded. Exact fix: either implement the parser with tests or raise `NotImplementedError` instead of returning an empty dataset. Verification: provide a small valid fixture and assert it loads nonzero positions, or assert unsupported formats fail loudly.

**TC-4 — Public Kociemba timeout does not include lazy table initialization.**
Severity: Major. File: `src/kociemba/solver.py`. Location: `src/kociemba/solver.py:118-135`, `src/kociemba/solver.py:353-360`. Problem: `solve(..., timeout=...)` calls `_initialize()` before setting `start_time`, so first-run table loading/generation is outside the solver’s internal timeout. Why it matters: users may assume the timeout bounds the entire solve call, but cold-start latency can exceed it. Exact fix: start the timer before `_initialize()` or explicitly split `initialize()` from `solve()` and document that timeout is warm-search only. Verification: remove caches, run `solve(timeout=1)`, and confirm either the call is bounded or the API explicitly reports initialization time separately.

**TC-5 — Reusing one `AlgorithmComparison` object contaminates later batches.**
Severity: Minor. File: `src/evaluation/algorithm_comparison.py`. Location: `src/evaluation/algorithm_comparison.py:167`, `src/evaluation/algorithm_comparison.py:571-583`. Problem: `self.results` is initialized once in `__init__` and `run_batch_test` appends to it without clearing. Why it matters: running two batches on the same object returns/export aggregates from both, which can silently corrupt benchmark summaries. Exact fix: clear `self.results` at the start of `run_batch_test`, or add an explicit `append=False` parameter. Verification: run two one-scramble batches on the same object and assert the second result length is one unless append mode is requested.

**TC-6 — Thistlethwaite cache loaders accept pickle payloads without schema/shape validation.**
Severity: Major. File: `src/thistlethwaite/tables.py`. Location: `src/thistlethwaite/tables.py:120-124`, `src/thistlethwaite/tables.py:320-330`. Problem: cached pattern tables are loaded directly with `pickle.load` and assigned to the table without validating type, length, schema version, or expected coordinate count. Why it matters: stale or corrupt generated caches can silently poison solver correctness. Exact fix: store cache metadata with schema version, table size, phase name, move set, and checksum; reject payloads whose length/type does not match `db.size`. Verification: write an invalid pickle to a cache path and confirm the loader rejects it instead of accepting it.

## 4. Research/experimental issues

**RE-1 — The canonical benchmark corpus is legacy and allows redundant scrambles.**
Severity: Major. File: `results/benchmarks/thesis/thesis_results_combined.json`, `thesis/chapters/07_evaluation.tex`. Location: `results/benchmarks/thesis/thesis_results_combined.json:115-119`, `results/benchmarks/thesis/thesis_results_combined.json:123-131`, `thesis/chapters/07_evaluation.tex:75-77`, `thesis/chapters/07_evaluation.tex:331-340`. Problem: the benchmark metadata states `legacy_random_all_moves_redundant_allowed`; the thesis admits requested scramble length is not exact optimal depth. Why it matters: conclusions by “depth” are actually conclusions by requested generation length on a legacy corpus. Exact fix: regenerate a clean corpus with no consecutive same-face moves and, ideally, oracle-verified exact-depth buckets; report legacy and clean results separately. Verification: inspect metadata for `allow_redundant=false` or equivalent and verify exact-depth distribution with the optimal backend.

**RE-2 — Main evaluation tables omit robust uncertainty/statistical summaries.**
Severity: Major. File: `thesis/chapters/07_evaluation.tex`. Location: `thesis/chapters/07_evaluation.tex:112-117`, `thesis/chapters/07_evaluation.tex:226-239`. Problem: the chapter’s main tables report means and explicitly says a stricter future run should add medians, standard deviation/IQR, confidence intervals, and timeout-aware summaries. Why it matters: runtime distributions are highly skewed, and timeout-heavy solver comparisons need robust summaries. Exact fix: add median, IQR, standard deviation, bootstrap confidence intervals, and timeout-count columns to the main tables or supplementary tables. Verification: rerun the analysis script and confirm those metrics are present in generated tables and thesis text.

**RE-3 — Memory measurements are too coarse for strong resource claims.**
Severity: Major. File: `src/evaluation/algorithm_comparison.py`, `thesis/chapters/07_evaluation.tex`. Location: `src/evaluation/algorithm_comparison.py:76-78`, `src/evaluation/algorithm_comparison.py:243-250`, `thesis/chapters/07_evaluation.tex:108-119`, `thesis/chapters/07_evaluation.tex:337-340`. Problem: memory is measured as process RSS delta in a shared sequential process with reused solver instances. Why it matters: this cannot support isolated peak-memory claims per solver. Exact fix: run each solver/case in a separate child process, record peak RSS, separate cold-start and warm-start memory, and update `memory_method`. Verification: regenerated JSON should state an isolated peak-RSS method and include per-solver peak values.

**RE-4 — Canonical native validation cannot be reproduced from the source ZIP alone without a missing large cache.**
Severity: Major. File: `data/README.md`, `results/validation/native_exact/MANIFEST.json`, `scripts/verification/native_exact_validation.py`. Location: `data/README.md:28-37`, `results/validation/native_exact/MANIFEST.json:5-12`, `results/validation/native_exact/MANIFEST.json:24-27`, `scripts/verification/native_exact_validation.py:26-37`, `scripts/verification/native_exact_validation.py:382-392`. Problem: the canonical native validation requires `data/pattern_databases/corner_db.pkl`, but the source ZIP omits generated `.pkl` cache files. Why it matters: the checked-in native exact claim is not fully rerunnable from the archive without a separate expensive/generated artifact. Exact fix: provide a documented cache-generation target with expected runtime and hash, or distribute the required cache as a separately verifiable artifact. Verification: from a fresh extraction, either the canonical validation command succeeds end-to-end or fails with a clear documented prerequisite and reproducible cache-build command.

## 5. Citation/reference issues

**CR-1 — Foundational Thistlethwaite claims rely on a secondary webpage as if it were a primary source.**
Severity: Major. File: `thesis/references.bib`, `thesis/chapters/03_thistlethwaite.tex`, `thesis/chapters/02_background.tex`. Location: `thesis/references.bib:25-30`, `thesis/chapters/03_thistlethwaite.tex:8-16`, `thesis/chapters/02_background.tex:160`, `thesis/chapters/02_background.tex:237`. Problem: bibliography key `thistlethwaite1981` is authored by Jaap Scherphuis and described as a historical summary, but it supports core historical and mathematical statements about Thistlethwaite. Why it matters: foundational algorithm claims should use primary or clearly identified secondary sources. Exact fix: replace or supplement this with the strongest primary/historical source available; if only the secondary source is available, state that explicitly in the citation note and thesis wording. Verification: bibliography and chapter citations distinguish primary algorithm source from secondary explanatory source.

**CR-2 — The bibliography contains many uncited entries.**
Severity: Minor. File: `thesis/references.bib`. Location: `thesis/references.bib:188-199`, `thesis/references.bib:231-249`. Problem: static citation analysis found 63 bibliography keys, 31 cited keys, and 32 uncited keys; examples include the Wikipedia entries and several recent ML/GNN papers. Why it matters: uncited bibliography entries dilute the reference list and can look like padding. Exact fix: remove uncited entries or cite them in an appropriate related-work/future-work section. Verification: run a cite-key comparison script and confirm uncited count is zero or intentionally documented.

**CR-3 — Citation-content verification is not possible from the ZIP alone because source PDFs are excluded.**
Severity: Major. File: `papers/DOWNLOAD_SUMMARY.txt`, `REPRODUCIBILITY_MANIFEST.json`, `README.md`. Location: `papers/DOWNLOAD_SUMMARY.txt:13-16`, `papers/DOWNLOAD_SUMMARY.txt:31-39`, `papers/DOWNLOAD_SUMMARY.txt:54-64`, `papers/DOWNLOAD_SUMMARY.txt:110-116`, `REPRODUCIBILITY_MANIFEST.json:2-6`, `README.md:61-62`. Problem: the ZIP contains bibliography metadata and an acquisition log, but not the cited PDFs; the log also records incomplete acquisition coverage. Why it matters: from the submitted ZIP alone, an auditor can verify citation keys but not whether every cited claim is supported by source text. Exact fix: add a claim-to-reference evidence table with page/section pointers and public DOI/URL fields, or provide a separate permitted evidence bundle. Verification: randomly sample cited claims and confirm each has a source locator that can be checked without private/local files.

## 6. Reproducibility/setup issues

**RS-1 — `verify_setup.py --full` does not actually override pytest’s default marker exclusions.**
Severity: Major. File: `verify_setup.py`, `pytest.ini`, `pyproject.toml`. Location: `verify_setup.py:341-349`, `verify_setup.py:451-456`, `pytest.ini:3-7`, `pyproject.toml:15-22`. Problem: the “full” command is `python -m pytest tests -q`, but pytest still applies configured `addopts = -m "not slow and not external and not cache_building"`. Why it matters: `--full` is advertised as including slow/cache-building tests but silently remains filtered. Exact fix: for full mode, call pytest with `-o addopts=` and an explicit marker expression, or clear `PYTEST_ADDOPTS`; document whether external tests are included. Verification: `python verify_setup.py --full` should collect/run the 9 tests normally deselected by the default profile.

**RS-2 — Setup verification checks `requirements.txt`, not the pinned `requirements.lock`.**
Severity: Major. File: `README.md`, `verify_setup.py`, `requirements.txt`, `requirements.lock`. Location: `README.md:28-33`, `README.md:41-45`, `verify_setup.py:138-164`, `requirements.txt:1-42`, `requirements.lock:1-18`. Problem: README tells users to install `requirements.lock`, but `verify_setup.py` reads `requirements.txt` and tells users to install `requirements.txt` if packages are missing. Why it matters: verification is not checking the pinned audited dependency set. Exact fix: make `verify_setup.py` default to `requirements.lock`, add a `--requirements` option if needed, and update the missing-package message. Verification: run `python verify_setup.py` and confirm it reports the lock file path and pinned versions.

**RS-3 — Python dependency locking is explicitly non-cryptographic and omits platform/toolchain versions.**
Severity: Major. File: `README.md`, `requirements.lock`. Location: `README.md:41-45`, `requirements.lock:1-18`, `requirements.lock:117-143`. Problem: the repository acknowledges `requirements.lock` has no hashes, Python ABI constraints, TeX/Tectonic versions, or Node/npm versions. Why it matters: dependency resolution can drift or differ by platform even with pinned package versions. Exact fix: use a hash-verified lock mechanism such as `uv.lock` or `pip-tools --generate-hashes`; pin TeX/Docker image versions and Node/npm versions. Verification: fresh install with hash checking succeeds, and build/test commands record exact tool versions.

## 7. Submission polish issues

**SP-1 — Historical audit material remains in the submitted docs tree.**
Severity: Minor. File: `docs/THESIS_FULL_AUDIT_2026-03-21.md`. Location: `docs/THESIS_FULL_AUDIT_2026-03-21.md:1-7`, `docs/THESIS_FULL_AUDIT_2026-03-21.md:28-34`, `docs/THESIS_FULL_AUDIT_2026-03-21.md:492-509`. Problem: the repository includes an old audit report with unresolved historical findings and open questions. It is labelled historical, but it still appears under `docs/`. Why it matters: final submission packages should not foreground stale internal QA material unless clearly archived. Exact fix: move it to an `archive/` or `audit-history/` directory, or remove it from the submission ZIP while retaining it internally. Verification: final archive either excludes the historical audit or marks it clearly as non-submission archival material.

## FIX_TARGETS

```json
[
  {
    "severity": "critical",
    "category": "Critical blocker",
    "file": "thesis/main.tex; thesis/chapters/00_approval.tex; README.md; thesis/README.md",
    "location": "thesis/main.tex:174-180; thesis/chapters/00_approval.tex:36-44; README.md:7-8; thesis/README.md:3",
    "issue": "The formal approval/signature page is excluded from the manuscript and still contains placeholder committee members/date.",
    "why_it_matters": "The thesis is not institutionally submission-ready without completed and included approval front matter.",
    "exact_fix": "Fill in official committee names, titles, signatures/date in 00_approval.tex and include the approval page in main.tex at the required front-matter position.",
    "verification_steps": [
      "Run rg -n \"00_approval|Μέλος Εξεταστικής|Ημερομηνία εξέτασης\" thesis/main.tex thesis/chapters/00_approval.tex.",
      "Rebuild thesis/main.pdf.",
      "Inspect the PDF front matter and confirm the approval page is present and complete."
    ]
  },
  {
    "severity": "critical",
    "category": "Reproducibility/setup issue",
    "file": "README.md; thesis/README.md; scripts/thesis_workflow.py",
    "location": "README.md:28-38; thesis/README.md:39-43; scripts/thesis_workflow.py:482-516; scripts/thesis_workflow.py:1034-1052",
    "issue": "The documented thesis build path depends on a locally available TeX/Tectonic/Docker path and exits if none is ready.",
    "why_it_matters": "A thesis archive needs a deterministic build route from clean checkout to PDF.",
    "exact_fix": "Add a pinned Docker/TeX build target or explicit install script that provides xelatex and bibtex/tectonic, then make build --mode auto pass from a clean environment.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py validate --output /tmp/validation.md.",
      "Run python scripts/thesis_workflow.py build --mode auto.",
      "Confirm thesis/main.pdf is regenerated without manual toolchain guessing."
    ]
  },
  {
    "severity": "critical",
    "category": "Reproducibility/setup issue",
    "file": "tests/unit/test_native_coordinate_heuristic.py; src/korf/corner_database.py; pytest.ini; thesis/chapters/00_abstract_en.tex; thesis/chapters/08_implementation.tex",
    "location": "tests/unit/test_native_coordinate_heuristic.py:122-131; src/korf/corner_database.py:8-16; src/korf/corner_database.py:266-336; pytest.ini:3-7; thesis/chapters/00_abstract_en.tex:35; thesis/chapters/08_implementation.tex:221-227",
    "issue": "A heavyweight corner database generation test is unmarked, contradicting the claim that the default fast profile excludes cache-building tests.",
    "why_it_matters": "The default reproducibility profile can run unexpectedly expensive cache generation.",
    "exact_fix": "Mark test_coordinate_heuristic_ignores_incomplete_corner_database with @pytest.mark.cache_building or replace real database generation with a tiny mocked incomplete fixture.",
    "verification_steps": [
      "Run python -m pytest tests --collect-only -q -m cache_building and confirm the test is collected.",
      "Run python -m pytest tests/unit/test_native_coordinate_heuristic.py::test_coordinate_heuristic_ignores_incomplete_corner_database -q -m \"not cache_building\" and confirm it is deselected."
    ]
  },
  {
    "severity": "critical",
    "category": "Research/experimental issue",
    "file": "scripts/verification/native_exact_validation.py; results/validation/native_exact/native_exact_validation_20260322_144046.json; thesis/chapters/05_korf.tex; thesis/chapters/09_conclusions.tex; thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex",
    "location": "scripts/verification/native_exact_validation.py:125-167; scripts/verification/native_exact_validation.py:235-289; results/validation/native_exact/native_exact_validation_20260322_144046.json:39-70; thesis/chapters/05_korf.tex:73-79; thesis/chapters/09_conclusions.tex:52-61; thesis/chapters/00_abstract_en.tex:31; thesis/chapters/00_abstract_gr.tex:33",
    "issue": "The thesis claims the remaining native timeout is an edge-dominated depth-8 case, but the failure record has oracle_stats null and the validation script skips oracle verification on native timeout.",
    "why_it_matters": "The exact depth and interpretation of the failure are not fully supported by the stored evidence.",
    "exact_fix": "Run the oracle independently for every oracle-sample case, including native timeouts, record oracle_length/oracle_stats, and compare native length against oracle length rather than generated scramble length.",
    "verification_steps": [
      "Rerun python scripts/verification/native_exact_validation.py --preset canonical --output-dir results/validation/native_exact after providing required caches.",
      "Inspect every failure entry and confirm oracle_stats and oracle_length are present or the failure is labelled unverified-depth.",
      "Update thesis claims if oracle evidence changes the depth or interpretation."
    ]
  },
  {
    "severity": "minor",
    "category": "Thesis writing issue",
    "file": "thesis/chapters/00_abstract_gr.tex; thesis/chapters/07_evaluation.tex; thesis/chapters/08_implementation.tex",
    "location": "thesis/chapters/00_abstract_gr.tex:14; thesis/chapters/00_abstract_gr.tex:21-23; thesis/chapters/00_abstract_gr.tex:37; thesis/chapters/07_evaluation.tex:321; thesis/chapters/08_implementation.tex:217",
    "issue": "The Greek thesis text mixes untranslated English repository jargon with academic prose.",
    "why_it_matters": "The manuscript reads less polished and less academically consistent.",
    "exact_fix": "Translate recurring terms or define them once in parentheses; replace Use case with Περίπτωση χρήσης and rewrite synthetic preview/live telemetry/authoritative evidence in Greek academic style.",
    "verification_steps": [
      "Run rg -n \"Use case|synthetic preview|live solver telemetry|authoritative|profile|cache-building|exact solver\" thesis/chapters.",
      "Confirm remaining English terms are either standard technical terms or first-use definitions."
    ]
  },
  {
    "severity": "major",
    "category": "Thesis writing issue",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "thesis/chapters/07_evaluation.tex:125-133; thesis/chapters/07_evaluation.tex:217-224; thesis/chapters/07_evaluation.tex:345-347",
    "issue": "Chapter 7 contains revision-history language such as corrected, older wrong picture, and initial wrong version.",
    "why_it_matters": "Final thesis chapters should present validated results, not internal correction history.",
    "exact_fix": "Rewrite the passages as neutral final findings and move correction history to an appendix only if needed.",
    "verification_steps": [
      "Run rg -n \"διόρθωση|λανθασμένη|παλαιότερη|αρχική\" thesis/chapters/07_evaluation.tex.",
      "Confirm no final-result paragraph uses debugging or revision-history language."
    ]
  },
  {
    "severity": "major",
    "category": "Technical/code issue",
    "file": "src/korf/validation.py; src/cube/rubik_cube.py",
    "location": "src/korf/validation.py:68-94; src/cube/rubik_cube.py:258-299",
    "issue": "ValidationDataset.generate_random_scrambles accepts a seed but passes seed=None to RubikCube.scramble, making generated datasets non-deterministic.",
    "why_it_matters": "Seeded validation data cannot be reproduced reliably.",
    "exact_fix": "Use a local RNG seeded by the method argument and pass deterministic per-case seeds into cube.scramble; store generated move sequences.",
    "verification_steps": [
      "Generate two ValidationDataset instances with the same seed.",
      "Compare [cube.state_key() for cube, _ in dataset] across both runs.",
      "Assert the lists are identical."
    ]
  },
  {
    "severity": "major",
    "category": "Technical/code issue",
    "file": "src/korf/validation.py",
    "location": "src/korf/validation.py:96-152",
    "issue": "ValidationDataset.save_to_file writes an empty positions array even though load_from_file expects positions with moves and distance.",
    "why_it_matters": "Validation datasets cannot round-trip and saved validation artifacts are misleading.",
    "exact_fix": "Serialize every position with move sequence or facelet state plus distance, and add a save/load round-trip test.",
    "verification_steps": [
      "Create a dataset with at least two positions.",
      "Save it and reload it.",
      "Assert equal length, distances, and cube.state_key values."
    ]
  },
  {
    "severity": "major",
    "category": "Technical/code issue",
    "file": "src/korf/validation.py",
    "location": "src/korf/validation.py:1-12; src/korf/validation.py:354-396",
    "issue": "load_cube20_data is advertised as a feature but the parser is not implemented and returns an empty dataset for existing files.",
    "why_it_matters": "A caller can believe external optimal-distance data was loaded when no validation cases were loaded.",
    "exact_fix": "Implement cube20 parsing with fixtures or raise NotImplementedError instead of returning an empty ValidationDataset.",
    "verification_steps": [
      "Create a small valid cube20-format fixture.",
      "Run load_cube20_data on it.",
      "Assert the dataset length is nonzero, or assert unsupported formats fail loudly."
    ]
  },
  {
    "severity": "major",
    "category": "Technical/code issue",
    "file": "src/kociemba/solver.py",
    "location": "src/kociemba/solver.py:118-135; src/kociemba/solver.py:353-360",
    "issue": "KociembaSolver.solve starts its internal timeout clock after lazy table initialization.",
    "why_it_matters": "The timeout parameter does not bound cold-start solve latency.",
    "exact_fix": "Start timing before _initialize or split initialization into an explicit warmup API and document timeout semantics.",
    "verification_steps": [
      "Remove generated kociemba caches.",
      "Call solve(timeout=1) on a scramble.",
      "Confirm the call is bounded by the timeout policy or reports initialization time separately."
    ]
  },
  {
    "severity": "minor",
    "category": "Technical/code issue",
    "file": "src/evaluation/algorithm_comparison.py",
    "location": "src/evaluation/algorithm_comparison.py:167; src/evaluation/algorithm_comparison.py:571-583",
    "issue": "AlgorithmComparison.run_batch_test appends to self.results without clearing previous batch results.",
    "why_it_matters": "Repeated batch runs on the same object can contaminate summaries and exports.",
    "exact_fix": "Clear self.results at the start of run_batch_test or add an explicit append parameter defaulting to false.",
    "verification_steps": [
      "Run run_batch_test(n_scrambles=1) twice on the same object.",
      "Assert the second returned result list has length 1 unless append mode is explicitly enabled."
    ]
  },
  {
    "severity": "major",
    "category": "Technical/code issue",
    "file": "src/thistlethwaite/tables.py",
    "location": "src/thistlethwaite/tables.py:120-124; src/thistlethwaite/tables.py:320-330",
    "issue": "Thistlethwaite cached tables are loaded from pickle without validating schema, type, or expected size.",
    "why_it_matters": "Stale or corrupt generated cache files can silently affect solver correctness.",
    "exact_fix": "Store and validate schema version, table name, expected size, move set, and checksum before accepting cached tables.",
    "verification_steps": [
      "Write an invalid pickle payload to a cache path.",
      "Run the loader.",
      "Confirm it rejects the payload with a clear error."
    ]
  },
  {
    "severity": "major",
    "category": "Research/experimental issue",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "results/benchmarks/thesis/thesis_results_combined.json:115-119; results/benchmarks/thesis/thesis_results_combined.json:123-131; thesis/chapters/07_evaluation.tex:75-77; thesis/chapters/07_evaluation.tex:331-340",
    "issue": "The canonical benchmark corpus is legacy_random_all_moves_redundant_allowed, so requested scramble length is not exact optimal depth.",
    "why_it_matters": "Depth-based conclusions are weaker because they refer to generation length, not guaranteed search depth.",
    "exact_fix": "Regenerate and report a clean corpus with no redundant same-face moves and oracle-verified exact-depth buckets; keep legacy results only as historical comparison.",
    "verification_steps": [
      "Inspect benchmark metadata for scramble_generation and redundancy policy.",
      "Verify exact-depth distribution using the optimal backend.",
      "Update thesis tables to label requested length versus verified depth."
    ]
  },
  {
    "severity": "major",
    "category": "Research/experimental issue",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "thesis/chapters/07_evaluation.tex:112-117; thesis/chapters/07_evaluation.tex:226-239",
    "issue": "Main evaluation tables rely on means and defer median, standard deviation/IQR, confidence intervals, and timeout-aware summaries to a future stricter run.",
    "why_it_matters": "Solver runtime distributions are skewed and timeout-sensitive; means alone are insufficient for robust comparison.",
    "exact_fix": "Add median, IQR, standard deviation, bootstrap confidence intervals, and timeout-count fields to the tables or supplementary analysis.",
    "verification_steps": [
      "Rerun the analysis pipeline.",
      "Confirm generated tables include robust distribution metrics and timeout-aware summaries.",
      "Update Chapter 7 text to interpret those metrics."
    ]
  },
  {
    "severity": "major",
    "category": "Research/experimental issue",
    "file": "src/evaluation/algorithm_comparison.py; thesis/chapters/07_evaluation.tex",
    "location": "src/evaluation/algorithm_comparison.py:76-78; src/evaluation/algorithm_comparison.py:243-250; thesis/chapters/07_evaluation.tex:108-119; thesis/chapters/07_evaluation.tex:337-340",
    "issue": "Memory is measured as process RSS delta in a shared sequential process with reused solvers.",
    "why_it_matters": "The metric cannot support isolated peak-memory claims per solver.",
    "exact_fix": "Run each solver/case in a separate child process and record peak RSS with cold-start and warm-start modes separated.",
    "verification_steps": [
      "Regenerate benchmark JSON with an isolated peak-RSS memory_method.",
      "Confirm each solver result records peak memory independently.",
      "Update Chapter 7 memory figure and captions."
    ]
  },
  {
    "severity": "major",
    "category": "Reproducibility/setup issue",
    "file": "data/README.md; results/validation/native_exact/MANIFEST.json; scripts/verification/native_exact_validation.py",
    "location": "data/README.md:28-37; results/validation/native_exact/MANIFEST.json:5-12; results/validation/native_exact/MANIFEST.json:24-27; scripts/verification/native_exact_validation.py:26-37; scripts/verification/native_exact_validation.py:382-392",
    "issue": "The canonical native exact validation requires data/pattern_databases/corner_db.pkl, but generated .pkl caches are omitted from the source ZIP.",
    "why_it_matters": "The native exact validation claim cannot be fully rerun from the archive alone without a separate large generated artifact.",
    "exact_fix": "Add a documented cache-generation target with expected runtime and hash, or distribute the required cache as a separately verifiable artifact.",
    "verification_steps": [
      "Extract the ZIP into a fresh directory.",
      "Run the canonical native validation command.",
      "Confirm it either succeeds end-to-end or fails with a documented command for generating the missing cache."
    ]
  },
  {
    "severity": "major",
    "category": "Citation/reference issue",
    "file": "thesis/references.bib; thesis/chapters/03_thistlethwaite.tex; thesis/chapters/02_background.tex",
    "location": "thesis/references.bib:25-30; thesis/chapters/03_thistlethwaite.tex:8-16; thesis/chapters/02_background.tex:160; thesis/chapters/02_background.tex:237",
    "issue": "The foundational Thistlethwaite citation is a secondary Jaap Scherphuis webpage but is used to support primary algorithm history and theory.",
    "why_it_matters": "Core historical and mathematical claims need primary or explicitly secondary sourcing.",
    "exact_fix": "Replace or supplement thistlethwaite1981 with the best primary/historical source available, or explicitly label it as a secondary explanatory source in the thesis.",
    "verification_steps": [
      "Inspect thesis/references.bib for a primary Thistlethwaite source or explicit secondary-source note.",
      "Confirm chapter text distinguishes historical source from explanatory webpage."
    ]
  },
  {
    "severity": "minor",
    "category": "Citation/reference issue",
    "file": "thesis/references.bib",
    "location": "thesis/references.bib:188-199; thesis/references.bib:231-249",
    "issue": "The bibliography contains uncited entries; static analysis found 32 uncited keys.",
    "why_it_matters": "Uncited entries make the bibliography look padded and reduce reference-list precision.",
    "exact_fix": "Remove uncited entries or cite them in a relevant related-work or future-work section.",
    "verification_steps": [
      "Run a script comparing LaTeX cite keys to thesis/references.bib keys.",
      "Confirm uncited count is zero or intentionally documented."
    ]
  },
  {
    "severity": "major",
    "category": "Citation/reference issue",
    "file": "papers/DOWNLOAD_SUMMARY.txt; REPRODUCIBILITY_MANIFEST.json; README.md",
    "location": "papers/DOWNLOAD_SUMMARY.txt:13-16; papers/DOWNLOAD_SUMMARY.txt:31-39; papers/DOWNLOAD_SUMMARY.txt:54-64; papers/DOWNLOAD_SUMMARY.txt:110-116; REPRODUCIBILITY_MANIFEST.json:2-6; README.md:61-62",
    "issue": "Citation-content verification is not possible from the ZIP alone because cited PDFs are excluded and the acquisition log records incomplete coverage.",
    "why_it_matters": "An auditor can verify citation keys but not whether every cited claim is supported by source text.",
    "exact_fix": "Add a claim-to-reference evidence table with page/section pointers and public DOI/URL fields, or provide a separately verifiable permitted evidence bundle.",
    "verification_steps": [
      "Sample cited claims from thesis chapters.",
      "Confirm each sampled claim has a source locator that can be checked without private/local PDFs."
    ]
  },
  {
    "severity": "major",
    "category": "Reproducibility/setup issue",
    "file": "verify_setup.py; pytest.ini; pyproject.toml",
    "location": "verify_setup.py:341-349; verify_setup.py:451-456; pytest.ini:3-7; pyproject.toml:15-22",
    "issue": "verify_setup.py --full does not override pytest addopts, so slow/external/cache_building tests remain excluded.",
    "why_it_matters": "The advertised full verification mode is not actually full.",
    "exact_fix": "For full mode, call pytest with -o addopts= and an explicit marker policy, or clear PYTEST_ADDOPTS before running pytest.",
    "verification_steps": [
      "Run python -m pytest tests --collect-only -q and observe default deselections.",
      "Run python verify_setup.py --full after the fix and confirm the previously deselected tests are included or explicitly reported according to policy."
    ]
  },
  {
    "severity": "major",
    "category": "Reproducibility/setup issue",
    "file": "README.md; verify_setup.py; requirements.txt; requirements.lock",
    "location": "README.md:28-33; README.md:41-45; verify_setup.py:138-164; requirements.txt:1-42; requirements.lock:1-18",
    "issue": "README instructs installation from requirements.lock, but verify_setup.py checks requirements.txt and tells users to install requirements.txt.",
    "why_it_matters": "The verification script does not validate the pinned audited dependency snapshot.",
    "exact_fix": "Make verify_setup.py default to requirements.lock, add a --requirements option if needed, and update the missing-package message.",
    "verification_steps": [
      "Run python verify_setup.py.",
      "Confirm it reports requirements.lock as the checked dependency file.",
      "Confirm missing-package instructions match README setup instructions."
    ]
  },
  {
    "severity": "major",
    "category": "Reproducibility/setup issue",
    "file": "README.md; requirements.lock",
    "location": "README.md:41-45; requirements.lock:1-18; requirements.lock:117-143",
    "issue": "The Python lock file is explicitly non-cryptographic and omits hashes, platform markers, Python ABI constraints, and TeX/Tectonic versions.",
    "why_it_matters": "Dependency installation can drift across platforms even when versions appear pinned.",
    "exact_fix": "Use a hash-verified lock mechanism such as uv.lock or pip-tools --generate-hashes, and pin TeX/Docker image and Node/npm versions.",
    "verification_steps": [
      "Install dependencies with hash checking from a clean environment.",
      "Record Python, package, TeX, Node, and npm versions in the validation output.",
      "Confirm setup/build/test commands use those pinned versions."
    ]
  },
  {
    "severity": "minor",
    "category": "Submission polish issue",
    "file": "docs/THESIS_FULL_AUDIT_2026-03-21.md",
    "location": "docs/THESIS_FULL_AUDIT_2026-03-21.md:1-7; docs/THESIS_FULL_AUDIT_2026-03-21.md:28-34; docs/THESIS_FULL_AUDIT_2026-03-21.md:492-509",
    "issue": "A historical internal audit report with old findings and open questions remains under docs.",
    "why_it_matters": "It can confuse reviewers or make the final submission package look unresolved.",
    "exact_fix": "Move the file to an archive/audit-history area or exclude it from the final submission ZIP while retaining it internally.",
    "verification_steps": [
      "Inspect the final archive contents.",
      "Confirm historical audit material is either absent from submission docs or clearly quarantined as archival."
    ]
  }
]
```

## Scores

Overall thesis quality score: **68/100**
Technical quality score: **63/100**
Submission readiness score: **38/100**

The thesis has substantial structure, real benchmark artifacts, and many self-critical limitations, but it is not submission-ready because the approval page is incomplete/excluded, the build/test reproducibility story has blockers, and at least one native validation claim is stronger than the stored evidence.
