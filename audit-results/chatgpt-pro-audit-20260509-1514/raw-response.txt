## Audit basis

I audited the extracted uploaded ZIP only: `/mnt/data/repo-audit-20260509-1404.zip`. I did not use GitHub or external repositories and did not modify files.

Verified during audit:

* `python -m pytest tests -q` completed with `276 passed, 1 skipped, 28 deselected`.
* The repository manifest’s listed file hashes matched the current files it lists.
* The committed benchmark tables in the thesis are broadly consistent with the committed benchmark JSON.
* The audit still found several real blockers and reproducibility/claim-alignment problems below.

---

# 1. Critical blockers

## C1 — Final institutional approval page is incomplete and excluded

* **Severity:** Critical
* **File:** `thesis/main.tex`
* **Location:** lines `178-179`
* **Problem:** The thesis explicitly excludes the approval/signature page: “Approval/signature page intentionally excluded until official committee names and exam date are supplied.”
* **Why it matters:** This is a submission blocker. The repository also acknowledges this at `README.md:7-8` and `thesis/README.md:3`. The existing approval file contains placeholders at `thesis/chapters/00_approval.tex:36-44`.
* **Exact fix recommendation:** Complete `thesis/chapters/00_approval.tex` with official committee members and examination date, include it from `thesis/main.tex`, rebuild `thesis/main.pdf`, and update the README claim that final institutional front matter is pending.
* **Verification steps:** Confirm `thesis/main.tex` includes `chapters/00_approval.tex`; confirm no `\dotfill` placeholders remain in `00_approval.tex`; rebuild the PDF and verify the approval page appears in the front matter.

## C2 — Benchmark metadata contains a stale/circular reproducibility manifest hash

* **Severity:** Critical
* **File:** `results/benchmarks/thesis/thesis_results_combined.json`
* **Location:** line `145`
* **Problem:** The JSON records `reproducibility_manifest_sha256` as `b680fa72d060f073e8d88cfdb6bf2222da3fa69e2599c5fd3fb2841a82224a9e`, but the current `REPRODUCIBILITY_MANIFEST.json` hash is `6845e433e1d67fdc790363a66adf6e8ec2799eb2b9e719051f10538014a7a08a`.
* **Why it matters:** This breaks the provenance claim for the main benchmark artifact. It is also structurally circular because the manifest hashes benchmark artifacts while a benchmark artifact embeds the manifest hash.
* **Exact fix recommendation:** Remove the manifest hash from benchmark JSON, or move package-level manifest hashes to an external audit/provenance file that is not itself part of the hashed benchmark set. Then regenerate the manifest and benchmark metadata consistently.
* **Verification steps:** Recompute `sha256sum REPRODUCIBILITY_MANIFEST.json`; verify no committed benchmark JSON embeds an obsolete manifest hash; run the repository’s manifest verification script/check and confirm all listed hashes pass.

---

# 2. Thesis writing issues

## T1 — A*/IDA* optimality table omits the admissibility condition

* **Severity:** Medium
* **File:** `thesis/chapters/05_korf.tex`
* **Location:** lines `43-58`, especially line `52`
* **Problem:** The table says A* and IDA* have optimality “Ναι” without qualifying that this depends on an admissible/consistent heuristic.
* **Why it matters:** The surrounding text discusses admissibility, but the table itself is technically over-broad. A non-admissible heuristic can break optimality.
* **Exact fix recommendation:** Change the table entry to “Ναι, εφόσον η ευρετική είναι αποδεκτή” or equivalent.
* **Verification steps:** Rebuild the thesis and inspect the A*/IDA* comparison table in Chapter 5.

## T2 — Thesis “Manhattan distance” formula does not match the implementation

