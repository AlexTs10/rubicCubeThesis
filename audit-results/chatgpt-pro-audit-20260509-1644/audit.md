## Audit basis

I audited the extracted ZIP only. I did not use GitHub, external repositories, or web sources.

I verified several baseline facts before listing issues:

* `pytest` fast test suite: `283 passed, 1 skipped, 28 deselected`.
* Test collection: `284/312 tests collected`.
* Source-ZIP native exact smoke validation completed: `261` cases, `0` failures.
* Stored benchmark solution rows in `results/benchmarks/thesis/thesis_results_combined.json` solve their recorded scrambles using the repository cube implementation.
* The thesis PDF has 110 pages, embedded fonts, and no obvious unresolved `??` / undefined-reference markers in extracted text.
* All cited BibTeX keys used in the thesis sources exist in `thesis/references.bib`.
* I did not find a mismatch between the claimed `40` Python source files under `src/` and the actual repository count.

The issues below are only issues I could verify from actual ZIP contents.

---

# 1. Critical blockers

## CB-1 — Missing final institutional approval/front-matter page

**Severity:** Critical
**File / location:**

* `README.md:7-8`
* `thesis/README.md:1-3`
* `thesis/main.tex:173-180`
* `thesis/chapters/00_approval.tex:30-45`

**Problem:**
The repository explicitly states that the thesis is still in review state and that final institutional front matter is pending. `thesis/main.tex:178-179` comments that the formal approval/signature page remains excluded. `thesis/chapters/00_approval.tex:30-45` still contains placeholders such as committee-member labels and dotted signature/date fields.

**Why it matters:**
A final thesis submission normally cannot be considered institutionally complete if the approval page is missing or placeholder-filled. This is a submission blocker, not just a polish issue.

**Exact fix recommendation:**
Fill `thesis/chapters/00_approval.tex` with the official committee names, roles, signatures/date text required by the institution, then include it in `thesis/main.tex` immediately after the title page and before acknowledgements, for example with `\input{chapters/00_approval}`.

**Verification steps:**

1. Rebuild `thesis/main.pdf`.
2. Confirm the PDF contains the approval page text and no placeholder dotted fields.
3. Search the rebuilt PDF text for the Greek approval-page heading and committee names.
4. Confirm `README.md` and `thesis/README.md` no longer state that final front matter is pending.

---

## CB-2 — Canonical native-exact validation claim is not reproducible from the ZIP alone

**Severity:** Critical
**File / location:**

* `results/validation/native_exact/MANIFEST.json:5-12`
* `results/validation/native_exact/MANIFEST.json:24-28`
* `results/validation/native_exact/README.md:25-30`
* `data/README.md:36-48`
* Missing path: `data/pattern_databases/corner_db.pkl`

**Problem:**
The canonical native-exact validation report depends on `data/pattern_databases/corner_db.pkl`, but that cache is intentionally omitted from the source ZIP. The manifest records the canonical `corner_pdb_enabled` validation as `3513` cases with `1` failure, while the source-ZIP reproducibility path is a smaller smoke preset. The ZIP documents this limitation, but the thesis-level claims still rely on the larger canonical validation as empirical evidence.

**Why it matters:**
A reproducibility auditor cannot regenerate the main native-exact validation evidence from the submitted ZIP alone. This weakens the thesis’s empirical claim that the native exact solver was validated on the full canonical corpus.

**Exact fix recommendation:**
Either include the required generated cache as a separate approved artifact with its SHA-256 hash and provenance, or explicitly downgrade the thesis claim to “checked-in canonical report, not fully source-ZIP reproducible.” The abstract, evaluation chapter, and reproducibility notes should state that the full canonical native-exact validation requires an external generated cache artifact.

**Verification steps:**

1. Confirm `data/pattern_databases/corner_db.pkl` exists in the submitted artifact or approved companion artifact.
2. Run the canonical command from `results/validation/native_exact/MANIFEST.json:24-28`.
3. Compare the regenerated report’s total cases and failure count against the manifest.
4. Confirm the thesis text distinguishes source-ZIP smoke validation from canonical validation.

---

## CB-3 — Benchmark rerun metadata can mislabel legacy redundant scrambles

**Severity:** High
**File / location:**

* `results/benchmarks/thesis/thesis_results_combined.json:117-119`
* `results/benchmarks/thesis/thesis_results_combined.json:150-158`
* `thesis/chapters/07_evaluation.tex:88-90`
* `src/evaluation/algorithm_comparison.py:557-598`
* `src/evaluation/algorithm_comparison.py:792-834`
* `scripts/benchmarks/regenerate_thesis_benchmarks.py:98-156`
* `scripts/benchmarks/regenerate_thesis_benchmarks.py:170-203`
* `scripts/benchmarks/regenerate_thesis_benchmarks.py:254-258`

**Problem:**
The canonical benchmark corpus metadata correctly says it is a legacy corpus allowing redundant same-face moves. The first stored scramble itself contains adjacent same-face moves: `F'` followed by `F` in `results/benchmarks/thesis/thesis_results_combined.json:150-158`. The thesis correctly acknowledges this in `07_evaluation.tex:88-90`.

However, `src/evaluation/algorithm_comparison.py:557-598` generates new scrambles using `allow_redundant=False`, and `export_results()` at `792-834` always writes `scramble_generation: "random_no_consecutive_same_face_moves"`. The regeneration script loads fixed legacy scrambles from the canonical JSON, but exports through this generic metadata path and its combined writer only preserves selected metadata keys.

**Why it matters:**
A rerun from the canonical legacy source can produce per-depth artifacts that are mislabeled as no-consecutive-same-face, even when the scrambles came from the legacy redundant corpus. This undermines traceability of Chapter 7 benchmark reproduction.

**Exact fix recommendation:**
Make scramble-generation metadata an explicit parameter in `export_results()` and in the benchmark regeneration script. When fixed source scrambles are used, copy the original corpus metadata exactly, including `scramble_generation` and any warning/corpus-status fields. Add a test that regenerating from `thesis_results_combined.json` preserves the legacy redundant-scramble label.

**Verification steps:**

1. Regenerate benchmark shards from the stored canonical source.
2. Inspect each generated shard’s `metadata.scramble_generation`.
3. Confirm it says legacy/redundant-allowed when legacy scrambles are loaded.
4. Add a regression test using a stored scramble with adjacent same-face moves and assert the exported metadata does not claim no-consecutive-same-face generation.

---

# 2. Thesis writing issues

## TW-1 — Abstracts present native validation results without the source-ZIP caveat

**Severity:** High
**File / location:**

