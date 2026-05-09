Audit basis: uploaded ZIP only, extracted under `/mnt/data/audit_repo`. I verified actual files before listing issues. Fast pytest passed (`287 passed, 29 deselected`), source-ZIP native exact validation passed (`261 cases, 0 failures`), but the full/canonical evidence path and several quality gates remain weak.

## 1. Critical blockers

### CRITICAL — Approval/signature page is still a template

File: `thesis/chapters/00_approval.tex`
Location: lines 33–36, 41–44, 50
Problem: The final thesis still contains placeholder committee rows (`Ονοματεπώνυμο μέλους επιτροπής, ιδιότητα`) and a blank examination date. `README.md` line 8 also admits signature-page completion is pending.
Why it matters: This is not submission-ready institutional front matter. The rendered PDF still exposes the incomplete administrative page.
Exact fix: Replace the placeholder rows with the official committee names/titles and examination date, or remove this generated template and insert the institution-approved signed page according to University of Patras rules.
Verification steps: Rebuild `thesis/main.pdf`; inspect page 2 visually; grep the source/PDF text for `Ονοματεπώνυμο μέλους επιτροπής` and ensure no placeholder remains.

### CRITICAL — Canonical native-exact validation claims cannot be regenerated from the uploaded ZIP alone

Files: `results/validation/native_exact/README.md`, `data/README.md`, `thesis/chapters/appendix_a.tex`, `results/validation/native_exact/MANIFEST.json`
Locations: `results/validation/native_exact/README.md` lines 25–31 and 61–68; `data/README.md` lines 36–53; `thesis/chapters/appendix_a.tex` lines 160–161; `MANIFEST.json` lines 65–69
Problem: The thesis and manifest cite the canonical 3,513-case native-exact validation, but the source ZIP explicitly omits `data/pattern_databases/corner_db.pkl` and requires an optional external oracle/backend. The repository provides only a smaller `--preset source-zip` smoke validation from the ZIP.
Why it matters: A reviewer using only the submitted ZIP cannot independently regenerate a headline validation result cited in the thesis.
Exact fix: Either include the companion cache as a separately documented artifact with SHA-256, size, generation command, and archival location, or downgrade the thesis wording so the canonical result is clearly “archived evidence, not source-ZIP reproducible.”
Verification steps: From a clean extracted ZIP, run `python scripts/verification/native_exact_validation.py --preset canonical --output-dir /tmp/native_exact_canonical_clean`; it must either pass from included/archived prerequisites or the thesis must explicitly state that only `--preset source-zip` is reproducible from the source package.

## 2. Thesis writing issues

### MEDIUM — Academic tone is weakened by inconsistent Greek/English terminology

File: `thesis/chapters/07_evaluation.tex`
Location: lines 6, 14–20, 22–27, 34–44, 126–137
Problem: Greek prose repeatedly mixes untranslated English terms such as `exact benchmark`, `backend choices`, `inputs`, `batch-amortized timings`, `soft grace`, `solver instances`, and `confidence intervals`.
Why it matters: The technical meaning is mostly clear, but the style is not consistently polished for a Greek academic thesis.
Exact fix: Add a short terminology policy/glossary and standardize terms: either translate consistently or mark retained English technical terms with `\emph{}`/`\texttt{}` only where justified.
Verification steps: Rebuild the thesis and manually review Chapter 7 for consistent terminology; search for repeated raw English phrases and confirm each is either translated or intentionally styled.

### HIGH — Abstract overstates the strength of the test suite