* **Severity:** High
* **File:** `thesis/chapters/06_heuristics.tex`
* **Location:** lines `152-163`
* **Problem:** The thesis defines the heuristic as a sum of minimum moves per piece plus orientation penalty. The implementation in `src/korf/heuristics.py:96-189` instead counts misplaced corner/edge positions and nonzero orientations, then normalizes.
* **Why it matters:** This is a mathematical and implementation-claim mismatch. The thesis describes a stronger/different heuristic than the one actually implemented.
* **Exact fix recommendation:** Either rewrite the thesis to describe the actual mismatch/orientation-count heuristic, or implement the stated piece-distance heuristic with explicit distance tables and tests.
* **Verification steps:** Compare `thesis/chapters/06_heuristics.tex:152-163` with `src/korf/heuristics.py:96-189`; add a unit test showing the documented formula matches computed values.

## T3 — Composite heuristic strategy table omits the fallback used by code

* **Severity:** Medium
* **File:** `thesis/chapters/06_heuristics.tex`
* **Location:** lines `351-362`
* **Problem:** The table says high-entropy states use “Pattern DBs”, but the implementation falls back to enhanced Manhattan when pattern databases are missing or unusable.
* **Why it matters:** In the source ZIP, pattern database availability is conditional. The table overstates what the runtime strategy actually guarantees.
* **Exact fix recommendation:** Change the high-entropy row to “Pattern DBs when available; otherwise enhanced Manhattan” and reference the fallback behavior.
* **Verification steps:** Compare the updated table against `src/korf/composite_heuristic.py:232-250` and `src/korf/composite_heuristic.py:322-352`.

## T4 — Several source-line references in the thesis are stale

* **Severity:** Medium
* **File:** `thesis/chapters/05_korf.tex`
* **Location:** lines `104-105` and `381-382`
* **Problem:** The thesis cites `corner_index` as `src/korf/corner_database.py` lines `38-59`, but the function is actually at `src/korf/corner_database.py:56-77`. It also cites `_is_redundant_move` as `src/korf/a_star.py` lines `418-431`; the A* version is at `237-267` and the IDA* version is at `446-459`.
* **Why it matters:** Stale line references damage reproducibility and make reviewer verification harder.
* **Exact fix recommendation:** Correct the cited line ranges or avoid fragile exact line ranges by referring to function names plus file paths.
* **Verification steps:** Grep for `corner_index` and `_is_redundant_move`; verify all thesis references point to the current source locations.

## T5 — One heuristic listing caption has a stale source-line reference

* **Severity:** Low
* **File:** `thesis/chapters/06_heuristics.tex`
* **Location:** line `172`
* **Problem:** The caption cites `src/korf/heuristics.py` lines `169-192`, while `manhattan_distance` is currently at `src/korf/heuristics.py:166-189`.
* **Why it matters:** This is a small but real traceability defect.
* **Exact fix recommendation:** Update the line range or cite only the function name.
* **Verification steps:** Grep for `def manhattan_distance`; confirm the thesis caption matches the current implementation.

## T6 — Efficiency metric is introduced but not used in the evaluation

* **Severity:** Medium
* **File:** `thesis/chapters/06_heuristics.tex`
* **Location:** lines `77-81`
* **Problem:** The thesis defines an efficiency index `η`, but the later evaluation does not report or use this metric.
* **Why it matters:** Introducing unused metrics creates the impression of an analysis that was not actually performed.
* **Exact fix recommendation:** Either remove the metric definition or add an evaluation table computing `η` for the compared heuristics/solvers.
* **Verification steps:** Search the thesis for subsequent uses of `η`; confirm either it is removed or reported with data.

---

# 3. Technical/code issues

## C3 — External Korf backend stats are lost when `verbose=True`

* **Severity:** Medium
* **File:** `src/korf/optimal_solver.py`
* **Location:** lines `267-288`, parser at `368-391`
* **Problem:** Backend stdout is captured only when `verbose` is false. When `verbose=True`, backend output goes directly to stdout and `backend_output` remains empty, so `_parse_backend_output` cannot extract nodes/depth statistics.
* **Why it matters:** Verbose runs silently lose statistics, which can corrupt diagnostics and benchmark metadata.
* **Exact fix recommendation:** Always capture backend stdout into a buffer, then optionally echo it when `verbose=True`.
* **Verification steps:** Add a test backend that prints `nodes generated: 42`; call `solve(verbose=True)` and verify `stats["nodes_generated"] == 42`.