* `thesis/chapters/00_abstract_gr.tex:22-28`
* `thesis/chapters/00_abstract_en.tex:22-28`
* Related reproducibility limitation: `results/validation/native_exact/README.md:25-30`

**Problem:**
Both abstracts state the native exact solver validation results, including the `3,513`-case corpus and failure reduction from `3` to `1`, but they do not state that canonical regeneration requires an omitted generated cache.

**Why it matters:**
Abstracts are often read independently. Without the caveat, the reader may believe the full validation is reproducible directly from the source ZIP.

**Exact fix recommendation:**
Add a concise sentence to both abstracts, or immediately after the result statement, explaining that canonical native-exact regeneration requires the generated corner-pattern-database cache and that the source ZIP contains a smaller smoke reproducibility preset.

**Verification steps:**

1. Search both abstract files for the native-validation result sentence.
2. Confirm the sentence includes the cache/source-ZIP limitation.
3. Rebuild the PDF and verify the caveat appears in both Greek and English abstracts.

---

## TW-2 — Greek thesis prose uses many untranslated English technical headings and labels

**Severity:** Medium
**File / location:**

* `thesis/chapters/01_introduction.tex:73-86`
* `thesis/chapters/07_evaluation.tex:141-152`
* `thesis/chapters/08_implementation.tex:78-119`

**Problem:**
The thesis mixes Greek academic prose with many English terms and headings such as `backend`, `test profiles`, `Next.js demo frontend`, `Streamlit live UI`, `Lazy Loading`, `Caching`, `Factory Pattern`, and English table abbreviations such as `Succ.`, `TO`, `Med. t`, and `IQR`.

**Why it matters:**
Some English terminology is unavoidable in software theses, but unexplained and inconsistent language switching weakens academic tone and readability.

**Exact fix recommendation:**
Add a terminology/glossary convention early in the thesis, translate headings and table labels where reasonable, and keep code identifiers in monospace while translating the surrounding explanatory prose. For example, use Greek table headings with English abbreviations explained in a caption or note.

**Verification steps:**

1. Search the thesis chapters for repeated English headings and abbreviations.
2. Confirm each is translated, explained, or intentionally kept as a code/tool name.
3. Rebuild the PDF and review Chapter 7 tables and Chapter 8 headings for consistent language.

---

## TW-3 — Implementation chapter makes architecture claims without citations or precise code cross-references

**Severity:** Medium
**File / location:**

* `thesis/chapters/08_implementation.tex:4-10`
* `thesis/chapters/08_implementation.tex:78-91`
* `thesis/chapters/08_implementation.tex:93-119`

**Problem:**
Chapter 8 discusses architecture, lazy loading, caching, factory patterns, backend selection, and implementation structure, but the chapter contains no `\cite{...}` commands and does not consistently cross-reference exact source files for the architectural mechanisms it describes.

**Why it matters:**
Implementation chapters can rely on the author’s code, but architectural claims should be auditable. Without citations or precise code cross-references, the reader must manually search the repository.

**Exact fix recommendation:**
Add source-path cross-references to the relevant modules, and cite external methodology references where general design patterns, caching strategy, or benchmark-engineering principles are discussed. If the thesis has an appendix mapping files to claims, cross-reference it directly.

**Verification steps:**

1. Run `grep -n '\\cite' thesis/chapters/08_implementation.tex`.
2. Confirm the chapter contains either citations or explicit source-path references for each major architectural claim.
3. Rebuild the PDF and check that references and appendix cross-references resolve.

---

## TW-4 — Abstract-level wording can blur native exact validation and external exact benchmark backend

**Severity:** Medium
**File / location:**

* `thesis/chapters/00_abstract_en.tex:24-27`
* `thesis/chapters/00_abstract_gr.tex:22-28`
* Clarification later exists at `thesis/chapters/07_evaluation.tex:34-44`
* Clarification later exists at `thesis/chapters/09_conclusions.tex:17-30`

**Problem:**
The abstract mentions Korf, an external exact backend, and native exact validation in close proximity. Later chapters correctly clarify that deep optimal benchmark results use an external exact backend and not only the native implementation, but the abstract is less explicit.

**Why it matters:**
A reader may over-credit the native implementation for deep optimal benchmark results that actually depend on the external exact backend.

**Exact fix recommendation:**
Revise both abstracts to state explicitly: native exact validation covers the native path, while deep benchmark optimality in the main comparison uses the external exact backend.

**Verification steps:**

1. Search both abstract files for “native” and “external”.
2. Confirm the distinction is made before numeric benchmark claims.
3. Rebuild and review the abstract pages.

---

# 3. Technical/code issues

## TC-1 — `inverse_move()` accepts invalid one-character moves silently

**Severity:** Medium
**File / location:**

* `src/cube/moves.py:12-15`
* `src/cube/moves.py:18-43`
* Related stricter move application: `src/cube/rubik_cube.py:240-257`

**Problem:**
`inverse_move("X")` returns `"X'"` because `inverse_move()` only checks string length and suffix shape. It does not validate that the move is in `ALL_MOVES`.

**Why it matters:**
Invalid moves can propagate through inverse-sequence utilities and fail later in a different subsystem. This creates inconsistent validation behavior compared with `RubikCube.apply_move()`, which rejects invalid base moves.

**Exact fix recommendation:**
Validate `move in ALL_MOVES` at the start of `inverse_move()`, or validate the face and modifier explicitly before returning an inverse.

**Verification steps:**

1. Add tests for `inverse_move("X")`, `inverse_move("R3")`, and `inverse_sequence(["R", "X"])`.
2. Confirm each invalid input raises `ValueError`.
3. Confirm valid moves such as `R`, `R'`, and `R2` still invert correctly.

---

## TC-2 — Cube constructor validates sticker structure but not physical solvability

**Severity:** Medium
**File / location:**

* `src/cube/rubik_cube.py:67-83`
* `src/cube/rubik_cube.py:91-107`

**Problem:**
The constructor accepts an externally supplied cube state and `_validate_state()` checks array shape, sticker range, sticker counts, and fixed centers. It does not reject physically impossible but color-count-valid facelet states, such as states with illegal cubie parity or orientation.

**Why it matters:**
External UI/API inputs can construct impossible cube states that later make solvers fail in ways that look like algorithm bugs rather than invalid input.

**Exact fix recommendation:**
Either add optional legality validation for externally supplied states, for example `validate_legal=True`, using the repository’s facelet-to-cubie legality checks, or clearly rename/document `_validate_state()` as structural validation only and ensure all external input paths perform cubie legality validation before solving.

**Verification steps:**