Files: `thesis/chapters/00_abstract_en.tex`, `thesis/chapters/00_abstract_gr.tex`, `pytest.ini`
Locations: `00_abstract_en.tex` lines 31–34; `00_abstract_gr.tex` lines 31–34; `pytest.ini` lines 1–6
Problem: The abstracts describe an “extensive test suite” with separate fast, slow, external-backend, and cache-building profiles, but the default pytest profile explicitly excludes `slow`, `external`, and `cache_building`, and the slow profile is not practically bounded.
Why it matters: The thesis summary gives a stronger impression of implementation validation than the default reproducibility path supports.
Exact fix: Either make all advertised profiles reliably runnable under documented budgets or revise the abstracts to say the repository includes a fast regression suite plus opt-in heavyweight profiles.
Verification steps: Run `python -m pytest tests -q`, `python -m pytest tests -q -m slow`, `python -m pytest tests -q -m external`, and `python -m pytest tests -q -m cache_building` in a clean environment; update the abstract wording to match what actually completes.

## 3. Technical/code issues

### HIGH — Thistlethwaite correctness tests can pass when the solver returns `None`

File: `tests/unit/test_thistlethwaite.py`
Location: lines 457–477, 478–487, 521–542, 544–563, 566–594
Problem: Several tests only verify correctness inside `if result is not None`; one skips when the solver returns `None`, and the integration test prints a message without failing.
Why it matters: A regression where the solver stops solving can still pass or skip important tests. This invalidates solver-correctness confidence.
Exact fix: Replace conditional verification with `assert result is not None` before checking move correctness, except for explicitly marked `xfail` cases with documented reasons.
Verification steps: Temporarily monkeypatch `ThistlethwaiteSolver.solve()` to return `None`; the affected tests must fail, not pass or skip.

### HIGH — Slow Kociemba performance test is not bounded enough for reproducible execution

File: `tests/unit/test_kociemba.py`
Location: lines 433–481
Problem: `test_solver_performance` runs five 20-move scrambles with `KociembaSolver()` and `timeout=10.0`, but the solver itself has additional timeout grace and expensive lazy initialization. In audit, the slow profile exceeded 180 seconds at this first selected test.
Why it matters: The advertised slow profile is not a reliable verification target for reviewers or CI.
Exact fix: Reduce the sample size/depth, separate table initialization from timed solve assertions, add a per-test timeout such as `pytest-timeout`, or require an explicit environment variable for full performance runs.
Verification steps: Run `python -m pytest tests/unit/test_kociemba.py::TestKociembaSolver::test_solver_performance -q -m slow` from a clean checkout; it should complete under the documented budget.

### MEDIUM — Kociemba opposite-face pruning comment/convention is inconsistent with the thesis/native exact convention

Files: `src/kociemba/solver.py`, `src/korf/native_exact_solver.py`, `thesis/chapters/05_korf.tex`
Locations: `src/kociemba/solver.py` lines 587–597 and 719–727; `src/korf/native_exact_solver.py` lines 281–301; `thesis/chapters/05_korf.tex` line 379
Problem: `src/kociemba/solver.py` says the canonical order is `U before D, F before B, L before R`, but its predicate prunes the opposite order relative to that text. The native exact solver and thesis describe the opposite-pair canonicalization differently.
Why it matters: This is a search-space pruning rule. Even if completeness is unaffected, the documented convention and implementation are not auditable as written.
Exact fix: Decide the canonical order once, align both solvers and comments to it, and add a regression test that confirms opposite-face commutation pruning does not remove the canonical representative.
Verification steps: Run targeted tests for adjacent opposite-face pairs such as `U D`, `D U`, `F B`, `B F`, `L R`, `R L`; confirm exactly one canonical ordering is retained and solver completeness tests still pass.

### MEDIUM — Pickle cache loading lacks schema/hash validation

Files: `src/korf/native_coordinate_heuristic.py`, `src/korf/corner_database.py`, `src/korf/pattern_database.py`
Locations: `native_coordinate_heuristic.py` lines 147–152 and 159–169; `corner_database.py` lines 348–351; `pattern_database.py` lines 204–215
Problem: Repository cache files are loaded via `pickle.load()` and trusted with minimal validation. Some code checks a format version, but there is no consistent shape, dtype, size, checksum, or manifest validation before using loaded tables.
Why it matters: Corrupt or stale cache files can silently change solver behavior and benchmark reproducibility. Pickle also has avoidable safety risks when used on untrusted files.
Exact fix: Add schema validation for all cache payloads, check expected table sizes and value ranges, store SHA-256 digests in a manifest, and reject mismatched caches with a clear rebuild path.
Verification steps: Corrupt one cached table intentionally; the loader must fail with a deterministic validation error instead of accepting the payload.