## C4 — IDA* timeout is conflated with no-solution/incomplete search

* **Severity:** Medium
* **File:** `src/korf/a_star.py`
* **Location:** lines `361-375` and `405-408`
* **Problem:** `_search` returns `float('inf')` on timeout, and the outer loop treats `float('inf')` as “No solution exists.” This conflates timeout, depth exhaustion, and genuine unsolvability.
* **Why it matters:** Solver outcomes become ambiguous. For Rubik’s Cube, “no solution” is usually not the right interpretation for a legal cube; timeout/incomplete should be explicit.
* **Exact fix recommendation:** Return a distinct timeout sentinel or exception and record `timed_out`, `depth_limit_reached`, and `solution_found` separately in stats.
* **Verification steps:** Add a forced-short-timeout test and confirm the returned result/stats explicitly indicate timeout rather than no solution.

## C5 — A*/IDA* memory statistics are rough constants, not measured memory

* **Severity:** Medium
* **File:** `src/korf/a_star.py`
* **Location:** lines `160-163`, `269-289`, and `461-470`
* **Problem:** A* estimates memory as “100 states per MB,” and IDA* reports a constant `estimated_memory_mb: 0.1`.
* **Why it matters:** These fields look quantitative but are not real memory measurements. They can mislead users or future evaluations.
* **Exact fix recommendation:** Rename these fields to clearly indicate rough estimates, or replace them with measured RSS/tracemalloc/psutil values.
* **Verification steps:** Run a solver instance and confirm reported memory fields are either measured or explicitly labeled as estimates.

## C6 — `PatternDatabase.save()` fails for basename-only paths

* **Severity:** Medium
* **File:** `src/korf/pattern_database.py`
* **Location:** lines `168-175`
* **Problem:** `save()` calls `os.makedirs(os.path.dirname(filepath), exist_ok=True)`. If `filepath` is just `corner_db.pkl`, `os.path.dirname(filepath)` is empty and `os.makedirs("")` raises `FileNotFoundError`.
* **Why it matters:** The API is brittle and fails for a common valid-looking filename.
* **Exact fix recommendation:** Guard the directory creation: only call `os.makedirs` when the dirname is non-empty.
* **Verification steps:** Add a unit test that saves to a basename-only temporary working directory path and reloads successfully.

## C7 — `RubikCube` accepts invalid externally supplied states without validation

* **Severity:** Medium
* **File:** `src/cube/rubik_cube.py`
* **Location:** lines `67-80`
* **Problem:** The constructor copies a supplied `state` but does not validate shape, sticker values, sticker counts, or center consistency.
* **Why it matters:** Invalid cube states can enter solvers/converters and produce undefined or misleading behavior.
* **Exact fix recommendation:** Validate shape `(6, 9)`, integer sticker range, exactly nine stickers per color, and fixed center consistency, or document that the constructor accepts unchecked internal states only.
* **Verification steps:** Add tests for invalid shape, invalid color value, wrong sticker counts, and invalid centers.

## C8 — Kociemba solver prints during quiet initialization

* **Severity:** Low
* **File:** `src/kociemba/solver.py`
* **Location:** lines `120-137`
* **Problem:** `_initialize()` prints initialization messages unconditionally, even though `solve()` has a `verbose=False` default.
* **Why it matters:** Quiet benchmark/test runs can be polluted by unexpected stdout.
* **Exact fix recommendation:** Thread the `verbose` setting into initialization or replace unconditional prints with logging controlled by verbosity.
* **Verification steps:** Capture stdout during a first `solve(verbose=False)` call and verify it is empty.

## C9 — Composite heuristic code documentation overclaims learning behavior