1. Create a structurally valid but physically impossible cube state, such as a two-sticker swap.
2. Confirm structural validation alone accepts it.
3. Add a legality-validation path and confirm it rejects the impossible state.
4. Confirm normal solved and scrambled legal cubes are still accepted.

---

## TC-3 — External exact backend process-timeout path loses backend stdout/statistics

**Severity:** Medium
**File / location:**

* `src/korf/optimal_solver.py:60-71`
* `src/korf/optimal_solver.py:187-215`
* `src/korf/optimal_solver.py:260-289`

**Problem:**
The child-process worker returns only the backend solve result. The parent later parses backend output from a local `StringIO`, but that buffer is only populated in the signal-timeout path. In the process-timeout fallback path, backend stdout/statistics are not returned to the parent.

**Why it matters:**
On platforms using the process fallback instead of `SIGALRM`/`setitimer`, exported statistics such as generated nodes can be missing or incomplete. This affects reproducibility of node-count comparisons.

**Exact fix recommendation:**
Capture stdout inside `_optimal_backend_worker()` using `redirect_stdout`, return both solution and captured output, and parse the returned output in the parent. Alternatively, change the backend wrapper to return structured statistics instead of parsing stdout.

**Verification steps:**

1. Force the process-timeout path in a test.
2. Use a mocked backend that prints node statistics.
3. Confirm the parent receives and parses those statistics.
4. Confirm benchmark export includes the same statistics under both timeout mechanisms.

---

## TC-4 — Streamlit comparison page uses redundant scramble generation by default

**Severity:** Medium
**File / location:**

* `ui/pages/2_Comparison.py:123-126`
* `src/cube/rubik_cube.py:279-320`
* `src/evaluation/algorithm_comparison.py:590-598`

**Problem:**
The Streamlit comparison page calls `cube.scramble(moves=scramble_depth, seed=seed)` without setting `allow_redundant=False`. The cube method default is `allow_redundant=True`, while the current batch benchmark generator uses `allow_redundant=False`.

**Why it matters:**
The interactive comparison UI can produce scramble distributions that differ from the current benchmark generator. Users may interpret UI comparisons as matching benchmark methodology when they do not.

**Exact fix recommendation:**
Expose scramble policy in the UI and label it clearly. For benchmark-style comparison, default to `allow_redundant=False`; for legacy/canonical comparison, label the corpus as legacy redundant-allowed.

**Verification steps:**

1. Run the Streamlit comparison logic with a fixed seed.
2. Confirm the selected benchmark-style mode generates no adjacent same-face moves.
3. Confirm the UI displays the chosen scramble policy.

---

## TC-5 — Next.js move parser silently drops invalid moves

**Severity:** Medium
**File / location:**

* `webapp/src/lib/cube.ts:206-233`
* `webapp/src/lib/cube.ts:235-240`

**Problem:**
`parseMoves()` ignores tokens that are not in the valid move list instead of reporting them. For example, an input such as `R X U` would parse as `R U`. `inverseMove()` also casts strings to `Move` without runtime validation.

**Why it matters:**
The demo can solve or display a different scramble than the user typed, which is misleading in an educational interface.

**Exact fix recommendation:**
Change `parseMoves()` to return both parsed moves and validation errors, or throw on invalid tokens. Add UI-level error reporting. Add runtime validation in `inverseMove()` for non-`Move` inputs.

**Verification steps:**

1. Add a test for `parseMoves("R X U")`.
2. Confirm the parser reports or rejects `X`.
3. Add a test that `inverseMove("X" as Move)` throws or is unreachable through validated input.

---

## TC-6 — Thistlethwaite lazy database loading prints unconditionally

**Severity:** Low
**File / location:**

* `src/thistlethwaite/solver.py:73-80`
* `src/thistlethwaite/solver.py:82-87`

**Problem:**
`_ensure_databases_loaded()` always prints `Loading pattern databases for first time...` even when `solve(..., verbose=False)` is used.

**Why it matters:**
Unconditional stdout output pollutes benchmark logs, UI output, and quiet-mode tests.

**Exact fix recommendation:**
Pass verbosity into `_ensure_databases_loaded()` or use a logger with configurable level. Quiet mode should not print.

**Verification steps:**

1. Capture stdout around `solver.solve(cube, verbose=False)`.
2. Confirm no loading message appears.
3. Confirm verbose mode still reports useful loading information if desired.

---

# 4. Research/experimental issues

## RE-1 — Main benchmark is single-run and lacks repeated trials or confidence intervals

**Severity:** High
**File / location:**

* `thesis/chapters/07_evaluation.tex:125-136`
* `thesis/chapters/07_evaluation.tex:380-395`

**Problem:**
The thesis explicitly states that the benchmark does not include repetitions, confidence intervals, cold/warm timing separation, full package snapshot, or kernel metadata in the original JSON.

**Why it matters:**
The reported timing and ranking conclusions are descriptive for one benchmark artifact, not statistically robust performance claims.

**Exact fix recommendation:**
Add repeated trials per scramble and solver, include warmup handling, report median/IQR and confidence intervals, and separate cold-start from warm-cache timings.

**Verification steps:**

1. Regenerate benchmarks with a repeat count greater than one.
2. Confirm the result schema records repeat IDs and cold/warm status.
3. Confirm Chapter 7 tables report confidence intervals or bootstrap intervals.
4. Confirm conclusions avoid unsupported statistical generalization.

---

## RE-2 — Memory metric is coarse shared-process RSS delta, not isolated peak memory

**Severity:** Medium
**File / location:**

* `src/evaluation/algorithm_comparison.py:256-263`
* `thesis/chapters/07_evaluation.tex:80-81`
* `thesis/chapters/07_evaluation.tex:313-315`
* `thesis/chapters/07_evaluation.tex:395`

**Problem:**
The benchmark memory metric is a clamped before/after process RSS delta in a shared Python process. The thesis acknowledges this metric is qualitative/noisy.

**Why it matters:**
Shared-process RSS deltas are affected by allocator behavior, garbage collection, cache reuse, and previous solver runs. They are weak evidence for solver memory comparison.

**Exact fix recommendation:**
Run each solver invocation in an isolated subprocess and record peak RSS. Report memory as peak child-process RSS, with the current shared-process delta either removed or clearly labeled as auxiliary.

**Verification steps:**

1. Add a subprocess-based memory measurement path.
2. Record `mem_peak_mb`, PID, and measurement method in result JSON.
3. Compare results across at least two runs to check stability.
4. Update Chapter 7 captions and tables to use peak RSS.

---

## RE-3 — Benchmark groups by requested scramble length, not exact cube distance

**Severity:** Medium
**File / location:**

