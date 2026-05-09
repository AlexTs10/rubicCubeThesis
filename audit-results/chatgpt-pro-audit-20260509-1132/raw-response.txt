## Audit basis

I audited the extracted contents of the uploaded ZIP only. I did not use GitHub or external repositories.

Validated during the audit:

* ZIP inventory matched the repository manifest: 238 files total, including `REPRODUCIBILITY_MANIFEST.json`.
* `thesis/main.pdf` is readable, 106 pages, A4, fonts embedded, no obvious placeholder strings such as `TODO`, `FIXME`, `Lorem`, `??`, or undefined references in extracted text.
* Python fast test profile ran successfully: `272 passed, 1 skipped, 28 deselected`.
* Notebook verification passed for all 6 notebooks via `scripts/verify_notebooks.py`.
* Web app `npm ci`, `npm test`, `npm run lint`, and `npm run build` succeeded in the audit environment.
* `scripts/thesis_workflow.py status` reported 31 bibliography entries, 31 citation keys used, 0 missing, 0 unused.
* `scripts/thesis_workflow.py validate` reported no ready thesis build path in this environment, but still exited successfully; that is reported below as an issue.

---

# 1. Critical blockers

## CB-01 — Critical — Final institutional front matter is incomplete and excluded

**File:** `thesis/main.tex`; `thesis/chapters/00_approval.tex`; `thesis/README.md`; `README.md`
**Location:** `thesis/main.tex:174-180`; `thesis/chapters/00_approval.tex:34-44`; `thesis/README.md:3`; `README.md:8`

**Problem:** The formal approval/signature page is not included in the thesis build. `main.tex` inputs acknowledgements and abstracts after `\frontmatter`, but does not input `chapters/00_approval.tex`. The approval file itself still contains placeholder committee-member rows and a dotted examination-date field.

**Why it matters:** The repository itself states that final institutional submission is not complete until this page is filled and included. This is a hard submission-readiness blocker even if the technical content is otherwise strong.

**Exact fix recommendation:** Fill `thesis/chapters/00_approval.tex` with official committee names, roles, and examination date. Add `\input{chapters/00_approval}` at the required location in `thesis/main.tex`, according to institutional formatting rules. Update `README.md` and `thesis/README.md` once this is no longer pending.

**Verification steps:**
Run `python scripts/thesis_workflow.py build --mode auto`; inspect the generated PDF; run `pdftotext thesis/main.pdf - | grep` for the committee names and examination date; confirm no placeholder committee rows or `\dotfill` remain.

---

## CB-02 — Critical — Canonical native exact validation is not reproducible from the source ZIP alone

**File:** `results/validation/native_exact/README.md`; `results/validation/native_exact/MANIFEST.json`; `scripts/verification/native_exact_validation.py`
**Location:** `results/validation/native_exact/README.md:25-30`; `results/validation/native_exact/MANIFEST.json:24-28`; `scripts/verification/native_exact_validation.py:244-255`

**Problem:** The canonical native exact validation path requires `data/pattern_databases/corner_db.pkl`, but the source ZIP intentionally omits that cache. Running the canonical preset from the extracted repository fails with a `FileNotFoundError`. The repository provides a smaller source-ZIP smoke preset, but that is not equivalent to the canonical validation claim.

**Why it matters:** The thesis claims around native exact validation cannot be fully reproduced from the submitted source ZIP alone. A reproducibility auditor cannot independently rerun the canonical validation without an omitted artifact or a deterministic regeneration path.

**Exact fix recommendation:** Either include the canonical `corner_db.pkl` as a separately listed, hashed artifact with retrieval instructions, or add a deterministic cache-generation command that rebuilds it from source and records its hash. If the full artifact is intentionally excluded, downgrade the thesis claim to “canonical artifacts archived; source ZIP supports smoke validation only.”

**Verification steps:**
From a clean extraction, run `python scripts/verification/native_exact_validation.py --preset canonical --output-dir /tmp/native_exact_audit`. It should complete successfully without manual artifact injection, or the thesis must explicitly state that canonical validation requires an external archived artifact.

---

## CB-03 — Major — Thesis validation reports failure but exits with success status

**File:** `scripts/thesis_workflow.py`
**Location:** `scripts/thesis_workflow.py:878-939`; `scripts/thesis_workflow.py:1163-1180`

**Problem:** `python scripts/thesis_workflow.py validate` reports that no thesis build path is ready when local BibTeX/Tectonic/Docker are unavailable, but the command still exits with status `0`.

**Why it matters:** CI, graders, or examiners can falsely interpret the repository as validated even when the thesis build path is not ready. This weakens the repository’s reproducibility contract.

**Exact fix recommendation:** Make `validate` return a non-zero exit code whenever any validation issue is emitted, or add a `--strict` mode and make that the documented CI/default verification command. The validation report should distinguish warnings from hard failures.

**Verification steps:**
Temporarily run in an environment without BibTeX, Tectonic, and Docker. Execute `python scripts/thesis_workflow.py validate; echo $?`. The exit code should be non-zero when “No thesis build path is ready” is reported.

---

# 2. Thesis writing issues

## TW-01 — Major — Evaluation opening overstates “three implemented algorithms” despite external exact backend use