* **Severity:** Medium
* **File:** `src/korf/composite_heuristic.py`
* **Location:** lines `130-143`
* **Problem:** The class docstring claims “better estimates across varying scramble depths” and “learning-based adjustment factors,” but the implementation is rule-based and does not learn adjustment factors.
* **Why it matters:** The source documentation overstates the implemented method and conflicts with the thesis’s more cautious framing.
* **Exact fix recommendation:** Rewrite the docstring to state that this is an exploratory rule-based selector with fallback behavior and no proven learning component.
* **Verification steps:** Grep for “learning-based” and “better estimates”; confirm claims are removed or backed by actual implementation/tests.

---

# 4. Research/experimental issues

## R1 — Benchmark “depth” is requested scramble length, not verified optimal distance

* **Severity:** High
* **File:** `thesis/chapters/07_evaluation.tex`
* **Location:** lines `88-90`
* **Problem:** The thesis admits the legacy corpus can contain redundant moves and that requested scramble length is not exact optimal distance. The committed JSON also marks `legacy_generator_redundant_moves: true` at `results/benchmarks/thesis/thesis_results_combined.json:115-119`.
* **Why it matters:** Results grouped by “depth” can be misleading. A nominal depth-20 scramble may be easier than a true depth-20 instance.
* **Exact fix recommendation:** Either regenerate the benchmark corpus with canonical nonredundant exact-depth instances, or relabel all analysis as “requested scramble length” and include verified-depth distributions.
* **Verification steps:** Inspect generated scrambles for adjacent same-face cancellations; compute verified optimal depths for a representative subset; update tables/axis labels accordingly.

## R2 — Main benchmark lacks repeated runs, confidence intervals, and cold/warm split

* **Severity:** High
* **File:** `thesis/chapters/07_evaluation.tex`
* **Location:** lines `125-136` and `380-390`
* **Problem:** The thesis states that there were no multiple repetitions/statistical intervals, no cold/warm split, and incomplete original environment/package provenance.
* **Why it matters:** Time comparisons are not statistically strong enough for robust performance conclusions.
* **Exact fix recommendation:** Add repeated benchmark runs, report mean/median/std or confidence intervals, separate cold-start from warmed-cache timing, and preserve environment metadata at run time.
* **Verification steps:** Regenerate benchmark JSON with per-run samples and environment metadata; update Chapter 7 tables to include variability.

## R3 — Korf benchmark performance is for an external exact backend, not the native implementation

* **Severity:** High
* **File:** `thesis/chapters/07_evaluation.tex`
* **Location:** lines `34-42`
* **Problem:** The thesis states the Korf benchmark uses an external exact backend, while the repository also contains native exact solver code. The benchmark therefore does not measure the native Korf implementation as an implementation artifact.
* **Why it matters:** Readers may attribute external backend performance to the thesis implementation unless the distinction is made very explicit everywhere performance is discussed.
* **Exact fix recommendation:** Reframe Korf benchmark results as “external exact reference backend” results, and add a separate native exact benchmark on a feasible smaller corpus if implementation performance is claimed.
* **Verification steps:** Search all Korf performance claims; confirm each says external backend/reference where applicable; add native benchmark JSON or remove native-performance implications.

## R4 — Native exact validation claim is not fully reproducible from the uploaded source ZIP

* **Severity:** High
* **File:** `results/validation/native_exact/README.md`
* **Location:** lines `25-30`
* **Problem:** The canonical validation command depends on `data/pattern_databases/corner_db.pkl`, which is not provided in the source ZIP. The script hard-fails this prerequisite at `scripts/verification/native_exact_validation.py:252-263`.
* **Why it matters:** The archived validation result may be present, but the central native exact validation claim cannot be fully reproduced from this uploaded ZIP alone.
* **Exact fix recommendation:** Include the required corner database as a separately hashed artifact, provide a deterministic generation procedure with expected hash/size/runtime, or demote the canonical claim and clearly label the available source-ZIP path as a smoke validation only.
* **Verification steps:** From a clean extraction, run the canonical validation command; confirm it either succeeds because the required artifact exists or the thesis/README no longer claims full source-only reproducibility.

---

# 5. Citation/reference issues

## CR1 — Chapter 8 makes implementation and validation claims without citations/cross-references