### HIGH — Coverage gate is too low for the thesis claims

File: `README.md`
Location: lines 157–159
Problem: The documented coverage command uses `--cov-fail-under=49`. Audit coverage was only about 49.57%, with entire evaluation modules at 0% and important solver/table modules substantially under-tested.
Why it matters: A thesis implementation claiming validated solver behavior and benchmark tooling should not rely on a coverage threshold below 50%.
Exact fix: Add tests for evaluation/statistics/validation/visualization modules and solver/table edge cases, then raise the gate in stages, at least to a defensible interim threshold such as 70%.
Verification steps: Run `python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered --cov-fail-under=70`; the command should pass after added tests.

## 4. Research/experimental issues

### HIGH — Benchmark timing evidence is single-run and lacks full reproducibility metadata

Files: `thesis/chapters/07_evaluation.tex`, `results/benchmarks/thesis/thesis_results_combined.json`
Locations: `07_evaluation.tex` lines 126–137 and 381–398; `thesis_results_combined.json` lines 120–145
Problem: The thesis admits there are no repetitions per scramble, no confidence intervals, no separate cold/warm timing, and no full package/kernel/process/backend digest captured in the original run.
Why it matters: The comparative runtime conclusions are useful but not statistically strong. Single-run, batch-amortized timings are vulnerable to initialization, cache, and machine-state effects.
Exact fix: Add a regenerated benchmark protocol with repeated runs per scramble, explicit warmup/cold separation, fixed seeds, process isolation, and full environment/backend hashes.
Verification steps: Regenerate `results/benchmarks/thesis/thesis_results_combined.json` with fields such as `run_id`, `repetition_id`, `warmup_policy`, `package_lock_sha256`, `backend_wheel_sha256`, and confidence intervals; update Chapter 7 tables/figures accordingly.

### MEDIUM — Scramble corpus uses requested length, not verified depth, and allows redundant moves

Files: `thesis/chapters/07_evaluation.tex`, `results/benchmarks/thesis/thesis_results_combined.json`
Locations: `07_evaluation.tex` lines 89–91 and 394; `thesis_results_combined.json` lines 117–119
Problem: The benchmark corpus is marked `legacy_random_all_moves_redundant_allowed`; requested scramble length can include adjacent same-face redundancy and cancellations.
Why it matters: Figures or discussion by “depth” can be misread as performance by true optimal distance. The thesis discloses this, but the experimental design remains weaker than an exact-depth or redundancy-controlled corpus.
Exact fix: Regenerate a secondary benchmark using no-consecutive-same-face scrambles and, where feasible, exact-depth stratification using the exact backend for verification.
Verification steps: Produce a new corpus manifest showing the generator policy, seed, redundancy checks, and verified depth distribution; update captions to distinguish requested length from verified depth.

## 5. Citation/reference issues

### MEDIUM — External exact backend citation lacks archival commit/release provenance

Files: `thesis/references.bib`, `results/benchmarks/thesis/thesis_results_combined.json`, `README.md`
Locations: `references.bib` lines 162–168; `thesis_results_combined.json` lines 147–157; `README.md` line 128
Problem: The external exact backend is cited as a GitHub repository/PyPI package version, while the benchmark JSON records `upstream_commit: null` and notes that the original benchmark did not record a wheel hash or upstream commit.
Why it matters: A benchmark-critical external solver should be cited and archived precisely enough for future reproduction.
Exact fix: Cite an archived release, Software Heritage snapshot, Zenodo artifact, exact commit, or exact wheel hash used for the benchmark; store the same identifier in benchmark provenance.
Verification steps: Confirm `references.bib` includes the archived identifier and `thesis_results_combined.json` has non-null reproducibility fields for the external backend.