* `thesis/chapters/07_evaluation.tex:88-112`
* Example stored scramble: `results/benchmarks/thesis/thesis_results_combined.json:150-158`

**Problem:**
The thesis correctly states that requested scramble length is not exact optimal depth, and the corpus allows adjacent same-face redundancy. The stored benchmark example confirms redundant adjacent moves. The verified distance distribution shows many states are shallower than the requested scramble length.

**Why it matters:**
Readers can easily misinterpret depth-10/15/20 tables as performance by true cube distance. This is especially important for optimal solvers.

**Exact fix recommendation:**
Make true verified depth the primary grouping where available, and present requested scramble length as the generation parameter. Add a supplemental exact-depth or no-cancellation corpus if stronger depth claims are needed.

**Verification steps:**

1. Generate tables grouped by verified optimal depth.
2. Confirm every row includes both requested length and verified depth where available.
3. Add a corpus audit that detects adjacent inverse or same-face reductions.
4. Update Chapter 7 captions to say “requested scramble length” wherever applicable.

---

## RE-4 — Native exact and external exact results require stronger separation in headline claims

**Severity:** Medium
**File / location:**

* `thesis/chapters/00_abstract_en.tex:24-27`
* `thesis/chapters/00_abstract_gr.tex:22-28`
* `thesis/chapters/07_evaluation.tex:34-44`
* `thesis/chapters/09_conclusions.tex:17-30`

**Problem:**
Later chapters distinguish native exact validation from the external exact backend used in deep benchmarks, but the headline abstract text is compact enough that the distinction can be missed.

**Why it matters:**
This affects interpretation of the main technical contribution. The native implementation and the external backend support different claims.

**Exact fix recommendation:**
Revise headline claims to separate: native exact solver validation, external exact benchmark backend, and heuristic solver comparisons.

**Verification steps:**

1. Review both abstracts and the conclusion.
2. Confirm each numeric result names the implementation/backend it depends on.
3. Confirm no sentence implies deep optimal benchmark results were produced solely by the native exact implementation.

---

# 5. Citation/reference issues

## CR-1 — Online-reference access dates exist in BibTeX but are not rendered in the PDF bibliography

**Severity:** Medium
**File / location:**

* `thesis/references.bib:25-31`
* `thesis/references.bib:129-163`
* Rendered output: `thesis/main.pdf` bibliography text

**Problem:**
Several online references have `urldate` fields in `references.bib`, but the rendered bibliography does not show access dates. This is consistent with the bibliography style not rendering `urldate`.

**Why it matters:**
Access dates are important for web and software references, especially for reproducibility and citation auditing.

**Exact fix recommendation:**
Move access dates into `note={Accessed: ...}` fields, or use a bibliography style/package that renders `urldate`.

**Verification steps:**

1. Rebuild `thesis/main.pdf`.
2. Extract bibliography text with `pdftotext`.
3. Search for `Accessed` or the relevant access dates.
4. Confirm all web/software references display access dates.

---

## CR-2 — Thistlethwaite foundational citation is a secondary web summary

**Severity:** Medium
**File / location:**

* `thesis/references.bib:25-31`
* `papers/README.md:98-101`
* `papers/BIBLIOGRAPHY_INDEX.md:203-212`

**Problem:**
The `thistlethwaite1981` reference cites Jaap Scherphuis’s historical summary of Morwen Thistlethwaite’s subgroup algorithm rather than a primary archival publication. The repository’s literature notes also acknowledge missing historical sources.

**Why it matters:**
For an academic thesis, foundational algorithm history should prefer primary or archival references when possible. If only a secondary source is available, that limitation should be explicit.

**Exact fix recommendation:**
Add a primary/archival Thistlethwaite or Singmaster/Kociemba historical source if available through the institution. If unavailable, explicitly state in the relevant chapter or bibliography note that the cited source is a secondary historical summary.

**Verification steps:**

1. Inspect `thesis/references.bib` for a primary Thistlethwaite-related source.
2. Check Chapter 3 or the relevant algorithm-history section for a note identifying secondary-source usage.
3. Rebuild the PDF and confirm the note appears near the historical claim.

---

## CR-3 — External exact backend citation lacks immutable package provenance

**Severity:** Medium
**File / location:**

* `thesis/references.bib:157-163`
* `results/benchmarks/thesis/thesis_results_combined.json:136-143`
* `thesis/chapters/07_evaluation.tex:132-136`

**Problem:**
The external exact backend is cited by repository/package/version information, and the benchmark JSON includes post-hoc metadata, but it lacks a wheel hash, source commit hash, or equivalent immutable artifact identifier.

**Why it matters:**
Deep optimal benchmark results depend on this backend. Version numbers alone are weaker than immutable hashes for exact reproducibility.

**Exact fix recommendation:**
Record the backend package wheel/sdist hash, imported module file hashes, and upstream commit if available. Include these in the benchmark JSON and cite them in the thesis reproducibility section.

**Verification steps:**

1. Install the backend in a clean environment.
2. Record package artifact hashes and import-file hashes.
3. Add them to benchmark metadata.
4. Confirm Chapter 7 references the immutable backend provenance.

---

# 6. Reproducibility/setup issues

## RS-1 — `verify_setup.py --all-artifacts` does not perform a clean webapp dependency reproduction

**Severity:** Medium
**File / location:**

* `verify_setup.py:534-545`
* `README.md:143-152`

**Problem:**
`check_webapp_artifacts()` fails if `webapp/node_modules` is absent and tells the user to run `npm ci` first. Therefore, `--all-artifacts` checks a preinstalled webapp state rather than reproducing the webapp setup from a clean ZIP checkout.

**Why it matters:**
A reviewer may expect one verification command to reproduce the webapp build from lockfile state. Instead, the command depends on prior manual installation.

**Exact fix recommendation:**
Add a clean mode such as `--install-webapp` that runs `npm ci` under `webapp/` before testing/building, or rename/document the current mode as a preinstalled-environment artifact check.

**Verification steps:**

1. Remove `webapp/node_modules`.
2. Run the new clean verification command.
3. Confirm it runs `npm ci`, then `npm test` and `npm run build`.
4. Confirm `verify_setup.py --all-artifacts` documentation states whether it installs dependencies or requires them.

---

## RS-2 — Python dependency lock is exact-pinned but not cryptographically reproducible

**Severity:** Medium
**File / location:**

* `README.md:41-47`
* `requirements.lock:1-162`

**Problem:**
The repository states that `requirements.lock` pins exact versions but is not a cryptographic lockfile and lacks hashes, platform markers, Python ABI details, and system-level tool versions.