* **Severity:** Medium
* **File:** `thesis/chapters/08_implementation.tex`
* **Location:** lines `184-190` and `220-241`
* **Problem:** Chapter 8 discusses native validation results, tests, reproducibility, and JSON exports but contains no citation commands and limited formal cross-reference anchoring to the exact artifacts.
* **Why it matters:** For an implementation-heavy thesis, artifact-backed claims need traceable references to benchmark JSON, validation manifests, test reports, and repository files.
* **Exact fix recommendation:** Add explicit cross-references to the validation manifest, benchmark manifest, test configuration, and reproducibility manifest, or add appendix references that make these claims auditable.
* **Verification steps:** Grep Chapter 8 for citation/cross-reference commands; verify claims at lines `184-190` and `220-241` point to exact artifacts.

---

# 6. Reproducibility/setup issues

## RS1 — Python dependency lock is not cryptographic and lacks platform/ABI constraints

* **Severity:** Medium
* **File:** `README.md`
* **Location:** lines `41-43`
* **Problem:** The README acknowledges that `requirements.lock` is not a cryptographic lock and lacks hashes, platform markers, Python ABI constraints, and TeX/Tectonic version pinning.
* **Why it matters:** A future reviewer may not be able to reconstruct the exact environment that produced the results.
* **Exact fix recommendation:** Use a hash-locked dependency mechanism such as `pip-tools --generate-hashes`, `uv lock`, or a Conda lock file; record Python ABI and OS constraints.
* **Verification steps:** Recreate the environment in a clean container using only the lock file and verify all packages install with hash checking.

## RS2 — Thesis Docker image pins Debian base digest but not apt package versions

* **Severity:** Medium
* **File:** `docker/thesis.Dockerfile`
* **Location:** lines `5-15`
* **Problem:** The Dockerfile pins the Debian base image digest, but TeX and build packages are installed from Debian repositories at build time without snapshot pinning.
* **Why it matters:** Rebuilding the same Dockerfile later may produce different TeX/package versions and potentially different PDF output.
* **Exact fix recommendation:** Use Debian snapshot repositories, pin package versions, or publish and reference a built image digest for the thesis build environment.
* **Verification steps:** Rebuild the Docker image twice in clean environments and compare package versions and `thesis/main.pdf` hash.

---

# 7. Submission polish issues

## SP1 — Final PDF is not tagged for accessibility

* **Severity:** Low
* **File:** `thesis/main.pdf`
* **Location:** PDF metadata, `Tagged: no`
* **Problem:** The generated PDF is untagged.
* **Why it matters:** Some institutional or archival submission systems expect tagged/accessibility-aware PDFs, and untagged PDFs are weaker for accessibility review.
* **Exact fix recommendation:** Produce a tagged/accessibility-compliant PDF if required by the institution, or document that the institution does not require tagging.
* **Verification steps:** Run `pdfinfo thesis/main.pdf` and confirm `Tagged: yes`, or attach the relevant institutional exemption.

---

# FIX_TARGETS