**File:** `thesis/chapters/07_evaluation.tex`
**Location:** `thesis/chapters/07_evaluation.tex:6`; `thesis/chapters/07_evaluation.tex:34-44`

**Problem:** The chapter opening states that the evaluation compares three implemented algorithms. Later, the chapter correctly explains that the official optimal/Korf benchmark path uses an external exact backend through `src/korf/optimal_solver.py`.

**Why it matters:** This wording can mislead examiners into attributing the optimal-backend performance to a fully native implementation. The later clarification is good, but the opening claim should not conflict with it.

**Exact fix recommendation:** Replace “three implemented algorithms” with “three solver paths” or “two repository-implemented solvers plus an external exact optimal baseline wrapped by the repository.” Also state this distinction near the first evaluation table.

**Verification steps:**
Search `thesis/chapters/07_evaluation.tex` for `υλοποιημέν` / “implemented algorithms” wording and confirm every such occurrence distinguishes native/internal implementation from external optimal backend.

---

## TW-02 — Medium — Fairness and attribution wording needs stronger qualification

**File:** `thesis/chapters/07_evaluation.tex`
**Location:** `thesis/chapters/07_evaluation.tex:6`; `thesis/chapters/07_evaluation.tex:22-27`; `thesis/chapters/07_evaluation.tex:88`; `thesis/chapters/07_evaluation.tex:125-132`; `thesis/chapters/07_evaluation.tex:400-404`

**Problem:** The evaluation chapter contains good caveats about unequal timeouts, legacy scramble redundancy, lack of repeated runs, and batch-amortized timing. However, some summary language still frames the comparison as a fair/common-condition algorithmic comparison.

**Why it matters:** Because the comparison uses different solver backends, different timeout policies, a legacy non-exact-depth corpus, and single-run timings, the conclusions should be framed as “under this fixed documented harness,” not as broad algorithmic superiority claims.

**Exact fix recommendation:** Reword the conclusion and opening to state that observed differences are valid for the documented corpus, platform, timeout policy, backend selection, and batch-amortized methodology. Avoid unqualified “fair comparison” language.

**Verification steps:**
Search the chapter for “δίκαι”, “κοινές συνθήκες”, “αποδίδονται”, and equivalent English terms. Confirm all such claims are explicitly bounded by the documented benchmark conditions.

---

## TW-03 — Medium — Published figures use English labels inside a Greek thesis

**File:** `src/evaluation/visualizations.py`; generated figure files under `thesis/figures/`
**Location:** `src/evaluation/visualizations.py:204-205`; `src/evaluation/visualizations.py:243-244`; `src/evaluation/visualizations.py:284-285`; `src/evaluation/visualizations.py:324-325`; `src/evaluation/visualizations.py:347-349`; `src/evaluation/visualizations.py:386-388`; `src/evaluation/visualizations.py:417-419`

**Problem:** The thesis captions are Greek, but the generated figure titles and axes are English, for example “Solution Length Comparison”, “Execution Time Comparison”, and “Memory Usage Comparison”.

**Why it matters:** This creates an avoidable formatting and language inconsistency in a Greek-language thesis.

**Exact fix recommendation:** Add a Greek-label mode to `src/evaluation/visualizations.py` or translate the labels used for the thesis figures. Regenerate all thesis figures after the label change.

**Verification steps:**
Regenerate figures, open `thesis/figures/fig*.png`, and confirm titles, axes, legends, and metric names use the same language style as the surrounding thesis text.

---

# 3. Technical/code issues

## TC-01 — Major — Thesis benchmark regeneration does not force the documented Kociemba backend

**File:** `src/evaluation/algorithm_comparison.py`; `src/kociemba/solver.py`; `scripts/benchmarks/regenerate_thesis_benchmarks.py`
**Location:** `src/evaluation/algorithm_comparison.py:188`; `src/kociemba/solver.py:79-87`; `src/kociemba/solver.py:337-344`; `src/kociemba/solver.py:380-390`; `src/kociemba/solver.py:405-414`; `src/kociemba/solver.py:435-445`; `scripts/benchmarks/regenerate_thesis_benchmarks.py:223-229`

**Problem:** The current benchmark JSON records Kociemba as internal, and the thesis states that all benchmark Kociemba rows used the internal backend. However, the regeneration script constructs `KociembaSolver()` through `AlgorithmComparison` without forcing `backend="internal"`. The solver default is `backend="auto"`, which can use or fall back to the optional native package under certain conditions.

**Why it matters:** Future regeneration may silently produce benchmark results that no longer match the thesis claim, depending on installed optional packages and solver behavior.

**Exact fix recommendation:** Add a `kociemba_backend` argument to `AlgorithmComparison` and `scripts/benchmarks/regenerate_thesis_benchmarks.py`. For the thesis benchmark, explicitly instantiate `KociembaSolver(backend="internal")`. Add a post-export assertion that every Kociemba row has `backend == "kociemba_internal"` and no fallback.

**Verification steps:**
Run the regeneration script in an environment with the optional native package installed. Confirm that the exported JSON still records only `kociemba_internal` for all Kociemba rows.

---