**Why it matters:**
Exact versions help, but without hashes and platform constraints, the Python environment is not tamper-evident or fully reproducible.

**Exact fix recommendation:**
Generate a hash-checked lockfile using `pip-tools --generate-hashes`, `uv.lock`, Poetry, or another reproducible lock mechanism. Record Python ABI and platform assumptions.

**Verification steps:**

1. Install in a clean virtual environment using hash-checking mode.
2. Confirm all packages are pinned and hash-verified.
3. Record Python version, platform, and ABI in the reproducibility manifest.
4. Confirm `README.md` no longer describes the lock as non-cryptographic without an alternative.

---

## RS-3 — Thesis Docker build still depends on mutable Debian package repositories

**Severity:** Medium
**File / location:**

* `docker/thesis.Dockerfile:1`
* `docker/thesis.Dockerfile:5-15`
* `thesis/README.md:60-65`

**Problem:**
The Docker base image is pinned by digest, but the Dockerfile still runs `apt-get update` and installs TeX packages from Debian repositories without snapshot-pinning package versions. The thesis README acknowledges this limitation.

**Why it matters:**
The Docker build may change over time as Debian package repositories change, which can alter LaTeX output or break the build.

**Exact fix recommendation:**
Use Debian snapshot repositories or record exact package versions from a successful build in a manifest. Prefer a fully pinned TeX Live image or archived package source for thesis builds.

**Verification steps:**

1. Build the Docker image on a fresh host.
2. Record `dpkg-query` package versions.
3. Rebuild on another date/host and compare package versions and PDF hash.
4. Confirm the README documents the snapshot or package-version manifest.

---

## RS-4 — Local thesis rebuild is unavailable without TeX/Tectonic/Docker

**Severity:** Medium
**File / location:**

* `thesis/README.md:42-43`
* `thesis/README.md:67-71`

**Problem:**
The thesis README states that validation/build fails if none of local TeX, Tectonic, or Docker is available, and that a machine without these tools cannot independently rebuild the thesis.

**Why it matters:**
This is a practical reproducibility barrier for reviewers who receive only the ZIP and lack a working TeX/Docker environment.

**Exact fix recommendation:**
Provide a container-independent fallback, a prebuilt verified PDF plus strict provenance, or a fully self-contained container workflow with pinned package sources. At minimum, make the environment requirement prominent in the top-level README.

**Verification steps:**

1. On a clean reviewer machine without TeX/Tectonic/Docker, run the documented validation command.
2. Confirm the README predicts the failure mode.
3. On a machine with the declared build path, rebuild the PDF and compare its hash to the manifest.

---

## RS-5 — Notebook verification is structural smoke only, not execution reproducibility

**Severity:** Medium
**File / location:**

* `scripts/verify_notebooks.py:1-9`
* `scripts/verify_notebooks.py:22-38`
* `thesis/chapters/08_implementation.tex:245`

**Problem:**
The notebook verification script intentionally checks only parseable JSON, metadata, non-empty cells, and kernelspec. It does not execute notebooks.

**Why it matters:**
A notebook can pass this smoke check even if its code is stale, broken, or no longer matches the repository APIs.

**Exact fix recommendation:**
Rename this check as structural verification only, and add an executable notebook subset using `nbclient` or similar with timeouts and deterministic seeds.

**Verification steps:**

1. Add an execution mode or separate script for selected notebooks.
2. Run the selected notebooks in a clean environment.
3. Confirm outputs are regenerated or execution completes without errors.
4. Update Chapter 8 wording to distinguish structural smoke checks from executable reproduction.

---

## RS-6 — Node version pin location can be clearer

**Severity:** Low
**File / location:**

* `.nvmrc:1`
* `webapp/package.json:5-9`
* `webapp/.npmrc:1`
* `README.md:41-45`

**Problem:**
The README says Node/npm are pinned using `.nvmrc`, `webapp/package.json`, and `webapp/.npmrc`, but the `.nvmrc` file is at the repository root, not inside `webapp/`.

**Why it matters:**
A reviewer entering `webapp/` directly may miss the root-level Node version pin.

**Exact fix recommendation:**
State “root `.nvmrc`” in the README, or add a duplicate `webapp/.nvmrc` if the webapp is meant to be built independently.

**Verification steps:**

1. Run `find . -name .nvmrc`.
2. Confirm README wording identifies the file location accurately.
3. From `webapp/`, confirm the documented Node-version workflow is unambiguous.

---

# 7. Submission polish issues

## SP-1 — Top-level README still labels the work as review-stage, not final submission

**Severity:** High
**File / location:**

* `README.md:7-8`
* `thesis/README.md:1-3`

**Problem:**
The top-level README says the project is a review manuscript and that final institutional front matter is pending. The thesis README repeats that final institutional submission is incomplete.

**Why it matters:**
A final thesis submission archive should not present itself as unfinished.

**Exact fix recommendation:**
After completing the approval/front-matter work, update both README files to describe the archive as a final submission artifact, not a review-state manuscript.

**Verification steps:**

1. Search the final archive for `pending`, `review manuscript`, and `not complete`.
2. Confirm such phrases are removed or moved to historical notes that do not describe current submission state.
3. Confirm the final README has a release date/version and completed submission checklist.

---

## SP-2 — Literature-acquisition notes are process artifacts and may distract from final evidence

**Severity:** Low
**File / location:**

* `papers/README.md:5-7`
* `papers/README.md:88-105`
* `papers/BIBLIOGRAPHY_INDEX.md:4-8`

**Problem:**
The `papers/` directory contains acquisition logs, missing-source notes, and local-PDF caveats. These are useful internal process records but are not the final thesis bibliography itself.

**Why it matters:**
Including process notes in a final submission ZIP can confuse reviewers about which sources are actually cited and available as evidence.

**Exact fix recommendation:**
Either exclude `papers/` from the final academic submission or rename it to something like `literature_acquisition_notes/` with a clear non-evidence disclaimer. Keep the authoritative bibliography in `thesis/references.bib`.

**Verification steps:**

1. Compare cited references in the thesis with `thesis/references.bib`.
2. Confirm `papers/` is either excluded or clearly labeled as process-only.
3. Confirm the final README points reviewers to the authoritative bibliography.

---

## SP-3 — Demo UI contains emoji/prototype-style language

**Severity:** Low
**File / location:**

* `ui/app.py:70-72`
* `ui/app.py:142-143`
* `ui/pages/3_Educational.py:118-126`

**Problem:**
The Streamlit demo includes emoji and promotional/prototype phrasing such as the thesis-comparison line ending with a graduation emoji.