```json
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "thesis/main.tex",
    "location": "lines 178-179; related placeholders in thesis/chapters/00_approval.tex:36-44",
    "issue": "The final institutional approval/signature page is incomplete and intentionally excluded from the thesis build.",
    "exact_fix": "Complete thesis/chapters/00_approval.tex with official committee members and examination date, include it from thesis/main.tex, rebuild thesis/main.pdf, and update README.md so it no longer says final front matter is pending.",
    "verification_steps": [
      "Confirm thesis/main.tex includes chapters/00_approval.tex.",
      "Confirm thesis/chapters/00_approval.tex has no dotfill or committee placeholders.",
      "Rebuild thesis/main.pdf and verify the approval page appears in the front matter."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "results/benchmarks/thesis/thesis_results_combined.json",
    "location": "line 145",
    "issue": "The benchmark metadata embeds a stale reproducibility_manifest_sha256 value and creates circular provenance because the manifest also hashes benchmark artifacts.",
    "exact_fix": "Remove the manifest hash from benchmark JSON or move it to an external provenance file that is not part of the hashed benchmark set. Regenerate benchmark metadata and REPRODUCIBILITY_MANIFEST.json consistently.",
    "verification_steps": [
      "Run sha256sum REPRODUCIBILITY_MANIFEST.json.",
      "Verify no benchmark JSON embeds an obsolete manifest hash.",
      "Run the repository manifest verification check and confirm all listed hashes pass."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/06_heuristics.tex",
    "location": "lines 152-163; implementation at src/korf/heuristics.py:96-189",
    "issue": "The thesis defines a Manhattan-style heuristic using minimum per-piece move distances, but the implementation counts misplaced positions and orientation flags.",
    "exact_fix": "Either rewrite the thesis to describe the actual mismatch/orientation-count heuristic or implement the stated distance-table heuristic with tests.",
    "verification_steps": [
      "Compare thesis/chapters/06_heuristics.tex:152-163 with src/korf/heuristics.py:96-189.",
      "Add a unit test showing documented heuristic values match implementation values.",
      "Rebuild the thesis after updating the formula or code."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 88-90; related metadata in results/benchmarks/thesis/thesis_results_combined.json:115-119",
    "issue": "Benchmark depth is requested scramble length, not verified optimal distance, and the legacy corpus can contain redundant moves.",
    "exact_fix": "Regenerate the corpus with canonical nonredundant exact-depth instances, or relabel all tables and discussion as requested scramble length and add verified-depth distributions.",
    "verification_steps": [
      "Inspect benchmark scrambles for adjacent same-face redundancies.",
      "Compute verified optimal depths for a representative subset.",
      "Update Chapter 7 labels and discussion to match the actual corpus semantics."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 125-136 and 380-390",
    "issue": "The benchmark lacks repeated runs, confidence intervals, cold/warm timing separation, and complete original environment provenance.",
    "exact_fix": "Rerun benchmarks with multiple repetitions, report variability, separate cold-start and warmed-cache timing, and record package/backend/environment metadata at run time.",
    "verification_steps": [
      "Regenerate benchmark JSON with per-run timing samples.",
      "Verify Chapter 7 reports mean or median plus variability.",
      "Verify benchmark metadata includes environment and backend provenance captured during the run."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "lines 34-42",
    "issue": "Korf benchmark performance is reported for an external exact backend, not for the repository's native exact solver implementation.",
    "exact_fix": "Reframe all Korf performance results as external exact reference backend results, and add a separate native exact benchmark on a feasible corpus if native implementation performance is claimed.",
    "verification_steps": [
      "Search thesis and README for Korf performance claims.",
      "Confirm each claim distinguishes external backend results from native implementation results.",
      "Add native benchmark artifacts or remove native-performance implications."
    ]
  },
  {
    "severity": "High",
    "category": "Reproducibility/setup issues",
    "file": "results/validation/native_exact/README.md",
    "location": "lines 25-30; hard prerequisite check at scripts/verification/native_exact_validation.py:252-263",
    "issue": "The canonical native exact validation depends on data/pattern_databases/corner_db.pkl, which is not included in the uploaded source ZIP.",
    "exact_fix": "Include the required corner database as a separately hashed artifact, provide a deterministic generation procedure with expected hash/size/runtime, or demote the canonical validation claim to archived-result status and clearly label the source-ZIP command as smoke-only.",
    "verification_steps": [
      "Extract the ZIP into a clean directory.",
      "Run the canonical native exact validation command.",
      "Confirm it succeeds from provided artifacts, or confirm the documentation no longer claims full source-only reproducibility."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/05_korf.tex",
    "location": "lines 43-58, especially line 52",
    "issue": "The A*/IDA* comparison table says both algorithms are optimal without stating the admissible-heuristic condition.",
    "exact_fix": "Change the optimality entries to state that optimality holds only when the heuristic is admissible, and preferably consistent where relevant.",
    "verification_steps": [
      "Rebuild the thesis.",
      "Inspect the A*/IDA* comparison table in Chapter 5.",
      "Confirm the admissibility condition appears in the table."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/06_heuristics.tex",
    "location": "lines 351-362; implementation at src/korf/composite_heuristic.py:232-250 and 322-352",
    "issue": "The composite heuristic strategy table says high-entropy states use Pattern DBs but omits the implemented fallback to enhanced Manhattan.",
    "exact_fix": "Update the high-entropy table row to say Pattern DBs are used when available and enhanced Manhattan is used otherwise.",
    "verification_steps": [
      "Compare the table with src/korf/composite_heuristic.py fallback logic.",
      "Rebuild the thesis.",
      "Confirm the table states the conditional behavior."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/05_korf.tex",
    "location": "lines 104-105 and 381-382",
    "issue": "The thesis contains stale source-line references for corner_index and _is_redundant_move.",
    "exact_fix": "Update the corner_index reference to src/korf/corner_database.py:56-77 and update the _is_redundant_move references to the current A*/IDA* locations, or cite function names without exact line ranges.",
    "verification_steps": [
      "Grep for def corner_index and def _is_redundant_move.",
      "Verify Chapter 5 references match the current source locations.",
      "Rebuild the thesis."
    ]
  },
  {
    "severity": "Low",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/06_heuristics.tex",
    "location": "line 172",
    "issue": "The manhattan_distance listing caption cites stale source lines.",
    "exact_fix": "Update the caption to cite src/korf/heuristics.py:166-189 or remove the fragile exact line range.",
    "verification_steps": [
      "Grep for def manhattan_distance.",
      "Confirm the caption points to the current function location.",
      "Rebuild the thesis."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/06_heuristics.tex",
    "location": "lines 77-81",
    "issue": "The efficiency index eta is introduced but not used in the later evaluation.",
    "exact_fix": "Remove the metric definition or add an evaluation table computing eta for the compared heuristic strategies.",
    "verification_steps": [
      "Search the thesis for subsequent uses of eta.",
      "Confirm the metric is either removed or supported by reported data."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/optimal_solver.py",
    "location": "lines 267-288; parser at lines 368-391",
    "issue": "External backend stdout is not captured when verbose=True, so parsed backend statistics are lost.",
    "exact_fix": "Always capture backend stdout into a buffer, and optionally echo the captured output when verbose=True.",
    "verification_steps": [
      "Add a fake backend that prints nodes generated: 42.",
      "Call solve(verbose=True).",
      "Verify the returned stats include nodes_generated equal to 42."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/a_star.py",
    "location": "lines 361-375 and 405-408",
    "issue": "IDA* returns float('inf') for timeout and the outer loop treats that as no solution, conflating timeout, incompleteness, and unsolvability.",
    "exact_fix": "Introduce a distinct timeout result or exception and record timed_out, depth_limit_reached, and solution_found separately.",
    "verification_steps": [
      "Add a forced-timeout unit test.",
      "Verify the solver reports timeout explicitly.",
      "Verify timeout is not described as no solution."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/a_star.py",
    "location": "lines 160-163, 269-289, and 461-470",
    "issue": "A* and IDA* memory statistics are rough estimates or constants rather than measured memory.",
    "exact_fix": "Rename the fields to make them explicitly approximate or replace them with measured RSS/tracemalloc/psutil values.",
    "verification_steps": [
      "Run A* and IDA* on a small cube.",
      "Inspect the reported memory fields.",
      "Confirm they are measured or clearly labeled as estimates."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/pattern_database.py",
    "location": "lines 168-175",
    "issue": "PatternDatabase.save fails for basename-only file paths because os.makedirs is called with an empty dirname.",
    "exact_fix": "Only call os.makedirs when os.path.dirname(filepath) is non-empty.",
    "verification_steps": [
      "Add a test that saves to a basename-only path in a temporary working directory.",
      "Reload the saved database.",
      "Confirm the test passes."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/cube/rubik_cube.py",
    "location": "lines 67-80",
    "issue": "RubikCube accepts externally supplied states without validating shape, sticker values, sticker counts, or centers.",
    "exact_fix": "Validate supplied states for shape (6, 9), integer color range, exactly nine stickers per color, and center consistency, or document that supplied states are unchecked internal data.",
    "verification_steps": [
      "Add tests for invalid shape, invalid sticker value, wrong sticker counts, and bad centers.",
      "Confirm invalid states are rejected or explicitly documented."
    ]
  },
  {
    "severity": "Low",
    "category": "Technical/code issues",
    "file": "src/kociemba/solver.py",
    "location": "lines 120-137",
    "issue": "KociembaSolver initialization prints messages even during quiet solve calls.",
    "exact_fix": "Pass verbosity into initialization or replace unconditional prints with logger calls controlled by verbosity.",
    "verification_steps": [
      "Capture stdout during the first solve(verbose=False) call.",
      "Confirm no initialization text is printed."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/composite_heuristic.py",
    "location": "lines 130-143",
    "issue": "The CompositeHeuristic docstring claims learning-based adjustment factors and better estimates, but the implementation is rule-based and does not learn.",
    "exact_fix": "Rewrite the docstring to describe the implemented exploratory rule-based selector and remove unsupported learning/better-estimate claims.",
    "verification_steps": [
      "Grep for learning-based and better estimates.",
      "Confirm unsupported claims are removed or backed by implementation and tests."
    ]
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/chapters/08_implementation.tex",
    "location": "lines 184-190 and 220-241",
    "issue": "Chapter 8 makes implementation, validation, test, and reproducibility claims without formal citations or artifact cross-references.",
    "exact_fix": "Add explicit cross-references to the validation manifest, benchmark manifest, test configuration, reproducibility manifest, and appendix/artifact descriptions.",
    "verification_steps": [
      "Grep Chapter 8 for citation and cross-reference commands.",
      "Verify claims at lines 184-190 and 220-241 point to exact artifacts."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "README.md",
    "location": "lines 41-43",
    "issue": "The dependency lock is not cryptographic and lacks hashes, platform markers, Python ABI constraints, and TeX/Tectonic pinning.",
    "exact_fix": "Adopt a hash-locked Python dependency file and record Python ABI, OS, and TeX/Tectonic versions required to reproduce the results.",
    "verification_steps": [
      "Create a clean container.",
      "Install dependencies using only the new lock file with hash checking.",
      "Run the default tests and setup verification."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "docker/thesis.Dockerfile",
    "location": "lines 5-15",
    "issue": "The Dockerfile pins the Debian base digest but installs TeX/build packages from live Debian repositories without package-version or snapshot pinning.",
    "exact_fix": "Use Debian snapshot repositories, pin apt package versions, or publish a built thesis-builder image digest.",
    "verification_steps": [
      "Rebuild the thesis Docker image in two clean environments.",
      "Compare installed package versions.",
      "Compare the resulting thesis/main.pdf hash."
    ]
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "thesis/main.pdf",
    "location": "PDF metadata: Tagged: no",
    "issue": "The generated PDF is not tagged for accessibility.",
    "exact_fix": "Generate a tagged/accessibility-compliant PDF if required by the institution, or document that tagging is not required.",
    "verification_steps": [
      "Run pdfinfo thesis/main.pdf.",
      "Confirm Tagged is yes, or attach the institutional exemption."
    ]
  }
]
```

---

## Scores

* **Overall thesis quality score:** 78 / 100
  The thesis is substantially improved, cautious in many places, and mostly aligned with the committed result artifacts, but the missing institutional approval page, stale references, and a few mathematical/wording mismatches remain significant.

* **Technical quality score:** 74 / 100
  The default test suite passes, the architecture is broad, and many claims are now caveated. However, solver outcome semantics, statistics capture, memory reporting, state validation, and documentation overclaims still need correction.

* **Submission readiness score:** 56 / 100
  The repository is not ready for final submission because the approval/front-matter page is incomplete and excluded, benchmark provenance has a stale/circular hash, and several central reproducibility claims require either additional artifacts or more precise wording.