## TC-02 — Major — Thistlethwaite goal-distance cache is loaded without schema validation

**File:** `src/thistlethwaite/tables.py`
**Location:** `src/thistlethwaite/tables.py:573-593`

**Problem:** `_load_or_generate_goal_distance_table` loads an existing pickle cache and returns it without validating type, shape, dtype, sentinel values, or goal-state consistency.

**Why it matters:** A stale or corrupt cache can silently invalidate pruning distances and solver behavior. This is especially risky because the project relies on generated/cached search tables.

**Exact fix recommendation:** Validate that the loaded object is a NumPy array with the expected shape, dtype, legal distance/sentinel range, and zero distance for all expected goal coordinates. On validation failure, regenerate or fail loudly with a clear error.

**Verification steps:**
Add a regression test that writes an invalid pickle at the expected cache path and verifies that the loader rejects or regenerates it. Then run the Thistlethwaite unit tests and the full fast test profile.

---

## TC-03 — Medium — `is_in_g3` is named as a full subgroup predicate but implements only a simplified projection

**File:** `src/thistlethwaite/moves.py`
**Location:** `src/thistlethwaite/moves.py:198-201`

**Problem:** `is_in_g3` is documented as checking whether a cube is in G3, but the implementation only checks `corner_tetrad_coord == 0` and `edge_slice_coord == 0`. The adjacent comment says a full G3 check requires additional invariants.

**Why it matters:** A function named as a full subgroup predicate can be reused incorrectly by future code or cited incorrectly in the thesis.

**Exact fix recommendation:** Rename it to something like `is_in_g3_projection` or implement the full invariant check. Add tests for states that satisfy the current two coordinates but violate the missing invariants.

**Verification steps:**
Search for `is_in_g3` usages. Add unit tests covering the renamed or completed predicate and verify that the solver behavior is unchanged.

---

## TC-04 — Medium — Permutation-parity helper is mathematically under-specified

**File:** `src/thistlethwaite/moves.py`
**Location:** `src/thistlethwaite/moves.py:168-181`

**Problem:** `affects_permutation_parity` states that only quarter turns affect permutation parity and returns `modifier != '2'`. The function does not specify whether it refers to corner parity, edge parity, combined cube-move parity, or a phase-specific parity coordinate.

**Why it matters:** Parity is a mathematically sensitive concept in cube theory. Ambiguous helper names and comments can cause incorrect future use or inaccurate thesis exposition.

**Exact fix recommendation:** Rename the helper to specify the exact parity coordinate it models, or remove it if unused. Add tests documenting quarter-turn and half-turn behavior for the intended parity coordinate.

**Verification steps:**
Run `grep -R "affects_permutation_parity" src tests thesis`. Confirm all references use precise terminology and that unit tests encode the intended semantics.

---

# 4. Research/experimental issues

## RE-01 — Major — Legacy benchmark corpus contains many redundant adjacent same-face moves

**File:** `results/benchmarks/thesis/thesis_results_combined.json`; `thesis/chapters/07_evaluation.tex`
**Location:** `results/benchmarks/thesis/thesis_results_combined.json:117-119`; `results/benchmarks/thesis/thesis_results_combined.json:152-157`; `thesis/chapters/07_evaluation.tex:88`

**Problem:** The benchmark metadata explicitly records `legacy_random_all_moves_redundant_allowed`, and the first listed scramble already contains adjacent same-face cancellation/redundancy: `F'` followed by `F`. The thesis acknowledges that requested scramble length is not exact optimal depth.

**Why it matters:** Per-depth conclusions based on requested lengths 5/10/15/20 are not conclusions about uniformly sampled states at those exact depths. This weakens claims about scaling with depth.

**Exact fix recommendation:** Regenerate the primary benchmark with the current no-consecutive-same-face generator or, preferably, with an oracle-verified exact-depth corpus. Keep the legacy corpus only as a historical appendix.

**Verification steps:**
Add a corpus validation script that asserts no adjacent same-face moves and records verified optimal depth for every scramble. Rerun the benchmark and update all evaluation tables and figures.

---

## RE-02 — Major — Runtime evidence is single-run and batch-amortized, without repeated trials or confidence intervals

**File:** `thesis/chapters/07_evaluation.tex`; `results/benchmarks/thesis/thesis_results_combined.json`
**Location:** `thesis/chapters/07_evaluation.tex:125-132`; `thesis/chapters/07_evaluation.tex:180-184`; `thesis/chapters/07_evaluation.tex:376-386`; `results/benchmarks/thesis/thesis_results_combined.json:24-26`

**Problem:** The chapter acknowledges that timings are single-run batch-amortized observations, solver instances are reused, and no repetitions or confidence intervals are reported.

**Why it matters:** Mean runtime tables are vulnerable to warmup, caching, OS scheduling, and outliers. Without repetitions, statistical uncertainty cannot be assessed.

**Exact fix recommendation:** Add repeated trials per solver/scramble, separate cold-start and warm-cache measurements, and report median, IQR, and confidence intervals. Preserve the current single-run benchmark only as a preliminary or legacy result.

**Verification steps:**
Update benchmark JSON schema to include repeated observations. Recompute tables from repeated-run data and confirm the thesis reports uncertainty, not only means.