## 6. Reproducibility/setup issues

### HIGH — CI workflow builds the thesis but does not validate code, webapp, coverage, or native-exact smoke evidence

Files: `.github/workflows/thesis-build.yml`, `webapp/package.json`
Locations: `.github/workflows/thesis-build.yml` lines 3–10 and 24–35; `webapp/package.json` lines 10–15
Problem: The only workflow validates thesis sources and builds the PDF. It does not run Python tests, coverage, source-ZIP native validation, or the webapp build/test scripts. It also does not trigger on `src/**`, `tests/**`, `results/**`, or `webapp/**` changes.
Why it matters: Changes to implementation or benchmark evidence can bypass CI while still affecting thesis claims.
Exact fix: Add CI jobs for Python fast tests, coverage, source-ZIP native validation, and webapp `npm ci`, `npm run build`, and `npm test`; expand path triggers to include code, tests, data/results, and webapp files.
Verification steps: Push a change under `src/` or `tests/`; CI must run and fail on an intentional test regression.

### MEDIUM — Audit/source ZIP includes `.coverage` despite ignore policy

Files: `.coverage`, `.gitignore`, `scripts/generate_reproducibility_manifest.py`, `scripts/create_audit_zip.py`
Locations: ZIP entry `.coverage`; `.gitignore` lines 37–40; `generate_reproducibility_manifest.py` lines 19–49 and 57–78; `create_audit_zip.py` lines 18–22
Problem: The uploaded archive contains `.coverage`, even though `.gitignore` excludes it. The reproducibility manifest exclusion rules do not exclude `.coverage`, and the audit ZIP creator includes whatever the manifest admits.
Why it matters: Generated local artifacts should not leak into a source audit archive. They can confuse reproducibility checks and make archives machine-state dependent.
Exact fix: Add `.coverage` and other coverage artifacts to the manifest exclusion rules, regenerate the source ZIP, and ensure generated coverage data is never packaged.
Verification steps: Run the archive script, then `unzip -l <archive>.zip | grep -E '(^|/)\\.coverage$'`; the command should return no matches.

### MEDIUM — Default solver/cache construction can mutate repository-local `data/`

Files: `src/korf/native_coordinate_heuristic.py`, `src/kociemba/solver.py`, `data/README.md`
Locations: `native_coordinate_heuristic.py` lines 49–58 and 140–170; `src/kociemba/solver.py` lines 79–82 and 129–135; `data/README.md` lines 3–4
Problem: Some constructors default to repository-local cache paths such as `data/pattern_databases/native_exact` and `data/kociemba`; when caches are missing, ordinary solver construction can create or update files under the repository tree.
Why it matters: Test and benchmark runs can dirty the checkout and make reproducibility depend on implicit local cache state.
Exact fix: Default runtime caches to an external cache location such as `$XDG_CACHE_HOME`, a user-supplied `--cache-dir`, or a pytest temporary directory; keep repository `data/` read-only unless an explicit generation command is run.
Verification steps: Remove generated caches, run the fast test suite, and verify `git status --porcelain data/` remains clean.

## 7. Submission polish issues

### LOW — Code-to-thesis mapping contains stale test counts

File: `docs/CODE_TO_THESIS_MAPPING.md`
Location: lines 38–64 and 123–125
Problem: The mapping claims `test_thistlethwaite.py` has 35 tests, `test_kociemba.py` has 25 tests, `test_composite_heuristic.py` has 25 tests, and `test_distance_estimator.py` has 21 tests. Actual collection from the uploaded ZIP differs.
Why it matters: This document is used as a thesis/code traceability aid; stale counts reduce reviewer trust.
Exact fix: Remove exact test counts or regenerate them automatically from `pytest --collect-only`.
Verification steps: Run `python -m pytest tests --collect-only -q -o addopts=` and compare per-file counts with the documentation.