**Why it matters:**
This is acceptable for a demo, but if submitted as part of an academic artifact, it should be clearly separated from formal thesis prose and not appear as official explanatory text.

**Exact fix recommendation:**
Keep playful UI copy only if the app is explicitly labeled as a demo. Remove phase/prototype language and emoji from any text intended as formal thesis material.

**Verification steps:**

1. Search `ui/` for emoji, `Phase`, and exclamation-heavy promotional text.
2. Confirm the UI is labeled as a demo or the language is made neutral.
3. Confirm no such text appears in thesis PDF pages or formal submission docs.

---

## SP-4 — Bibliography polish: rendered web/software references lack access-date presentation

**Severity:** Low
**File / location:**

* `thesis/references.bib:129-163`
* Rendered output: `thesis/main.pdf` bibliography

**Problem:**
This overlaps with citation issue CR-1 but also affects submission polish: the final bibliography visually omits access dates for web/software sources.

**Why it matters:**
Reviewers often check web references for access dates in final formatted theses.

**Exact fix recommendation:**
Render access dates in the final bibliography using `note={Accessed: ...}` or a compatible bibliography style.

**Verification steps:**

1. Rebuild the PDF.
2. Extract bibliography text.
3. Confirm every web/software reference displays an access date.

---

# FIX_TARGETS