---

## RE-03 — Major — Memory comparison uses coarse shared-process RSS deltas

**File:** `src/evaluation/algorithm_comparison.py`; `thesis/chapters/07_evaluation.tex`
**Location:** `src/evaluation/algorithm_comparison.py:331`; `src/evaluation/algorithm_comparison.py:364-372`; `src/evaluation/algorithm_comparison.py:397`; `src/evaluation/algorithm_comparison.py:437-445`; `src/evaluation/algorithm_comparison.py:470`; `src/evaluation/algorithm_comparison.py:521-529`; `thesis/chapters/07_evaluation.tex:121`; `thesis/chapters/07_evaluation.tex:150`; `thesis/chapters/07_evaluation.tex:307-311`; `thesis/chapters/07_evaluation.tex:385`

**Problem:** Memory is measured as process RSS before and after each solve in a shared sequential process. The thesis acknowledges that this metric is noisy and includes shared caches and allocator effects.

**Why it matters:** The reported memory numbers are not strong evidence for precise per-solver memory usage. They are especially weak for comparing external backend behavior against in-process Python solvers.

**Exact fix recommendation:** Run each solver invocation in an isolated subprocess and record peak RSS, or use a consistent profiler such as `/usr/bin/time -v` on Unix-like systems. Report peak memory and separate persistent preprocessing/cache memory from per-solve memory.

**Verification steps:**
Add benchmark fields such as `peak_rss_mb`, `isolated_process: true`, and `cache_state`. Rebuild the memory tables and confirm the thesis no longer relies on shared-process RSS deltas for strong claims.

---

## RE-04 — Medium — Unequal timeout policies weaken direct runtime comparisons

**File:** `thesis/chapters/07_evaluation.tex`; `results/benchmarks/thesis/thesis_results_combined.json`
**Location:** `thesis/chapters/07_evaluation.tex:22-27`; `thesis/chapters/07_evaluation.tex:29-32`; `thesis/chapters/07_evaluation.tex:34-44`; `results/benchmarks/thesis/thesis_results_combined.json:12-16`

**Problem:** Thistlethwaite, Kociemba, and the external exact backend use different timeout policies: 30 seconds, 60 seconds plus a soft grace period, and 120 seconds respectively.

**Why it matters:** Different time budgets are defensible for solver-specific behavior, but they make direct runtime comparisons less clean.

**Exact fix recommendation:** Add a sensitivity experiment using a shared wall-time budget across all solvers, or explicitly separate “quality baseline under generous exact timeout” from “runtime comparison under equal timeout.”

**Verification steps:**
Run a second benchmark with equal timeout settings and include a short table comparing whether the main conclusions change.

---

# 5. Citation/reference issues

## CR-01 — Major — External optimal backend citation and provenance are not archival enough

**File:** `thesis/references.bib`; `results/benchmarks/thesis/thesis_results_combined.json`; `README.md`
**Location:** `thesis/references.bib:157-163`; `results/benchmarks/thesis/thesis_results_combined.json:136-143`; `README.md:115-117`

**Problem:** The external exact backend is cited as a GitHub/PyPI-style software reference, and the benchmark metadata records version/import/home page information. However, the metadata also states that the original benchmark did not record the wheel hash or upstream commit, and the license metadata field is null.

**Why it matters:** The external exact backend is central to the optimal-solution claims. Without an archived release identifier, wheel hash, or commit hash, exact third-party provenance is weaker than expected for a reproducibility-grade thesis.

**Exact fix recommendation:** Add a software citation for the exact archived release, including version, commit or release tag, wheel SHA256, retrieval date, and license file hash. Update benchmark metadata to include the exact wheel hash or archived source hash.

**Verification steps:**
Install the cited package version from a clean environment, compute the wheel/source hash, and confirm it matches the metadata and bibliography entry.

---

# 6. Reproducibility/setup issues

## RS-01 — Major — Thesis build environment is not deterministic enough

**File:** `docker/thesis.Dockerfile`; `thesis/README.md`; `README.md`
**Location:** `docker/thesis.Dockerfile:1-15`; `thesis/README.md:42-69`; `README.md:55-59`

**Problem:** The Dockerfile uses `debian:bookworm-slim` without a digest and installs TeX packages from moving Debian repositories without pinned versions or an apt snapshot. In the audit environment, the local build path was not ready because BibTeX/Tectonic/Docker were unavailable.

**Why it matters:** A future rebuild may use different TeX package versions and produce a different PDF or fail. The checked-in PDF is useful, but strict reproducibility requires a deterministic build environment.

**Exact fix recommendation:** Pin the Docker base image by digest and use a frozen TeX Live image or Debian snapshot. Record the image digest in the README and reproducibility manifest. Make Docker the primary reproducible build path if local TeX is optional.

**Verification steps:**
From a clean machine with Docker only, run the thesis build twice and compare the resulting PDF hash. Confirm the image digest and TeX versions are recorded.

---

## RS-02 — Medium — Python dependency lock is not cryptographic or platform-complete

**File:** `requirements.lock`; `README.md`
**Location:** `requirements.lock:1-120`; `README.md:41-44`