## FIX_TARGETS

```json
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "thesis/chapters/00_approval.tex",
    "location": "lines 33-36, 41-44, 50",
    "issue": "The approval/signature page is still a template with two placeholder committee rows and a blank examination date. README.md line 8 also states that signature-page completion is pending.",
    "exact_fix": "Replace the placeholder committee rows and blank date with the official committee names/titles and examination date, or remove this generated template and insert the institution-approved signed page.",
    "verification_steps": [
      "Rebuild thesis/main.pdf.",
      "Inspect page 2 visually.",
      "Search the source and rendered PDF text for 'Ονοματεπώνυμο μέλους επιτροπής' and confirm it is absent."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "results/validation/native_exact/README.md; data/README.md; thesis/chapters/appendix_a.tex; results/validation/native_exact/MANIFEST.json",
    "location": "results/validation/native_exact/README.md lines 25-31 and 61-68; data/README.md lines 36-53; thesis/chapters/appendix_a.tex lines 160-161; MANIFEST.json lines 65-69",
    "issue": "The canonical 3,513-case native-exact validation claim cannot be regenerated from the uploaded ZIP alone because the required corner_db.pkl companion cache and optional external oracle/backend are omitted.",
    "exact_fix": "Include the companion cache as a separately documented artifact with SHA-256, size, generation command, and archival location, or revise the thesis so the canonical result is clearly identified as archived evidence rather than source-ZIP-reproducible evidence.",
    "verification_steps": [
      "From a clean extracted ZIP, run python scripts/verification/native_exact_validation.py --preset canonical --output-dir /tmp/native_exact_canonical_clean.",
      "Confirm the command passes using included or documented companion artifacts, or confirm the thesis states that only --preset source-zip is reproducible from the source package."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 6, 14-20, 22-27, 34-44, 126-137",
    "issue": "Chapter 7 mixes Greek prose with many raw English technical phrases such as exact benchmark, backend choices, inputs, batch-amortized timings, soft grace, solver instances, and confidence intervals.",
    "exact_fix": "Add a terminology policy/glossary and standardize these terms by either translating them consistently or styling retained English technical terms intentionally.",
    "verification_steps": [
      "Search Chapter 7 for raw English benchmark terminology.",
      "Rebuild the thesis and manually verify that repeated terms are consistently translated or styled."
    ]
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex; pytest.ini",
    "location": "00_abstract_en.tex lines 31-34; 00_abstract_gr.tex lines 31-34; pytest.ini lines 1-6",
    "issue": "The abstracts describe an extensive test suite with separate fast, slow, external-backend, and cache-building profiles, but the default pytest profile excludes slow, external, and cache_building tests and the slow profile is not practically bounded.",
    "exact_fix": "Either make all advertised profiles reliably runnable under documented budgets or revise the abstracts to describe a fast regression suite plus opt-in heavyweight profiles.",
    "verification_steps": [
      "Run python -m pytest tests -q.",
      "Run python -m pytest tests -q -m slow.",
      "Run python -m pytest tests -q -m external.",
      "Run python -m pytest tests -q -m cache_building.",
      "Ensure the abstract wording matches the profiles that actually complete."
    ]
  },
  {
    "severity": "High",
    "category": "Technical/code issues",
    "file": "tests/unit/test_thistlethwaite.py",
    "location": "lines 457-477, 478-487, 521-542, 544-563, 566-594",
    "issue": "Several Thistlethwaite tests only verify solver correctness when result is not None; one skips on None and the integration test only prints a message on failure.",
    "exact_fix": "Add assert result is not None before solution verification in these tests, except for explicitly documented xfail cases.",
    "verification_steps": [
      "Temporarily monkeypatch ThistlethwaiteSolver.solve() to return None.",
      "Run the affected tests.",
      "Confirm they fail rather than pass or skip."
    ]
  },
  {
    "severity": "High",
    "category": "Technical/code issues",
    "file": "tests/unit/test_kociemba.py",
    "location": "lines 433-481",
    "issue": "The slow Kociemba performance test runs five 20-move scrambles with lazy solver initialization and a soft timeout/grace model; in audit the slow profile exceeded 180 seconds at this first selected test.",
    "exact_fix": "Reduce sample size/depth, separate table initialization from timed assertions, add a per-test timeout, or require an explicit environment variable for full performance runs.",
    "verification_steps": [
      "Run python -m pytest tests/unit/test_kociemba.py::TestKociembaSolver::test_solver_performance -q -m slow.",
      "Confirm the test completes within the documented budget from a clean checkout."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/kociemba/solver.py; src/korf/native_exact_solver.py; thesis/chapters/05_korf.tex",
    "location": "src/kociemba/solver.py lines 587-597 and 719-727; src/korf/native_exact_solver.py lines 281-301; thesis/chapters/05_korf.tex line 379",
    "issue": "The Kociemba pruning comment says the canonical order is U before D, F before B, L before R, but the predicate prunes the opposite order relative to that text; this also differs from the native exact solver/thesis convention.",
    "exact_fix": "Choose one opposite-face canonical order, align comments and predicates across solvers, and add regression tests for opposite-face commutation pruning.",
    "verification_steps": [
      "Add tests covering U D, D U, F B, B F, L R, and R L adjacency cases.",
      "Confirm exactly one canonical order is retained.",
      "Run solver correctness tests after the change."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/native_coordinate_heuristic.py; src/korf/corner_database.py; src/korf/pattern_database.py",
    "location": "native_coordinate_heuristic.py lines 147-152 and 159-169; corner_database.py lines 348-351; pattern_database.py lines 204-215",
    "issue": "Cache payloads are loaded via pickle with insufficient schema, shape, dtype, value-range, and checksum validation.",
    "exact_fix": "Add strict schema validation, expected table sizes and value ranges, SHA-256 manifest checks, and clear rebuild errors for mismatched caches.",
    "verification_steps": [
      "Create a deliberately corrupted cache file.",
      "Run the relevant loader.",
      "Confirm it raises a deterministic validation error instead of accepting the cache."
    ]
  },
  {
    "severity": "High",
    "category": "Technical/code issues",
    "file": "README.md",
    "location": "lines 157-159",
    "issue": "The documented coverage gate is only --cov-fail-under=49; audit coverage was approximately 49.57%, with entire evaluation modules uncovered and several solver/table modules weakly covered.",
    "exact_fix": "Add tests for evaluation/statistics/validation/visualization modules and solver/table edge cases, then raise the coverage gate to a defensible interim threshold such as 70%.",
    "verification_steps": [
      "Run python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered --cov-fail-under=70.",
      "Confirm the command passes after new tests are added."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "07_evaluation.tex lines 126-137 and 381-398; thesis_results_combined.json lines 120-145",
    "issue": "Benchmark timing evidence is single-run and batch-amortized, with no repetitions per scramble, no confidence intervals, no separate cold/warm timings, and incomplete original runtime/backend provenance.",
    "exact_fix": "Regenerate benchmarks with repeated runs per scramble, explicit warmup/cold separation, fixed seeds, process isolation, full environment hashes, and backend artifact hashes.",
    "verification_steps": [
      "Regenerate thesis_results_combined.json with run_id, repetition_id, warmup_policy, package_lock_sha256, backend_wheel_sha256, and confidence interval fields.",
      "Update Chapter 7 tables and figures from the regenerated artifact."
    ]
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "07_evaluation.tex lines 89-91 and 394; thesis_results_combined.json lines 117-119",
    "issue": "The benchmark corpus records requested scramble length, not true optimal depth, and is marked as a legacy corpus that allows adjacent same-face redundancy and cancellations.",
    "exact_fix": "Regenerate a secondary corpus with no-consecutive-same-face scrambles and, where feasible, exact-depth stratification using the exact backend.",
    "verification_steps": [
      "Produce a corpus manifest with generator policy, seed, redundancy checks, and verified-depth distribution.",
      "Update figure captions and discussion to distinguish requested length from verified optimal depth."
    ]
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; results/benchmarks/thesis/thesis_results_combined.json; README.md",
    "location": "references.bib lines 162-168; thesis_results_combined.json lines 147-157; README.md line 128",
    "issue": "The external exact backend is cited only as a GitHub repository/PyPI package version while benchmark provenance has upstream_commit null and notes no original wheel hash or upstream commit was recorded.",
    "exact_fix": "Cite an archived release, Software Heritage snapshot, Zenodo artifact, exact commit, or exact wheel hash used for the benchmark, and store the same identifier in benchmark provenance.",
    "verification_steps": [
      "Confirm references.bib contains the archived identifier.",
      "Confirm thesis_results_combined.json has non-null reproducibility fields for the external backend."
    ]
  },
  {
    "severity": "High",
    "category": "Reproducibility/setup issues",
    "file": ".github/workflows/thesis-build.yml; webapp/package.json",
    "location": ".github/workflows/thesis-build.yml lines 3-10 and 24-35; webapp/package.json lines 10-15",
    "issue": "CI validates thesis sources and builds the PDF, but does not run Python tests, coverage, source-ZIP native validation, or webapp build/test scripts; path triggers also omit src, tests, results, and webapp changes.",
    "exact_fix": "Add CI jobs for Python fast tests, coverage, source-ZIP native validation, webapp npm ci, npm run build, and npm test; expand path triggers to include code, tests, data/results, and webapp files.",
    "verification_steps": [
      "Push or simulate a change under src/ or tests/.",
      "Confirm CI runs and fails on an intentional test regression."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": ".coverage; .gitignore; scripts/generate_reproducibility_manifest.py; scripts/create_audit_zip.py",
    "location": "ZIP entry .coverage; .gitignore lines 37-40; generate_reproducibility_manifest.py lines 19-49 and 57-78; create_audit_zip.py lines 18-22",
    "issue": "The uploaded audit/source ZIP includes .coverage even though .gitignore excludes it; the manifest/archive rules do not exclude this generated artifact.",
    "exact_fix": "Add .coverage and related coverage artifacts to the reproducibility manifest exclusion rules and regenerate the source ZIP.",
    "verification_steps": [
      "Run the archive creation script.",
      "Run unzip -l <archive>.zip | grep -E '(^|/)\\.coverage$'.",
      "Confirm there are no matches."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "src/korf/native_coordinate_heuristic.py; src/kociemba/solver.py; data/README.md",
    "location": "native_coordinate_heuristic.py lines 49-58 and 140-170; src/kociemba/solver.py lines 79-82 and 129-135; data/README.md lines 3-4",
    "issue": "Default solver/cache construction can create or update files under repository-local data/ paths when caches are missing.",
    "exact_fix": "Default runtime caches to XDG_CACHE_HOME, a user-supplied --cache-dir, or pytest temporary directories; keep repository data/ read-only unless an explicit generation command is run.",
    "verification_steps": [
      "Remove generated caches.",
      "Run the fast test suite.",
      "Verify git status --porcelain data/ remains clean."
    ]
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "docs/CODE_TO_THESIS_MAPPING.md",
    "location": "lines 38-64 and 123-125",
    "issue": "The code-to-thesis mapping contains stale per-file test counts that do not match pytest collection from the uploaded ZIP.",
    "exact_fix": "Remove exact test counts or regenerate them automatically from pytest --collect-only.",
    "verification_steps": [
      "Run python -m pytest tests --collect-only -q -o addopts=.",
      "Compare per-file counts with docs/CODE_TO_THESIS_MAPPING.md and update or remove stale numbers."
    ]
  }
]
```

Overall thesis quality score: **76/100**
Technical quality score: **70/100**
Submission readiness score: **52/100**