```json
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "README.md; thesis/README.md; thesis/main.tex; thesis/chapters/00_approval.tex",
    "location": "README.md:7-8; thesis/README.md:1-3; thesis/main.tex:173-180; thesis/chapters/00_approval.tex:30-45",
    "issue": "Final institutional approval/front-matter page is missing from the thesis build and the approval file still contains placeholders.",
    "exact_fix": "Fill thesis/chapters/00_approval.tex with official committee names, roles, and required date/signature text; include it in thesis/main.tex after the title page and before acknowledgements; update README files so they no longer say final front matter is pending.",
    "verification_steps": "Rebuild thesis/main.pdf; confirm the approval page appears; search the PDF and README files for placeholder dotted fields and pending-review wording; verify none remain."
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "results/validation/native_exact/MANIFEST.json; results/validation/native_exact/README.md; data/README.md; data/pattern_databases/corner_db.pkl",
    "location": "results/validation/native_exact/MANIFEST.json:5-12,24-28; results/validation/native_exact/README.md:25-30; data/README.md:36-48; missing path data/pattern_databases/corner_db.pkl",
    "issue": "Canonical native-exact validation requires corner_db.pkl, but that cache is intentionally omitted from the source ZIP.",
    "exact_fix": "Include the generated cache as an approved companion artifact with SHA-256 provenance, or revise thesis claims to state that the canonical validation is a checked-in report and only the smaller smoke preset is source-ZIP reproducible.",
    "verification_steps": "Confirm data/pattern_databases/corner_db.pkl exists or the thesis caveat is present; run the canonical validation command from the manifest; compare regenerated totals and failure counts with the manifest."
  },
  {
    "severity": "High",
    "category": "Critical blockers",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; src/evaluation/algorithm_comparison.py; scripts/benchmarks/regenerate_thesis_benchmarks.py; thesis/chapters/07_evaluation.tex",
    "location": "results/benchmarks/thesis/thesis_results_combined.json:117-119,150-158; src/evaluation/algorithm_comparison.py:557-598,792-834; scripts/benchmarks/regenerate_thesis_benchmarks.py:98-156,170-203,254-258; thesis/chapters/07_evaluation.tex:88-90",
    "issue": "Benchmark reruns can export metadata claiming no-consecutive-same-face scramble generation even when using legacy redundant scrambles.",
    "exact_fix": "Make scramble-generation metadata explicit in export_results and the regeneration script; preserve source corpus metadata when fixed legacy scrambles are loaded; add a regression test using a redundant legacy scramble.",
    "verification_steps": "Regenerate benchmark shards from the stored canonical source; inspect per-depth JSON metadata; confirm legacy redundant-allowed corpus metadata is preserved; run the new regression test."
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_gr.tex; thesis/chapters/00_abstract_en.tex; results/validation/native_exact/README.md",
    "location": "thesis/chapters/00_abstract_gr.tex:22-28; thesis/chapters/00_abstract_en.tex:22-28; results/validation/native_exact/README.md:25-30",
    "issue": "The abstracts state canonical native-exact validation results without saying that canonical regeneration needs an omitted cache.",
    "exact_fix": "Add a concise caveat in both abstracts explaining that the full canonical native-exact validation requires the generated corner PDB cache and that the ZIP includes a smaller smoke preset.",
    "verification_steps": "Search both abstract files for the native-validation result; confirm the cache/source-ZIP caveat appears; rebuild the PDF and inspect both abstracts."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/01_introduction.tex; thesis/chapters/07_evaluation.tex; thesis/chapters/08_implementation.tex",
    "location": "thesis/chapters/01_introduction.tex:73-86; thesis/chapters/07_evaluation.tex:141-152; thesis/chapters/08_implementation.tex:78-119",
    "issue": "Greek academic prose mixes many untranslated English technical headings, UI terms, and table abbreviations.",
    "exact_fix": "Add a terminology convention or glossary; translate headings/table labels where reasonable; keep code identifiers in monospace but translate surrounding prose.",
    "verification_steps": "Search thesis chapters for repeated English headings and abbreviations; confirm each is translated, explained, or intentionally kept as a code/tool term; rebuild and review tables/headings."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/08_implementation.tex",
    "location": "thesis/chapters/08_implementation.tex:4-10,78-91,93-119",
    "issue": "Implementation chapter makes architectural claims without citations or consistent exact source-code cross-references.",
    "exact_fix": "Add source-path cross-references for each major implementation claim and cite methodology/design references where general architectural concepts are discussed.",
    "verification_steps": "Run grep -n '\\\\cite' thesis/chapters/08_implementation.tex; inspect added source-path references; rebuild and confirm references resolve."
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex; thesis/chapters/07_evaluation.tex; thesis/chapters/09_conclusions.tex",
    "location": "thesis/chapters/00_abstract_en.tex:24-27; thesis/chapters/00_abstract_gr.tex:22-28; thesis/chapters/07_evaluation.tex:34-44; thesis/chapters/09_conclusions.tex:17-30",
    "issue": "Headline abstract wording can blur native exact validation and external exact benchmark backend results.",
    "exact_fix": "Revise both abstracts to explicitly separate native exact validation, external exact backend benchmark results, and heuristic solver comparisons.",
    "verification_steps": "Search abstracts for native/external backend wording; confirm every numeric result identifies the implementation/backend used; rebuild the PDF."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/cube/moves.py; src/cube/rubik_cube.py",
    "location": "src/cube/moves.py:12-15,18-43; src/cube/rubik_cube.py:240-257",
    "issue": "inverse_move accepts invalid one-character moves such as X and returns an invalid inverse instead of raising ValueError.",
    "exact_fix": "Validate move in ALL_MOVES at the start of inverse_move or validate face and modifier explicitly before returning.",
    "verification_steps": "Add tests for inverse_move('X'), inverse_move('R3'), and inverse_sequence(['R','X']); confirm they raise ValueError; confirm valid moves still invert correctly."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/cube/rubik_cube.py",
    "location": "src/cube/rubik_cube.py:67-83,91-107",
    "issue": "RubikCube constructor validates facelet structure but not physical solvability/legal cubie parity for externally supplied states.",
    "exact_fix": "Add optional legality validation for external states or document structural-only validation and ensure all external input paths call cubie legality checks before solving.",
    "verification_steps": "Construct a color-count-valid impossible cube state; confirm legality validation rejects it while legal solved/scrambled cubes are accepted."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/optimal_solver.py",
    "location": "src/korf/optimal_solver.py:60-71,187-215,260-289",
    "issue": "Process-timeout fallback for the external exact backend does not return captured backend stdout/statistics to the parent.",
    "exact_fix": "Capture stdout in the child worker and return it with the solution, or return structured backend statistics; parse the returned output in the parent.",
    "verification_steps": "Force the process-timeout path with a mocked backend that prints node statistics; assert the parent receives and exports those statistics."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "ui/pages/2_Comparison.py; src/cube/rubik_cube.py; src/evaluation/algorithm_comparison.py",
    "location": "ui/pages/2_Comparison.py:123-126; src/cube/rubik_cube.py:279-320; src/evaluation/algorithm_comparison.py:590-598",
    "issue": "Streamlit comparison page uses redundant scramble generation by default, unlike the current benchmark generator.",
    "exact_fix": "Expose scramble policy in the UI; default benchmark-style mode to allow_redundant=False; label legacy redundant-allowed mode explicitly.",
    "verification_steps": "Run the UI comparison path with a fixed seed; confirm benchmark-style mode has no adjacent same-face moves and the UI displays the selected policy."
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "webapp/src/lib/cube.ts",
    "location": "webapp/src/lib/cube.ts:206-233,235-240",
    "issue": "Next.js parser silently drops invalid move tokens and inverseMove casts arbitrary strings without runtime validation.",
    "exact_fix": "Make parseMoves return validation errors or throw on invalid tokens; add runtime validation in inverseMove or restrict it to validated inputs.",
    "verification_steps": "Add tests for parseMoves('R X U') and inverseMove('X' as Move); confirm invalid input is reported or rejected."
  },
  {
    "severity": "Low",
    "category": "Technical/code issues",
    "file": "src/thistlethwaite/solver.py",
    "location": "src/thistlethwaite/solver.py:73-80,82-87",
    "issue": "Thistlethwaite lazy database loading prints unconditionally even when solve is called with verbose=False.",
    "exact_fix": "Pass verbosity into _ensure_databases_loaded or use a configurable logger; suppress loading output in quiet mode.",
    "verification_steps": "Capture stdout around solver.solve(cube, verbose=False); confirm no loading message appears; confirm verbose mode remains informative."
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "thesis/chapters/07_evaluation.tex:125-136,380-395",
    "issue": "Main benchmark is single-run and lacks repeated trials, confidence intervals, and cold/warm timing separation.",
    "exact_fix": "Add repeated trials per scramble/solver, warmup handling, confidence intervals or bootstrap intervals, and separate cold-start from warm-cache timing.",
    "verification_steps": "Regenerate benchmarks with repeat_count > 1; confirm JSON records repeat IDs and cold/warm status; update Chapter 7 tables and conclusions."
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "src/evaluation/algorithm_comparison.py; thesis/chapters/07_evaluation.tex",
    "location": "src/evaluation/algorithm_comparison.py:256-263; thesis/chapters/07_evaluation.tex:80-81,313-315,395",
    "issue": "Memory metric is shared-process before/after RSS delta, not isolated peak RSS.",
    "exact_fix": "Measure each solver invocation in an isolated subprocess and record peak RSS; report the current shared-process delta only as auxiliary if retained.",
    "verification_steps": "Add subprocess peak-memory measurement; confirm result JSON records mem_peak_mb and measurement method; update tables/captions."
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "thesis/chapters/07_evaluation.tex:88-112; results/benchmarks/thesis/thesis_results_combined.json:150-158",
    "issue": "Benchmark groups by requested scramble length, not exact cube distance, and the canonical corpus permits redundant moves.",
    "exact_fix": "Use verified optimal depth as the primary grouping where available; present requested length only as generation parameter; add a supplemental exact-depth or no-cancellation corpus if needed.",
    "verification_steps": "Generate tables grouped by verified depth; add a corpus audit for adjacent same-face reductions; update Chapter 7 captions to say requested scramble length."
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/00_abstract_en.tex; thesis/chapters/00_abstract_gr.tex; thesis/chapters/07_evaluation.tex; thesis/chapters/09_conclusions.tex",
    "location": "thesis/chapters/00_abstract_en.tex:24-27; thesis/chapters/00_abstract_gr.tex:22-28; thesis/chapters/07_evaluation.tex:34-44; thesis/chapters/09_conclusions.tex:17-30",
    "issue": "Native exact and external exact backend claims require stronger separation in headline research claims.",
    "exact_fix": "Rewrite headline result statements so each numeric result names whether it depends on the native exact solver or the external exact backend.",
    "verification_steps": "Review abstracts and conclusions; confirm no deep optimal benchmark result is implied to come solely from the native exact implementation."
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; thesis/main.pdf",
    "location": "thesis/references.bib:25-31,129-163; rendered bibliography in thesis/main.pdf",
    "issue": "Online-reference access dates are present as urldate fields but are not rendered in the final PDF bibliography.",
    "exact_fix": "Move access dates into note fields or use a bibliography style/package that renders urldate.",
    "verification_steps": "Rebuild the PDF; extract bibliography text; search for Accessed or the relevant access dates; confirm web/software references display access dates."
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; papers/README.md; papers/BIBLIOGRAPHY_INDEX.md",
    "location": "thesis/references.bib:25-31; papers/README.md:98-101; papers/BIBLIOGRAPHY_INDEX.md:203-212",
    "issue": "The Thistlethwaite foundational citation is a secondary web summary rather than a primary archival source.",
    "exact_fix": "Add a primary or archival source if available, or explicitly state in the relevant chapter/bibliography note that the source is a secondary historical summary.",
    "verification_steps": "Inspect references for a primary Thistlethwaite-related source; confirm chapter text explains secondary-source usage if no primary source is available."
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "thesis/references.bib:157-163; results/benchmarks/thesis/thesis_results_combined.json:136-143; thesis/chapters/07_evaluation.tex:132-136",
    "issue": "External exact backend citation lacks immutable wheel/source commit provenance.",
    "exact_fix": "Record backend wheel or sdist SHA-256, imported module file hashes, and upstream commit if available; include them in benchmark metadata and thesis reproducibility text.",
    "verification_steps": "Install backend in a clean environment; record artifact/import hashes; add metadata to result JSON; verify Chapter 7 references the immutable provenance."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "verify_setup.py; README.md",
    "location": "verify_setup.py:534-545; README.md:143-152",
    "issue": "verify_setup.py --all-artifacts checks a preinstalled webapp state and does not perform clean npm dependency reproduction.",
    "exact_fix": "Add a clean mode that runs npm ci under webapp before testing/building, or document --all-artifacts as a preinstalled-environment check only.",
    "verification_steps": "Remove webapp/node_modules; run the new clean verification command; confirm npm ci, tests, and build execute successfully."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "README.md; requirements.lock",
    "location": "README.md:41-47; requirements.lock:1-162",
    "issue": "Python dependency lock pins exact versions but lacks cryptographic hashes and platform/ABI constraints.",
    "exact_fix": "Generate a hash-checked lockfile and record Python ABI/platform assumptions; keep requirements.lock only as a human-readable pin list if desired.",
    "verification_steps": "Install with hash-checking mode in a clean environment; confirm all dependencies are pinned and hash-verified; update README accordingly."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "docker/thesis.Dockerfile; thesis/README.md",
    "location": "docker/thesis.Dockerfile:1,5-15; thesis/README.md:60-65",
    "issue": "Thesis Docker build pins the base image but still installs TeX packages from mutable Debian repositories.",
    "exact_fix": "Use Debian snapshot repositories or record exact package versions from a successful build in a manifest.",
    "verification_steps": "Build on a fresh host; record dpkg-query versions; rebuild later or elsewhere; compare package versions and PDF hash."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "thesis/README.md",
    "location": "thesis/README.md:42-43,67-71",
    "issue": "Local thesis rebuild is impossible without local TeX, Tectonic, or Docker.",
    "exact_fix": "Provide a fully pinned container workflow, a container-independent fallback, or a clearly documented prebuilt PDF provenance path.",
    "verification_steps": "Run the documented validation command on a clean machine without TeX/Tectonic/Docker and confirm README predicts the failure; run on a prepared machine and compare rebuilt PDF hash."
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "scripts/verify_notebooks.py; thesis/chapters/08_implementation.tex",
    "location": "scripts/verify_notebooks.py:1-9,22-38; thesis/chapters/08_implementation.tex:245",
    "issue": "Notebook verification is structural smoke only and does not execute notebooks.",
    "exact_fix": "Rename the check as structural-only and add an executable deterministic notebook subset using nbclient or equivalent with timeouts.",
    "verification_steps": "Run the new execution-mode notebook check in a clean environment; confirm selected notebooks execute without errors; update Chapter 8 wording."
  },
  {
    "severity": "Low",
    "category": "Reproducibility/setup issues",
    "file": ".nvmrc; webapp/package.json; webapp/.npmrc; README.md",
    "location": ".nvmrc:1; webapp/package.json:5-9; webapp/.npmrc:1; README.md:41-45",
    "issue": "Node version pin is root-level but README wording does not explicitly say root .nvmrc.",
    "exact_fix": "Update README to say root .nvmrc or add webapp/.nvmrc for independent webapp builds.",
    "verification_steps": "Run find . -name .nvmrc; confirm README identifies the file location; verify the webapp build workflow is unambiguous from webapp/."
  },
  {
    "severity": "High",
    "category": "Submission polish issues",
    "file": "README.md; thesis/README.md",
    "location": "README.md:7-8; thesis/README.md:1-3",
    "issue": "Repository still labels the manuscript as review-stage and final front matter as pending.",
    "exact_fix": "After completing front matter, update README files to describe the archive as a final submission artifact and remove pending-review wording.",
    "verification_steps": "Search final archive for pending/review manuscript/not complete; confirm no current-state text describes the submission as unfinished."
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "papers/README.md; papers/BIBLIOGRAPHY_INDEX.md",
    "location": "papers/README.md:5-7,88-105; papers/BIBLIOGRAPHY_INDEX.md:4-8",
    "issue": "Literature-acquisition notes are process artifacts and may distract from the final evidence package.",
    "exact_fix": "Exclude papers/ from final submission or rename it to literature_acquisition_notes with a clear non-evidence disclaimer.",
    "verification_steps": "Confirm final archive points to thesis/references.bib as authoritative; verify process-only acquisition notes are excluded or clearly labeled."
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "ui/app.py; ui/pages/3_Educational.py",
    "location": "ui/app.py:70-72,142-143; ui/pages/3_Educational.py:118-126",
    "issue": "Demo UI contains emoji and prototype/promotional wording.",
    "exact_fix": "Label the app clearly as a demo or remove emoji/phase/prototype language from text intended for formal academic presentation.",
    "verification_steps": "Search ui/ for emoji, Phase, and promotional wording; confirm remaining text is either demo-labeled or academically neutral."
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "thesis/references.bib; thesis/main.pdf",
    "location": "thesis/references.bib:129-163; rendered bibliography in thesis/main.pdf",
    "issue": "Rendered bibliography lacks visible access dates for web/software references.",
    "exact_fix": "Render access dates through note fields or a bibliography style that supports urldate.",
    "verification_steps": "Rebuild the PDF; extract bibliography text; confirm web/software references show access dates."
  }
]
```

---

# Overall scores

**Thesis quality score:** 78 / 100
The thesis appears substantial, technically grounded, and internally self-aware about several limitations. The main deductions are the missing final approval/front matter, abstract caveats, language consistency, and citation/provenance weaknesses.

**Technical quality score:** 82 / 100
The implementation is relatively strong: the fast test suite passes, stored benchmark solutions validate, and the repository has meaningful verification scripts. Deductions are for input-validation gaps, metadata/provenance issues, backend-statistics portability, and UI/benchmark policy inconsistencies.

**Submission readiness score:** 58 / 100
The artifact is review-ready but not final-submission-ready. The largest blockers are the missing institutional front matter and the inability to reproduce canonical native-exact validation from the ZIP alone without the omitted cache artifact.