**Problem:** `requirements.lock` contains pinned versions, but the README correctly states that it is not a cryptographic lockfile and does not encode hashes, Python ABI, platform markers, or TeX/Tectonic binaries.

**Why it matters:** Reproducibility is weaker across machines and time, especially for packages with binary wheels or platform-specific behavior.

**Exact fix recommendation:** Generate a hash-locked dependency file using `pip-tools --generate-hashes`, `uv.lock`, or an equivalent approach. Include Python version and platform constraints in the reproducibility manifest.

**Verification steps:**
Run `pip install --require-hashes -r requirements.lock` or the equivalent locked install command in a clean Python 3.12 environment and confirm it succeeds.

---

## RS-03 — Medium — Node/npm versions are documented but not strongly enforced

**File:** `.nvmrc`; `webapp/package.json`; `README.md`
**Location:** `.nvmrc:1`; `webapp/package.json:5`; `README.md:43-44`

**Problem:** The repository records Node `v24.9.0` and npm `11.6.0`, but there is no strong enforcement in the webapp package metadata shown by the repository. A user can run `npm ci` with a different npm version.

**Why it matters:** Next.js and React toolchains are sensitive to Node/npm versions. A successful build under one version does not guarantee identical behavior under another.

**Exact fix recommendation:** Add `engines` to `webapp/package.json`, add `.npmrc` with `engine-strict=true`, and document `corepack enable && corepack prepare npm@11.6.0 --activate`.

**Verification steps:**
Run `npm ci` with an intentionally wrong Node/npm version and confirm it fails. Then run with Node `24.9.0` and npm `11.6.0` and confirm install, tests, lint, and build pass.

---

## RS-04 — Medium — Documentation test counts are stale

**File:** `docs/CODE_TO_THESIS_MAPPING.md`; `docs/THESIS_OUTLINE.md`
**Location:** `docs/CODE_TO_THESIS_MAPPING.md:189-194`; `docs/THESIS_OUTLINE.md:405-408`

**Problem:** `docs/CODE_TO_THESIS_MAPPING.md` reports `291 tests collected` and `288/291` fast tests, while `docs/THESIS_OUTLINE.md` reports `285 tests collected`. The actual audit collection reported `273/301 tests collected` with 28 deselected.

**Why it matters:** Stale verification counts undermine confidence in the documentation, even though the current tests themselves pass.

**Exact fix recommendation:** Replace hard-coded test counts with either current values generated by CI or remove exact counts from narrative documentation. Prefer linking to the verification command instead of embedding numbers.

**Verification steps:**
Run `python -m pytest tests --collect-only -q` and update the documentation to match the current collection output.

---

# 7. Submission polish issues

## SP-01 — Minor — Historical Path A document still contains stale “in progress” language

**File:** `docs/PATH_A_NATIVE_EXACT_PLAN.md`
**Location:** `docs/PATH_A_NATIVE_EXACT_PLAN.md:532-555`

**Problem:** The document is marked as historical/current-state context near the top, but the later “Immediate next slice” and completion-definition sections still read like an active unfinished implementation plan.

**Why it matters:** Reviewers may confuse historical planning notes with the current implementation state.

**Exact fix recommendation:** Move the stale plan text under a clearly titled “Historical plan, superseded” section, or update it to reflect the current native/external exact backend status.

**Verification steps:**
Search the document for “Immediate next slice”, “in progress”, and “Until then”. Confirm those sections are either removed, updated, or explicitly marked as historical.

---

## SP-02 — Minor — “rubic” typo appears in repository naming text

**File:** `README.md`; `scripts/thesis_workflow.py`
**Location:** `README.md:69`; `scripts/thesis_workflow.py:39`

**Problem:** The README layout line uses `rubicCubeThesis/`, and the Docker image constant is `rubic-cube-thesis-tex:local`.

**Why it matters:** This is minor, but visible naming typos reduce polish in a final thesis repository.

**Exact fix recommendation:** Rename visible strings to `rubikCubeThesis` / `rubik-cube-thesis-tex:local`, or use a neutral project slug consistently.

**Verification steps:**
Run `grep -R "rubic" README.md scripts thesis docs docker` and confirm no unintended occurrences remain.

---

# FIX_TARGETS

```json
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "thesis/main.tex; thesis/chapters/00_approval.tex; thesis/README.md; README.md",
    "location": "thesis/main.tex:174-180; thesis/chapters/00_approval.tex:34-44; thesis/README.md:3; README.md:8",
    "issue": "Formal approval/signature front matter is incomplete and excluded from the thesis build.",
    "exact_fix": "Fill thesis/chapters/00_approval.tex with official committee names, roles, and examination date; include it in thesis/main.tex at the institutionally required position; update README status text after completion.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py build --mode auto.",
      "Inspect the rebuilt PDF and confirm the approval page is present.",
      "Run pdftotext thesis/main.pdf - and confirm the committee names and examination date appear.",
      "Confirm no placeholder committee rows or dotfill examination-date fields remain."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "results/validation/native_exact/README.md; results/validation/native_exact/MANIFEST.json; scripts/verification/native_exact_validation.py",
    "location": "results/validation/native_exact/README.md:25-30; results/validation/native_exact/MANIFEST.json:24-28; scripts/verification/native_exact_validation.py:244-255",
    "issue": "Canonical native exact validation requires data/pattern_databases/corner_db.pkl, which is omitted from the source ZIP, so the canonical validation claim is not reproducible from the ZIP alone.",
    "exact_fix": "Provide the canonical corner_db.pkl as a hashed external artifact with retrieval instructions, or add a deterministic generation command and record the generated hash. If not provided, downgrade the thesis claim to state that only the source-ZIP smoke preset is reproducible from the submitted archive.",
    "verification_steps": [
      "From a clean extraction, run python scripts/verification/native_exact_validation.py --preset canonical --output-dir /tmp/native_exact_audit.",
      "Confirm it completes without manual artifact injection, or confirm the thesis explicitly states that canonical validation requires an external archived artifact."
    ]
  },
  {
    "severity": "Major",
    "category": "Critical blockers",
    "file": "scripts/thesis_workflow.py",
    "location": "scripts/thesis_workflow.py:878-939; scripts/thesis_workflow.py:1163-1180",
    "issue": "The validate command reports a failed thesis build path but exits with success status.",
    "exact_fix": "Make validate return a non-zero exit code whenever hard validation issues are emitted, or add a strict mode and document it as the CI/default reproducibility command.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py validate in an environment without BibTeX, Tectonic, or Docker.",
      "Confirm the command exits non-zero when it reports that no thesis build path is ready."
    ]
  },
  {
    "severity": "Major",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "thesis/chapters/07_evaluation.tex:6; thesis/chapters/07_evaluation.tex:34-44",
    "issue": "The evaluation opening says it compares three implemented algorithms, while the official optimal/Korf benchmark uses an external exact backend wrapped by the repository.",
    "exact_fix": "Change the wording to 'three solver paths' or 'two repository-implemented solvers plus an external exact optimal baseline wrapped by the repository', and repeat the distinction near the first evaluation table.",
    "verification_steps": [
      "Search thesis/chapters/07_evaluation.tex for wording equivalent to 'implemented algorithms'.",
      "Confirm each occurrence distinguishes native/internal implementation from the external optimal backend."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "thesis/chapters/07_evaluation.tex:6; thesis/chapters/07_evaluation.tex:22-27; thesis/chapters/07_evaluation.tex:88; thesis/chapters/07_evaluation.tex:125-132; thesis/chapters/07_evaluation.tex:400-404",
    "issue": "Some fairness and attribution wording is stronger than the benchmark design supports, given unequal timeouts, external backend use, redundant legacy scrambles, and single-run batch-amortized timings.",
    "exact_fix": "Qualify the evaluation conclusions as applying under the documented fixed corpus, platform, timeout policy, backend selection, and batch-amortized methodology.",
    "verification_steps": [
      "Search for terms equivalent to fair comparison, common conditions, and algorithmic attribution.",
      "Confirm those statements are bounded by the benchmark limitations already documented in the chapter."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "src/evaluation/visualizations.py; thesis/figures/*.png",
    "location": "src/evaluation/visualizations.py:204-205; src/evaluation/visualizations.py:243-244; src/evaluation/visualizations.py:284-285; src/evaluation/visualizations.py:324-325; src/evaluation/visualizations.py:347-349; src/evaluation/visualizations.py:386-388; src/evaluation/visualizations.py:417-419",
    "issue": "The generated thesis figures use English titles and axis labels inside a Greek-language thesis.",
    "exact_fix": "Add Greek label support to src/evaluation/visualizations.py or translate the thesis figure labels directly, then regenerate all thesis figures.",
    "verification_steps": [
      "Regenerate thesis figures.",
      "Open thesis/figures/fig*.png and confirm titles, axes, legends, and metric names use the same language style as the thesis text."
    ]
  },
  {
    "severity": "Major",
    "category": "Technical/code issues",
    "file": "src/evaluation/algorithm_comparison.py; src/kociemba/solver.py; scripts/benchmarks/regenerate_thesis_benchmarks.py",
    "location": "src/evaluation/algorithm_comparison.py:188; src/kociemba/solver.py:79-87; src/kociemba/solver.py:337-344; src/kociemba/solver.py:380-390; src/kociemba/solver.py:405-414; src/kociemba/solver.py:435-445; scripts/benchmarks/regenerate_thesis_benchmarks.py:223-229",
    "issue": "The thesis benchmark regeneration path does not force Kociemba's internal backend even though the thesis and current JSON describe all Kociemba benchmark rows as internal.",
    "exact_fix": "Add a kociemba_backend parameter and CLI flag; instantiate KociembaSolver(backend='internal') for thesis regeneration; add an export assertion that every Kociemba row records kociemba_internal and no fallback.",
    "verification_steps": [
      "Install the optional native package in a clean environment.",
      "Rerun the thesis benchmark regeneration command.",
      "Assert that every exported Kociemba result has backend equal to kociemba_internal."
    ]
  },
  {
    "severity": "Major",
    "category": "Technical/code issues",
    "file": "src/thistlethwaite/tables.py",
    "location": "src/thistlethwaite/tables.py:573-593",
    "issue": "The Thistlethwaite goal-distance pickle cache is loaded without validating object type, dtype, shape, sentinel range, or goal-state consistency.",
    "exact_fix": "Validate loaded cache structure and contents before returning it; regenerate or fail loudly when validation fails.",
    "verification_steps": [
      "Add a regression test that writes an invalid pickle at the expected cache path.",
      "Confirm the loader rejects or regenerates the invalid cache.",
      "Run the Thistlethwaite unit tests and full fast test profile."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/thistlethwaite/moves.py",
    "location": "src/thistlethwaite/moves.py:198-201",
    "issue": "is_in_g3 is named as a full G3 subgroup predicate but implements only a simplified projection over two coordinates.",
    "exact_fix": "Rename the function to describe the projection it checks, or implement the full G3 invariant predicate and add tests for missing-invariant cases.",
    "verification_steps": [
      "Search for all is_in_g3 usages.",
      "Add tests for states that satisfy the current two-coordinate check but violate the missing invariants.",
      "Confirm solver behavior and tests remain correct."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/thistlethwaite/moves.py",
    "location": "src/thistlethwaite/moves.py:168-181",
    "issue": "affects_permutation_parity has ambiguous parity terminology and does not specify the exact parity coordinate being modeled.",
    "exact_fix": "Rename the helper to specify the modeled parity coordinate or remove it if unused; add tests documenting quarter-turn and half-turn behavior for the intended parity concept.",
    "verification_steps": [
      "Run grep -R \"affects_permutation_parity\" src tests thesis.",
      "Confirm all references use precise parity terminology.",
      "Run the added parity-semantics tests."
    ]
  },
  {
    "severity": "Major",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "results/benchmarks/thesis/thesis_results_combined.json:117-119; results/benchmarks/thesis/thesis_results_combined.json:152-157; thesis/chapters/07_evaluation.tex:88",
    "issue": "The primary benchmark corpus is a legacy random-move corpus that permits adjacent same-face redundancy, so requested scramble length is not exact depth.",
    "exact_fix": "Regenerate the primary benchmark using no-consecutive-same-face scrambles or an oracle-verified exact-depth corpus; retain the legacy corpus only as a historical appendix.",
    "verification_steps": [
      "Run a corpus validation script that asserts no adjacent same-face moves.",
      "Record verified optimal depth for every scramble.",
      "Rerun benchmarks and update all evaluation tables and figures."
    ]
  },
  {
    "severity": "Major",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "thesis/chapters/07_evaluation.tex:125-132; thesis/chapters/07_evaluation.tex:180-184; thesis/chapters/07_evaluation.tex:376-386; results/benchmarks/thesis/thesis_results_combined.json:24-26",
    "issue": "Runtime evidence is based on single-run batch-amortized observations without repetitions, cold/warm separation, or confidence intervals.",
    "exact_fix": "Add repeated trials per solver and scramble, separate cold-start from warm-cache timing, and report median, IQR, and confidence intervals.",
    "verification_steps": [
      "Update benchmark JSON schema to store repeated observations.",
      "Recompute timing tables from repeated-run data.",
      "Confirm the thesis reports uncertainty intervals rather than only means."
    ]
  },
  {
    "severity": "Major",
    "category": "Research/experimental issues",
    "file": "src/evaluation/algorithm_comparison.py; thesis/chapters/07_evaluation.tex",
    "location": "src/evaluation/algorithm_comparison.py:331; src/evaluation/algorithm_comparison.py:364-372; src/evaluation/algorithm_comparison.py:397; src/evaluation/algorithm_comparison.py:437-445; src/evaluation/algorithm_comparison.py:470; src/evaluation/algorithm_comparison.py:521-529; thesis/chapters/07_evaluation.tex:121; thesis/chapters/07_evaluation.tex:150; thesis/chapters/07_evaluation.tex:307-311; thesis/chapters/07_evaluation.tex:385",
    "issue": "Memory comparison uses shared-process before/after RSS deltas, which are too coarse for strong per-solver memory claims.",
    "exact_fix": "Run solver invocations in isolated subprocesses and record peak RSS, separating persistent preprocessing/cache memory from per-solve memory.",
    "verification_steps": [
      "Add fields such as peak_rss_mb, isolated_process, and cache_state to benchmark output.",
      "Rebuild memory tables from isolated-process measurements.",
      "Confirm thesis memory claims are limited to the new measurement method."
    ]
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "thesis/chapters/07_evaluation.tex:22-27; thesis/chapters/07_evaluation.tex:29-32; thesis/chapters/07_evaluation.tex:34-44; results/benchmarks/thesis/thesis_results_combined.json:12-16",
    "issue": "The solvers use unequal timeout policies, weakening direct runtime comparisons.",
    "exact_fix": "Add a sensitivity experiment with equal wall-time budgets, or separate the exact solver's role as a quality baseline from runtime comparison tables.",
    "verification_steps": [
      "Run a second benchmark with equal timeout settings.",
      "Add a table showing whether conclusions change under equal time budgets."
    ]
  },
  {
    "severity": "Major",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; results/benchmarks/thesis/thesis_results_combined.json; README.md",
    "location": "thesis/references.bib:157-163; results/benchmarks/thesis/thesis_results_combined.json:136-143; README.md:115-117",
    "issue": "The external optimal backend citation and benchmark provenance do not include an archived release identifier, wheel hash, or upstream commit hash.",
    "exact_fix": "Add an exact software citation with version, release tag or commit, wheel/source SHA256, retrieval date, and license information; update benchmark metadata accordingly.",
    "verification_steps": [
      "Install the cited package version in a clean environment.",
      "Compute the wheel or source hash.",
      "Confirm the hash, version, and license metadata match the bibliography and benchmark metadata."
    ]
  },
  {
    "severity": "Major",
    "category": "Reproducibility/setup issues",
    "file": "docker/thesis.Dockerfile; thesis/README.md; README.md",
    "location": "docker/thesis.Dockerfile:1-15; thesis/README.md:42-69; README.md:55-59",
    "issue": "The thesis build environment is not pinned deterministically; the Dockerfile uses an unpinned Debian tag and moving apt package sources.",
    "exact_fix": "Pin the Docker base image by digest and use a frozen TeX Live image or Debian snapshot; record image digest and TeX versions in the reproducibility manifest.",
    "verification_steps": [
      "Build the thesis twice from a clean Docker-only machine.",
      "Compare resulting PDF hashes.",
      "Confirm the image digest and TeX versions are recorded."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "requirements.lock; README.md",
    "location": "requirements.lock:1-120; README.md:41-44",
    "issue": "The Python dependency lock is version-pinned but not cryptographic or platform-complete.",
    "exact_fix": "Generate a hash-locked dependency file using pip-tools --generate-hashes, uv.lock, or equivalent, and include Python ABI/platform constraints.",
    "verification_steps": [
      "Run pip install --require-hashes -r requirements.lock or the equivalent locked install command in a clean Python 3.12 environment.",
      "Confirm all dependencies install reproducibly."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": ".nvmrc; webapp/package.json; README.md",
    "location": ".nvmrc:1; webapp/package.json:5; README.md:43-44",
    "issue": "Node and npm versions are documented but not strongly enforced during webapp installation.",
    "exact_fix": "Add package.json engines, add .npmrc with engine-strict=true, and document corepack activation for npm 11.6.0.",
    "verification_steps": [
      "Run npm ci with an intentionally wrong Node/npm version and confirm it fails.",
      "Run npm ci, npm test, npm run lint, and npm run build with Node 24.9.0 and npm 11.6.0 and confirm all pass."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "docs/CODE_TO_THESIS_MAPPING.md; docs/THESIS_OUTLINE.md",
    "location": "docs/CODE_TO_THESIS_MAPPING.md:189-194; docs/THESIS_OUTLINE.md:405-408",
    "issue": "Documentation contains stale test-count claims that do not match the current pytest collection output.",
    "exact_fix": "Update the hard-coded test counts to the current collection output or remove exact counts and document the verification command instead.",
    "verification_steps": [
      "Run python -m pytest tests --collect-only -q.",
      "Confirm the documentation matches the current collection output or no longer embeds stale counts."
    ]
  },
  {
    "severity": "Minor",
    "category": "Submission polish issues",
    "file": "docs/PATH_A_NATIVE_EXACT_PLAN.md",
    "location": "docs/PATH_A_NATIVE_EXACT_PLAN.md:532-555",
    "issue": "Historical Path A documentation still contains active-sounding 'Immediate next slice' and 'in progress' language.",
    "exact_fix": "Move those sections under a clearly marked historical/superseded heading or update them to reflect the current native/external exact backend status.",
    "verification_steps": [
      "Search for 'Immediate next slice', 'in progress', and 'Until then'.",
      "Confirm those statements are removed, updated, or explicitly marked as historical."
    ]
  },
  {
    "severity": "Minor",
    "category": "Submission polish issues",
    "file": "README.md; scripts/thesis_workflow.py",
    "location": "README.md:69; scripts/thesis_workflow.py:39",
    "issue": "The typo 'rubic' appears in repository naming text and the Docker image constant.",
    "exact_fix": "Rename visible strings to use 'rubik' consistently or choose a neutral project slug.",
    "verification_steps": [
      "Run grep -R \"rubic\" README.md scripts thesis docs docker.",
      "Confirm no unintended occurrences remain."
    ]
  }
]
```

---

## Scores

**Overall thesis quality score:** 78 / 100
The thesis is substantially stronger than a typical draft: the evaluation chapter is unusually transparent about limitations, citations are internally consistent, the PDF is readable, and the benchmark data mostly matches the thesis tables. The main deductions are for incomplete institutional front matter, over-strong framing in places, figure-language inconsistency, and experimental limitations.

**Technical quality score:** 81 / 100
The Python tests, notebook checks, and webapp build are in good condition. The architecture is reasonably modular. Deductions come from backend pinning risk, unvalidated cache loading, ambiguous subgroup/parity helpers, and measurement methodology weaknesses.

**Submission readiness score:** 59 / 100
The repository is close to a strong technical submission, but not ready for final thesis submission because the approval page is incomplete/excluded, canonical validation is not reproducible from the ZIP alone, the thesis build path is not robustly validated, and several reproducibility claims need stronger artifact pinning.
