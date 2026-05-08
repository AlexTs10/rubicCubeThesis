
I’ll use only the uploaded ZIP, extract and inventory its actual contents, then tie every finding to verified files, locations, and feasible local checks.

The ZIP is extracted and mapped, with thesis sources/PDF, code, tests, benchmarks, webapp, notebooks, and caches present. I’m now verifying cross-file consistency; tests collect 291 despite README claims of 285.

Several earlier blockers appear fixed, including Kociemba Phase 2 sizing and strict optimal-solver output verification. Remaining findings center on stale artifacts, experimental validity, reproducibility, and theory/code mismatches.

Thought for 27m 57s
Audit scope and verification performed
Source used: the uploaded ZIP only, extracted locally at /mnt/data/repo_audit_extracted.

I inspected the extracted repository files and ran targeted verification commands from that extracted tree. Key verification results:

Check	Result
find src -type f -name '*.py'	40 Python source files
find tests -type f -name '*.py'	25 Python test files
python -m pytest tests --collect-only -q	291 tests collected
python -m pytest tests -q	Did not complete within 600 seconds; stalled in tests/unit/test_corner_database.py
python -m pytest tests/unit/test_optimal_solver.py -q -vv	4 passed
python scripts/thesis_workflow.py validate --output ...	Reported no usable thesis build path in this environment
python scripts/thesis_workflow.py build --mode auto	Failed: no usable build path found
cd webapp && npm ci --ignore-scripts --no-audit --no-fund	Failed with React/framer-motion peer dependency conflict
Benchmark artifact inspection	100 rows; official artifact still contains adjacent same-face/redundant scrambles
The repository has improved in several areas, especially the external optimal-solver verification path, but it is still not submission-ready. The main remaining blockers are reproducibility, stale thesis/documentation claims, a broken clean webapp install, an impractical full test command, and an inconsistency between the current benchmark generator and the official benchmark artifact.

1. Critical blockers
Severity	Exact file	Exact location	Problem	Why it matters	Exact fix recommendation	Verification steps
Critical	README.md; tests/unit/test_corner_database.py; src/korf/corner_database.py	README.md:26-31, README.md:100-101; tests/unit/test_corner_database.py:8-19; src/korf/corner_database.py:191-197, 339-371	The documented full test command is not reproducible from the clean ZIP. pytest --collect-only reports 291 tests, not 285. Full pytest tests -q did not complete within 600 seconds and stalled at the corner database test. That test uses max_depth=1, but the generator still builds/loads heavy move-table infrastructure.	The README claims the full test suite passes, but a reproducibility auditor cannot reproduce it from the ZIP. This is a direct submission blocker.	Mark heavy cache-building tests as slow or external, provide precomputed test fixtures for unit tests, and update README/test counts after a fresh clean run. Do not require 40,320×18 table generation in ordinary unit tests.	Run python -m pytest tests --collect-only -q; update all claimed counts to 291 or reduce collection intentionally. Run python -m pytest -m "not slow" tests -q on a clean checkout and confirm it completes quickly.
Critical	webapp/package.json; README.md	webapp/package.json:1; README.md:103, 113-117	npm ci fails in the extracted ZIP because React ^19.2.4 conflicts with framer-motion 10.x peer dependency expecting React 18. README claims cd webapp && npm ci && npm run build succeeds.	The repository’s documented web build/setup path is false for the uploaded ZIP. This breaks reproducibility and submission polish.	Upgrade framer-motion to a React-19-compatible version, downgrade React/ReactDOM to a compatible version, or use a documented override only if justified. Then regenerate package-lock.json.	From a clean extraction, run cd webapp && npm ci && npm run build. README claim is valid only after both commands pass without --legacy-peer-deps.
Critical	results/benchmarks/thesis/thesis_results_combined.json; src/evaluation/algorithm_comparison.py; scripts/benchmarks/regenerate_thesis_benchmarks.py	Artifact example at results/benchmarks/thesis/thesis_results_combined.json:120-128; generator at src/evaluation/algorithm_comparison.py:555-573; replay script at scripts/benchmarks/regenerate_thesis_benchmarks.py:80-109, 124-129	Current benchmark generation says “no consecutive same-face moves” and calls cube.scramble(... allow_redundant=False), but the official committed thesis artifact still contains adjacent same-face scrambles, e.g. F' followed by F. The regeneration script replays stored scrambles, so it preserves the old redundant corpus rather than producing the current generator’s corpus.	The implementation, benchmark artifact, and thesis evidence no longer describe the same experiment. Final experimental claims are therefore not aligned with the current code.	Either regenerate all thesis benchmark artifacts with the current no-consecutive-same-face generator, or explicitly label the committed artifact as the legacy redundant corpus. Add scramble_generation metadata to the combined artifact.	Parse all scramble_moves in thesis_results_combined.json and assert no adjacent same-face moves if claiming non-redundant generation. Confirm the combined artifact metadata includes the generator mode.
Critical	agent_workflow/generated/validation.md; thesis/README.md; README.md	agent_workflow/generated/validation.md:4-16; thesis/README.md:107-110; README.md:104	Generated validation says a thesis build path is ready and no blocking issues exist, but running the actual validation/build workflow in this extracted ZIP reported no usable build path and build --mode auto failed in the audit environment.	A final thesis repository must either provide a reproducible build path or state the external tool requirements precisely. The checked-in validation artifact is stale/misleading.	Regenerate agent_workflow/generated/validation.md from the current environment or remove generated validation artifacts from authoritative claims. Add a pinned TeX/Tectonic/Docker build path or exact setup instructions.	Run python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md and python scripts/thesis_workflow.py build --mode auto from a fresh extraction. The validation file must match the actual command result.
Critical	src/korf/distance_estimator.py; src/korf/corner_database.py	src/korf/distance_estimator.py:97-110, 329-344; src/korf/corner_database.py:266-327	create_estimator(load_databases=True, generate_if_missing=False) still can generate a full corner database because load_databases() calls create_corner_database(load_if_exists=True, save_path=corner_path) without forwarding generate_if_missing=False.	This can trigger massive unexpected generation in a supposedly non-generating path. It is a serious reproducibility and usability bug.	Pass generate_if_missing=generate_if_missing and require_complete=True into the corner DB call exactly as is done for edge DBs.	With no corner DB cache present, run create_estimator(load_databases=True, generate_if_missing=False) and assert it raises FileNotFoundError quickly rather than generating.
Critical	src/thistlethwaite/tables.py	src/thistlethwaite/tables.py:133-147, 600-622	Unknown pattern-database entries with sentinel 255 are converted to heuristic value 0. Phase-2 projection lookup also maps 255 to 0.	This fails open: incomplete/corrupt tables silently become weak heuristics. In a solver used for thesis claims, table incompleteness must be visible.	Raise an exception on sentinel values unless a clearly named debug option is enabled. Store completeness metadata and assert expected completeness before benchmark use.	Create a small table with a forced 255 entry and verify lookup raises. Run benchmark setup and confirm it refuses incomplete phase tables.
2. Thesis writing issues
Severity	Exact file	Exact location	Problem	Why it matters	Exact fix recommendation	Verification steps
High	thesis/chapters/01_introduction.tex; thesis/chapters/08_implementation.tex; thesis/chapters/appendix_a.tex	01_introduction.tex:74, 80; 08_implementation.tex:20-30, 221-225; appendix_a.tex:135	Thesis text still claims 13,033 source lines and 285 collected tests / 284 passed / 1 skipped. Actual extracted ZIP has 13,157 source lines and 291 collected tests; full suite did not complete in the audit run.	Hard-coded verification claims are false in the submitted ZIP. This is a serious academic/reproducibility problem.	Replace static counts with current generated values or move them into a dated reproducibility appendix. Do not claim a passing full suite unless the command passes from a clean extraction.	Run `find src -name '*.py' -print0
High	thesis/chapters/07_evaluation.tex	07_evaluation.tex:88, 123-126, 204-209, 264, 270-281, 338-339	Chapter 7 mostly explains “requested scramble length,” but still uses “βάθος/depth” wording in table headers and conclusions.	Readers can still interpret the groups as exact optimal-depth groups, which the artifact does not support.	Replace remaining “βάθος” labels with “ζητούμενο μήκος scramble” unless referring to verified optimal distance.	Search Chapter 7 for βάθος, βάθη, and depth; verify each occurrence is either corrected or explicitly refers to verified optimal distance.
High	thesis/chapters/03_thistlethwaite.tex; src/thistlethwaite/moves.py; src/kociemba/cubie.py	Thesis 03_thistlethwaite.tex:105; helper src/thistlethwaite/moves.py:128-144; actual cubie moves src/kociemba/cubie.py:217-235, 242-260	Thesis and helper comments say only F/B quarter turns affect corner orientation. Actual cubie definitions also twist corners under R/L quarter turns.	This is a mathematical/explanatory mismatch in an algorithm chapter.	Reword the thesis and helper docstring to match the implementation’s cubie convention, or remove stale helper functions.	Apply R and L to a solved cubie and assert nonzero corner orientation; ensure the thesis explanation matches that behavior.
Medium	thesis/chapters/06_heuristics.tex; src/korf/composite_heuristic.py	06_heuristics.tex:286-289; source docstring src/korf/composite_heuristic.py:1-21	Chapter 6 cautiously says no central quantitative conclusion is claimed, but the source docstring still says “Research Contribution,” “Key Innovation,” and “improves search efficiency” without a committed ablation proving it.	Reviewers may see a mismatch between sober thesis claims and stronger code-level claims.	Downgrade source wording to “exploratory heuristic,” or add an ablation experiment proving the improvement.	Add a benchmark table comparing composite, Hamming, Manhattan, weighted, and any PDB-backed variants on the same corpus.
Medium	thesis/chapters/06_heuristics.tex; src/korf/composite_heuristic.py	06_heuristics.tex:294-325; source src/korf/composite_heuristic.py:46-65, 173-175	Thesis cites fixed line ranges for StateAnalyzer and CompositeHeuristic.__call__, but the actual source line ranges have shifted.	Fixed source-line references drift and become inaccurate without LaTeX build errors.	Replace line references with function/class names and commit hash, or generate snippets automatically.	Run a script comparing cited line ranges to actual definitions before final submission.
Medium	Multiple thesis chapters	Examples include thesis/chapters/07_evaluation.tex:20-42, 05_korf.tex, 06_heuristics.tex	Greek prose mixes English terms such as backend, timeout, benchmark, solver, oracle, fallback, exact, corpus, and heuristic without a glossary.	The academic tone is uneven and harder to read for examiners.	Add a glossary or standardize first-use definitions: Greek term plus English in parentheses, then consistent use.	Perform a terminology pass over all chapters and appendices; ensure each recurring English term has a first-use definition.
Medium	thesis/chapters/07_evaluation.tex	07_evaluation.tex:320-323 and discussion/conclusion subsections	The text draws “clear conclusions” from 100 scrambles without confidence intervals or repeated runs.	The sample is useful but not statistically strong enough for broad claims.	Use “indicative practical conclusions” or add uncertainty estimates and repeated trials.	Add bootstrap confidence intervals for mean/median time and solution length; update wording accordingly.
3. Technical/code issues
Severity	Exact file	Exact location	Problem	Why it matters	Exact fix recommendation	Verification steps
High	src/kociemba/moves.py	src/kociemba/moves.py:76-105	Move-table cache stores raw pickled arrays with no format version, move-order metadata, code hash, shape checks, or dtype validation.	Stale/incompatible caches can silently change solver behavior.	Save metadata with format_version, move_order, expected shapes, dtype, and a code/schema hash. Validate on load.	Corrupt or alter cache metadata and confirm MoveTables.load() rejects it.
High	src/evaluation/algorithm_comparison.py; src/korf/optimal_solver.py	algorithm_comparison.py:196-203; optimal_solver.py:105, 195-223, 286-296, 377-390	KorfOptimalSolver.timeout_supported is set only from POSIX timer availability, even though the code now has a subprocess timeout fallback. In subprocess mode, backend stdout is not captured, so node statistics parsing may disappear.	Benchmark metadata can incorrectly describe timeout enforcement and node availability across platforms.	Replace timeout_supported with timeout_enforced=True when either signal or subprocess fallback is available. Capture stdout in the worker if node stats are needed.	Mock a no-SIGALRM environment; verify metadata says timeout is enforced and node stats behavior is explicitly recorded.
Medium	src/cube/rubik_cube.py	src/cube/rubik_cube.py:327-329	RubikCube.__hash__() hashes mutable NumPy state.	Mutating a cube after using it in a set/dict violates hash invariants.	Remove __hash__ or make cube state immutable; provide explicit state_key() for search keys.	Add a test showing either hashing is disabled or mutation after hash use is impossible.
Medium	src/cube/moves.py	src/cube/moves.py:129-133	Nested count_to_move() is annotated as returning str but returns None when count is zero.	Static type checks and maintainers get misleading information.	Change return annotation to Optional[str] or return an empty string and filter explicitly.	Run mypy or pyright and confirm no return-type error remains.
Medium	src/thistlethwaite/moves.py	src/thistlethwaite/moves.py:128-144, 184-193	Helper functions and docstrings are stale/simplified relative to the actual cubie implementation and exact subgroup logic.	Future code may reuse these helpers and reintroduce theoretical bugs.	Remove unused simplified helpers or make them delegate to the same cubie-coordinate checks used by the solver.	Search for all helper usages; add tests comparing helper results against actual cubie coordinate changes.
Medium	src/korf/composite_heuristic.py	src/korf/composite_heuristic.py:51-65, has_oriented_layer() later in the same class	StateAnalyzer.has_oriented_layer() is described as checking edge orientation, but it actually checks whether face edge stickers match the center color.	The name/documentation and computation do not match.	Rename to has_face_edge_color_match_layer() or implement a cubie orientation-based check.	Add tests for a cube with oriented edges but nonmatching face-edge colors and confirm naming/behavior is correct.
Medium	src/evaluation/algorithm_comparison.py	src/evaluation/algorithm_comparison.py:166, memory measurement paths in solver comparisons	Benchmark memory uses current process RSS deltas while solver instances and caches are reused.	Process-level RSS deltas are noisy and not per-solver peak memory.	Run each solver in an isolated subprocess and record peak RSS.	Compare subprocess peak RSS against current RSS-delta results on the same scrambles.
Low	src/evaluation/algorithm_comparison.py	src/evaluation/algorithm_comparison.py:555-573	Batch test print says no consecutive same-face moves, but that claim is not written into old combined artifacts.	Console output alone does not make benchmark artifacts self-describing.	Ensure every exported benchmark JSON includes scramble_generation and generator parameters.	Inspect results/benchmarks/thesis/thesis_results_combined.json and confirm generator metadata is present.
4. Research/experimental issues
Severity	Exact file	Exact location	Problem	Why it matters	Exact fix recommendation	Verification steps
High	results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex	Artifact example thesis_results_combined.json:120-128; discussion 07_evaluation.tex:75-82	The official benchmark corpus includes redundant/canceling scramble sequences. The thesis explains requested length vs optimal distance, but the experiment still uses a weak difficulty axis.	Performance by “length 20” is not performance on exact-depth-20 or even nonredundant length-20 states.	Add a second benchmark corpus using canonical no-adjacent-same-face scrambles or verified-distance buckets.	Generate a corpus where every row includes requested length, reduced/canonical length, and verified optimal distance where available.
High	src/evaluation/algorithm_comparison.py; scripts/benchmarks/analyze_thesis_data.py	Summary/export around algorithm_comparison.py:712-748; analysis script normalizes successes only	Exact-backend averages are success-conditioned; timeouts are not treated as censored observations in the main summaries.	Completed-only averages understate the cost of exact solving.	Report completed-only means separately from timeout-inclusive means, e.g. treating timeouts as 120 seconds for solve-time summaries.	Add a summary table with success count, timeout count, completed-only mean, and all-attempt timeout-inclusive mean.
High	thesis/chapters/07_evaluation.tex	Methodology/results sections throughout Chapter 7	No confidence intervals, no repeated runs, and no statistical tests are reported.	The claims are comparative but uncertainty is not quantified.	Add bootstrap confidence intervals for times and solution lengths; run at least several seeds/corpora where feasible.	Regenerate tables with 95% CIs and update conclusions to reflect uncertainty.
Medium	thesis/chapters/07_evaluation.tex; src/evaluation/algorithm_comparison.py	07_evaluation.tex:20-33; algorithm_comparison.py:739-745	Timing includes lazy-loading / one-off initialization amortized across reused solver instances. The thesis notes this, but still compares timings as if they are solver speed.	Cold-start and warm-solve performance are different quantities.	Report cold-start and warmed steady-state timings separately.	Add explicit warmup before timed runs, or record initialization time separately.
Medium	scripts/benchmarks/regenerate_thesis_benchmarks.py	regenerate_thesis_benchmarks.py:32-45, 80-109, 124-129	Regeneration defaults source and output to the canonical thesis directory and replays the old stored scrambles.	A user can overwrite official results while believing they generated a fresh corpus.	Default output to a timestamped rerun directory and add a separate generate_new_corpus.py path.	Run the script with no arguments and confirm it does not overwrite results/benchmarks/thesis.
Medium	thesis/chapters/06_heuristics.tex; src/korf/composite_heuristic.py	06_heuristics.tex:286-289; composite_heuristic.py:8-21	Composite heuristic is not backed by a final ablation experiment in the inspected ZIP.	It should not be presented as a measured research contribution without data.	Add ablation results or consistently label it as exploratory only.	Run identical-state comparisons for composite vs simpler heuristics and publish the table.
5. Citation/reference issues
Severity	Exact file	Exact location	Problem	Why it matters	Exact fix recommendation	Verification steps
Medium	thesis/references.bib	thesis/references.bib:95-100	bandelow1982inside is typed as @article with journal = {Birkhauser}.	Bibliographic metadata is wrong.	Change to @book, put Birkhäuser/Birkhauser in publisher, and add complete publication metadata.	Build bibliography and inspect the rendered entry.
Medium	thesis/references.bib	thesis/references.bib:199-210	Wikipedia entries are present as bibliography sources.	Wikipedia is weak support for thesis-critical claims.	Replace with primary papers, textbooks, official documentation, or remove if unused.	Search rendered .bbl/PDF for Wikipedia entries and verify no core claim depends on them.
Medium	thesis/references.bib	thesis/references.bib:506-510, 528-534, 537-542	Several entries use incomplete author fields such as and others.	Final thesis references should be complete and professionally formatted.	Replace with complete author lists or citation-style-approved truncation.	Search references.bib for and others; confirm remaining cases are justified.
High	thesis/references.bib; results/benchmarks/thesis/thesis_results_combined.json	references.bib:191-196; benchmark metadata top of thesis_results_combined.json	The external exact backend is central to optimality claims, but the citation/benchmark metadata includes package name/version only, not exact commit/hash/license or installed backend provenance.	Exact solver provenance is essential for reproducibility and academic auditability.	Add backend package version, installed distribution metadata, upstream commit/tag, license status, and artifact hash to benchmark metadata and thesis appendix.	Rerun benchmark export and confirm metadata includes exact backend provenance.
Low	thesis/references.bib	Multiple @misc entries using urldate	With IEEEtran, urldate may not render as expected for all entry types.	Access dates may disappear in the final bibliography.	Use note = {Accessed: YYYY-MM-DD} or verify the generated bibliography includes access dates.	Build the thesis and inspect the bibliography output.
6. Reproducibility/setup issues
Severity	Exact file	Exact location	Problem	Why it matters	Exact fix recommendation	Verification steps
High	requirements.txt	requirements.txt:1-42	Python dependencies are lower-bound ranges only; there is no Python lockfile in the inspected root.	Builds can drift as packages update.	Add requirements.lock, constraints.txt, or a pyproject.toml + lockfile with exact versions and hashes.	Create a fresh environment from the lockfile and run setup/test/build commands.
High	pytest.ini	pytest.ini:1-3	No pytest markers for slow/external/cache-building tests and no timeout policy.	Heavy tests can hang a clean reproduction run.	Add markers such as slow, external, cache_building, benchmark, and document standard test profiles.	Run pytest -m "not slow and not external" tests -q and ensure it completes quickly.
Medium	verify_setup.py	verify_setup.py:80-88	verify_setup.py checks only a subset of requirements.txt dependencies.	Setup can pass while Streamlit, Plotly, Pillow, Jupyter, profiling, or lint dependencies are missing.	Parse requirements by mode or define extras: core, thesis, ui, web, dev.	Remove a non-checked dependency and confirm the relevant verification mode fails.
Medium	verify_setup.py	verify_setup.py:124-139	Verification mutates the checkout by creating cache directories.	A verification script should be read-only unless explicitly preparing the environment.	Add --create-cache-dirs or move directory creation to a separate prepare script.	Run python verify_setup.py on a clean extraction and confirm no new files/directories appear unless requested.
Medium	verify_setup.py	verify_setup.py:291-302	verify_setup.py runs the full test suite as the supported command, but the current full suite is impractical from a clean ZIP.	The verification script’s “7/7 checks” claim is not reliable until the test profile is fixed.	Make default verification run the fast profile; provide --full for heavy tests.	Run python verify_setup.py from a clean extraction and confirm it finishes within a documented time budget.
Medium	agent_workflow/generated/status.md	status.md:50-69	Checked-in status output has stale toolchain and code-count data.	Generated status files should either be current or not treated as evidence.	Regenerate status after latest fixes or remove generated status from authoritative documentation.	Run python scripts/thesis_workflow.py status --output agent_workflow/generated/status.md and compare against actual counts/toolchain.
Medium	agent_workflow/generated/validation.md	validation.md:4-16	Checked-in validation output says no blocking issues, but actual workflow validation in the audit environment reported no build path.	This directly misleads reviewers about build readiness.	Regenerate validation or replace with a dated environment-specific note.	Run the validation command in the same environment and confirm the file matches.
7. Submission polish issues
Severity	Exact file	Exact location	Problem	Why it matters	Exact fix recommendation	Verification steps
Medium	Top-level ZIP contents	Top-level filenames containing mojibake Greek text	The extracted ZIP contains visibly corrupted/mojibake filenames for some PDF/DOC files.	This looks unprofessional and can break cross-platform handling.	Rename files using UTF-8-safe ASCII or correctly encoded Greek names; remove nonessential duplicate documents.	Extract the ZIP on Linux/macOS/Windows and confirm filenames render correctly.
Medium	docs/CODE_TO_THESIS_MAPPING.md; src/cube/moves.py; src/thistlethwaite/*	CODE_TO_THESIS_MAPPING.md:15-17, 32-35, 191-193; actual functions in src/cube/moves.py	Mapping lists stale/nonexistent symbols such as parse_moves(), format_moves(), PHASE_MOVES, edge_orientation(), corner_orientation(), and ida_star_search().	The mapping document is supposed to help audit code-to-thesis alignment, but currently contains false entries.	Update all function/class names to the actual source names. Add a script that validates documented symbols exist.	Run a symbol-existence checker over docs/CODE_TO_THESIS_MAPPING.md.
Medium	tests/unit/test_kociemba.py	tests/unit/test_kociemba.py:252-255	test_heuristic_admissibility() is a placeholder with pass.	A core correctness property is not actually tested.	Replace with sampled admissibility tests against exact/native shallow oracle or remove the placeholder.	Ensure the test contains real assertions and fails if a heuristic overestimates a shallow exact distance.
Medium	tests/unit/test_thistlethwaite.py	tests/unit/test_thistlethwaite.py:64-95	Edge/corner orientation tests contain vacuous assertions such as >= 0.	These tests do not verify the stated behavior.	Assert exact coordinate changes or compare against the trusted cubie model.	Mutate the coordinate extraction and confirm the tests fail.
Medium	tests/unit/test_thistlethwaite.py	tests/unit/test_thistlethwaite.py:462-492	test_phase_moves_maintain_invariants() comments describe phase-invariant checks but only asserts the final cube is solved.	Test name and comments overstate coverage.	Assert edge orientation after phase 0, corner orientation/E-slice after phase 1, exact G3 membership after phase 2, and solved after phase 3.	Introduce an intentional invariant violation and confirm this test catches it.
Low	webapp/package.json	webapp/package.json:1	package.json is minified into one line.	It is harder to review dependency changes and peer conflicts.	Pretty-print package.json with stable formatting.	Run jq . webapp/package.json > tmp && mv tmp webapp/package.json; verify npm ci still works after dependency fix.
Low	thesis/chapters/08_implementation.tex	08_implementation.tex:20-30, 221-225	Code/test metrics are hard-coded in thesis prose and table.	These numbers drift after local fixes.	Generate code/test metric tables from a script or move them to a dated reproducibility appendix.	Run metric generation script and confirm thesis numbers match the current repository.
FIX_TARGETS
[
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "README.md; tests/unit/test_corner_database.py; src/korf/corner_database.py",
    "location": "README.md:26-31,100-101; tests/unit/test_corner_database.py:8-19; src/korf/corner_database.py:191-197,339-371",
    "issue": "The documented full pytest command is not reproducible from the clean ZIP. Collection reports 291 tests rather than 285, and the full suite did not complete within 600 seconds while stalling in corner database tests.",
    "exact_fix": "Mark heavy cache-building tests as slow/external, provide lightweight fixtures for unit tests, and update README/thesis counts only after a clean successful run.",
    "verification_steps": [
      "Run python -m pytest tests --collect-only -q and confirm documented count matches.",
      "Run python -m pytest -m \"not slow and not external\" tests -q from a clean extraction.",
      "Run the full suite only under the documented full-test profile."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "webapp/package.json; README.md",
    "location": "webapp/package.json:1; README.md:103,113-117",
    "issue": "npm ci fails because React 19 conflicts with framer-motion 10.x peer dependencies, while README claims the clean webapp install/build succeeds.",
    "exact_fix": "Use dependency versions with compatible peer ranges, then regenerate package-lock.json. Do not rely on --legacy-peer-deps for the documented path.",
    "verification_steps": [
      "Run cd webapp && npm ci from a clean extraction.",
      "Run npm run build.",
      "Update README only after both commands pass."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; src/evaluation/algorithm_comparison.py; scripts/benchmarks/regenerate_thesis_benchmarks.py",
    "location": "thesis_results_combined.json:120-128; algorithm_comparison.py:555-573; regenerate_thesis_benchmarks.py:80-109,124-129",
    "issue": "Current code claims no consecutive same-face scramble generation, but official benchmark artifacts contain adjacent same-face moves and the regeneration script replays the old corpus.",
    "exact_fix": "Regenerate thesis benchmark artifacts with the current generator or clearly label the existing artifact as legacy redundant-scramble data. Add scramble_generation metadata to the combined artifact.",
    "verification_steps": [
      "Parse all scramble_moves and assert no adjacent same-face moves if claiming non-redundant generation.",
      "Confirm thesis_results_combined.json contains scramble_generation metadata.",
      "Rebuild Chapter 7 tables from the regenerated artifact."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "agent_workflow/generated/validation.md; thesis/README.md; README.md",
    "location": "validation.md:4-16; thesis/README.md:107-110; README.md:104",
    "issue": "Checked-in workflow validation says a thesis build path is ready and no blocking issues exist, but actual validation/build commands in the extracted ZIP reported no usable build path in this audit environment.",
    "exact_fix": "Regenerate validation output from the current environment or remove generated validation artifacts as authoritative evidence. Provide a pinned, reproducible TeX/Tectonic/Docker build path.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md.",
      "Run python scripts/thesis_workflow.py build --mode auto.",
      "Confirm the generated validation file matches the actual command outcome."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "src/korf/distance_estimator.py; src/korf/corner_database.py",
    "location": "src/korf/distance_estimator.py:97-110,329-344; src/korf/corner_database.py:266-327",
    "issue": "create_estimator(load_databases=True, generate_if_missing=False) can still generate a full corner pattern database because the flag is not passed to create_corner_database.",
    "exact_fix": "Pass generate_if_missing=generate_if_missing and require_complete=True to create_corner_database in the corner DB load path.",
    "verification_steps": [
      "Remove the corner DB cache.",
      "Run create_estimator(load_databases=True, generate_if_missing=False).",
      "Confirm it raises FileNotFoundError quickly and does not generate."
    ]
  },
  {
    "severity": "Critical",
    "category": "Critical blockers",
    "file": "src/thistlethwaite/tables.py",
    "location": "src/thistlethwaite/tables.py:133-147,600-622",
    "issue": "Unknown pattern database sentinel values are converted to zero heuristic values.",
    "exact_fix": "Raise on sentinel 255 by default and require explicit completeness metadata before benchmark use.",
    "verification_steps": [
      "Create or corrupt a table entry to 255.",
      "Call lookup and lookup_phase2.",
      "Confirm they fail loudly rather than returning zero."
    ]
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/01_introduction.tex; thesis/chapters/08_implementation.tex; thesis/chapters/appendix_a.tex",
    "location": "01_introduction.tex:74,80; 08_implementation.tex:20-30,221-225; appendix_a.tex:135",
    "issue": "Thesis claims stale code-line and test-count statistics.",
    "exact_fix": "Regenerate or remove hard-coded metric claims; update them only after a clean verified run.",
    "verification_steps": [
      "Run source/test counting commands.",
      "Run pytest collection and full documented test profile.",
      "Update thesis numbers and appendix metadata."
    ]
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "07_evaluation.tex:88,123-126,204-209,264,270-281,338-339",
    "issue": "Chapter 7 still uses depth wording for requested scramble length groups.",
    "exact_fix": "Replace ambiguous depth wording with requested scramble length unless referring to verified optimal distance.",
    "verification_steps": [
      "Search for βάθος, βάθη, and depth in Chapter 7.",
      "Confirm every occurrence is either corrected or explicitly tied to verified optimal distance."
    ]
  },
  {
    "severity": "High",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/03_thistlethwaite.tex; src/thistlethwaite/moves.py; src/kociemba/cubie.py",
    "location": "03_thistlethwaite.tex:105; src/thistlethwaite/moves.py:128-144; src/kociemba/cubie.py:217-235,242-260",
    "issue": "Thistlethwaite corner-orientation explanation/helper says only F/B quarter turns affect corner orientation, but R/L turns also twist corners in the actual cubie model.",
    "exact_fix": "Rewrite the explanation and helper docstring to match the implementation convention, or remove the stale helper.",
    "verification_steps": [
      "Apply R and L to a solved cubie and verify corner_orient changes.",
      "Confirm thesis and helper comments describe that behavior accurately."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/06_heuristics.tex; src/korf/composite_heuristic.py",
    "location": "06_heuristics.tex:286-289; src/korf/composite_heuristic.py:1-21",
    "issue": "Composite heuristic source docstring makes stronger improvement/innovation claims than the thesis evidence supports.",
    "exact_fix": "Downgrade wording to exploratory heuristic or add an ablation experiment proving the improvement.",
    "verification_steps": [
      "Run an ablation benchmark comparing composite against simpler heuristics.",
      "Update thesis and docstring with evidence-backed wording."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/06_heuristics.tex",
    "location": "06_heuristics.tex:294-325",
    "issue": "The thesis cites fixed source-line ranges for code definitions that have shifted.",
    "exact_fix": "Reference function/class names and commit hash, or auto-generate snippets and line references.",
    "verification_steps": [
      "Run a source-snippet verification script.",
      "Confirm cited ranges match actual source definitions."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "Multiple thesis chapters",
    "location": "Examples: thesis/chapters/07_evaluation.tex:20-42; thesis/chapters/05_korf.tex; thesis/chapters/06_heuristics.tex",
    "issue": "Academic prose mixes many English technical terms without a glossary or stable first-use definitions.",
    "exact_fix": "Add a glossary and standardize first-use definitions for backend, timeout, benchmark, solver, oracle, fallback, exact, corpus, and heuristic.",
    "verification_steps": [
      "Run a terminology pass across all chapters.",
      "Confirm every recurring English term is either defined or consistently translated."
    ]
  },
  {
    "severity": "Medium",
    "category": "Thesis writing issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "07_evaluation.tex:320-323",
    "issue": "The evaluation language is stronger than supported by 100 scrambles without uncertainty estimates.",
    "exact_fix": "Use more cautious wording or add repeated runs and confidence intervals.",
    "verification_steps": [
      "Add bootstrap confidence intervals to tables.",
      "Update discussion language to reflect uncertainty."
    ]
  },
  {
    "severity": "High",
    "category": "Technical/code issues",
    "file": "src/kociemba/moves.py",
    "location": "src/kociemba/moves.py:76-105",
    "issue": "Move table cache lacks format/version/shape/move-order metadata.",
    "exact_fix": "Store and validate format_version, move_order, table shapes, dtypes, and code/schema hash.",
    "verification_steps": [
      "Create a cache with mismatched metadata.",
      "Confirm MoveTables.load rejects it."
    ]
  },
  {
    "severity": "High",
    "category": "Technical/code issues",
    "file": "src/evaluation/algorithm_comparison.py; src/korf/optimal_solver.py",
    "location": "algorithm_comparison.py:196-203; optimal_solver.py:105,195-223,286-296,377-390",
    "issue": "Korf timeout metadata and node-stat parsing are inconsistent across signal and subprocess timeout paths.",
    "exact_fix": "Expose accurate timeout_enforced metadata and capture backend stdout in subprocess mode if node stats are reported.",
    "verification_steps": [
      "Mock a no-SIGALRM environment.",
      "Run a timed solve and inspect exported metadata and node stats."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/cube/rubik_cube.py",
    "location": "src/cube/rubik_cube.py:327-329",
    "issue": "RubikCube hashes mutable state.",
    "exact_fix": "Remove __hash__ or make hashed cube state immutable; provide state_key() for search keys.",
    "verification_steps": [
      "Add a test ensuring RubikCube is unhashable or immutable after hashing."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/cube/moves.py",
    "location": "src/cube/moves.py:129-133",
    "issue": "count_to_move is annotated as returning str but returns None for zero rotations.",
    "exact_fix": "Change return type to Optional[str] or return an empty string and filter explicitly.",
    "verification_steps": [
      "Run mypy or pyright and confirm no return-type error remains."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/thistlethwaite/moves.py",
    "location": "src/thistlethwaite/moves.py:128-144,184-193",
    "issue": "Stale helper functions and comments simplify orientation/subgroup semantics.",
    "exact_fix": "Remove or rewrite helpers to delegate to verified cubie-coordinate logic.",
    "verification_steps": [
      "Search for helper usage.",
      "Add tests comparing helper outputs with actual cubie coordinate transitions."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/korf/composite_heuristic.py",
    "location": "src/korf/composite_heuristic.py:51-65 and has_oriented_layer method",
    "issue": "has_oriented_layer name/documentation implies cubie edge orientation but checks face-edge color matches.",
    "exact_fix": "Rename the method or implement a true cubie orientation check.",
    "verification_steps": [
      "Add tests distinguishing cubie edge orientation from face-edge color matching."
    ]
  },
  {
    "severity": "Medium",
    "category": "Technical/code issues",
    "file": "src/evaluation/algorithm_comparison.py",
    "location": "src/evaluation/algorithm_comparison.py:166",
    "issue": "Memory metrics use process RSS deltas with reused solver instances and caches.",
    "exact_fix": "Measure each solver in an isolated subprocess and report peak RSS.",
    "verification_steps": [
      "Run the same benchmark with subprocess peak memory measurement.",
      "Compare with old RSS-delta values."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "results/benchmarks/thesis/thesis_results_combined.json; thesis/chapters/07_evaluation.tex",
    "location": "thesis_results_combined.json:120-128; 07_evaluation.tex:75-82",
    "issue": "Official corpus uses redundant/canceling scramble sequences, making requested length a weak difficulty axis.",
    "exact_fix": "Add canonical/no-adjacent-same-face and verified-distance-stratified benchmark corpora.",
    "verification_steps": [
      "Generate a new corpus with requested length, reduced length, and verified optimal distance fields.",
      "Recompute all Chapter 7 tables and figures."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "src/evaluation/algorithm_comparison.py; scripts/benchmarks/analyze_thesis_data.py",
    "location": "algorithm_comparison.py:712-748; analyze_thesis_data.py normalization and summary logic",
    "issue": "Exact-backend statistics are success-conditioned and do not treat timeouts as censored/all-attempt observations.",
    "exact_fix": "Report completed-only and timeout-inclusive metrics separately.",
    "verification_steps": [
      "Add timeout count and timeout-inclusive mean time to generated analysis tables."
    ]
  },
  {
    "severity": "High",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex",
    "location": "Chapter 7 methodology/results sections",
    "issue": "No confidence intervals, repeated runs, or statistical tests are reported.",
    "exact_fix": "Add bootstrap confidence intervals and repeated-seed experiments where feasible.",
    "verification_steps": [
      "Regenerate tables with 95% CIs.",
      "Update conclusion claims to match uncertainty."
    ]
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/07_evaluation.tex; src/evaluation/algorithm_comparison.py",
    "location": "07_evaluation.tex:20-33; algorithm_comparison.py:739-745",
    "issue": "Timing mixes lazy initialization cost with warm solve cost.",
    "exact_fix": "Separate initialization time from warmed solve time.",
    "verification_steps": [
      "Run cold-start and warmed benchmark profiles.",
      "Report both separately in Chapter 7."
    ]
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "scripts/benchmarks/regenerate_thesis_benchmarks.py",
    "location": "regenerate_thesis_benchmarks.py:32-45,80-109,124-129",
    "issue": "Benchmark regeneration defaults can overwrite canonical artifacts and only replay old scrambles.",
    "exact_fix": "Default output to a timestamped rerun directory and create a separate new-corpus generator.",
    "verification_steps": [
      "Run script with no arguments and confirm results/benchmarks/thesis is not overwritten."
    ]
  },
  {
    "severity": "Medium",
    "category": "Research/experimental issues",
    "file": "thesis/chapters/06_heuristics.tex; src/korf/composite_heuristic.py",
    "location": "06_heuristics.tex:286-289; composite_heuristic.py:8-21",
    "issue": "Composite heuristic lacks committed ablation evidence.",
    "exact_fix": "Add a dedicated ablation benchmark or label it as exploratory only.",
    "verification_steps": [
      "Run identical-state comparisons for composite, weighted, Hamming, Manhattan, and PDB-backed variants."
    ]
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "thesis/references.bib:95-100",
    "issue": "Bandelow reference is incorrectly typed as an article with publisher in journal field.",
    "exact_fix": "Correct to @book with publisher metadata.",
    "verification_steps": [
      "Build bibliography and inspect rendered Bandelow entry."
    ]
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "thesis/references.bib:199-210",
    "issue": "Wikipedia entries are included as bibliography sources.",
    "exact_fix": "Replace with primary/official sources or remove if unused.",
    "verification_steps": [
      "Inspect rendered bibliography and ensure thesis-critical claims do not cite Wikipedia."
    ]
  },
  {
    "severity": "Medium",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "thesis/references.bib:506-510,528-534,537-542",
    "issue": "Some references use incomplete author fields with 'and others'.",
    "exact_fix": "Replace with complete author metadata or style-approved truncation.",
    "verification_steps": [
      "Search references.bib for 'and others' and resolve every occurrence."
    ]
  },
  {
    "severity": "High",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib; results/benchmarks/thesis/thesis_results_combined.json",
    "location": "references.bib:191-196; benchmark metadata top-level object",
    "issue": "External exact backend citation and benchmark metadata lack exact commit/hash/license provenance.",
    "exact_fix": "Record backend version, distribution metadata, upstream commit/tag, license status, and artifact hash.",
    "verification_steps": [
      "Inspect exported benchmark metadata and thesis appendix for exact backend provenance."
    ]
  },
  {
    "severity": "Low",
    "category": "Citation/reference issues",
    "file": "thesis/references.bib",
    "location": "Multiple @misc entries with urldate fields",
    "issue": "urldate may not render under the selected IEEEtran bibliography style.",
    "exact_fix": "Use note = {Accessed: YYYY-MM-DD} or verify .bbl rendering.",
    "verification_steps": [
      "Build thesis and inspect rendered bibliography access dates."
    ]
  },
  {
    "severity": "High",
    "category": "Reproducibility/setup issues",
    "file": "requirements.txt",
    "location": "requirements.txt:1-42",
    "issue": "Python dependencies are specified only as lower bounds, with no Python lockfile.",
    "exact_fix": "Add a pinned lockfile or constraints file with exact versions and hashes.",
    "verification_steps": [
      "Create a fresh environment from the lockfile.",
      "Run setup, tests, thesis validation, and benchmarks."
    ]
  },
  {
    "severity": "High",
    "category": "Reproducibility/setup issues",
    "file": "pytest.ini",
    "location": "pytest.ini:1-3",
    "issue": "No pytest markers or timeout policy exist for slow/external/cache-building tests.",
    "exact_fix": "Add slow/external/cache_building markers and document fast/full test profiles.",
    "verification_steps": [
      "Run pytest -m \"not slow and not external\" tests -q.",
      "Run slow tests separately under a documented timeout."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "verify_setup.py",
    "location": "verify_setup.py:80-88",
    "issue": "verify_setup.py checks only a subset of requirements.txt.",
    "exact_fix": "Check dependencies by mode or parse requirements.txt.",
    "verification_steps": [
      "Remove a non-checked dependency and confirm the appropriate verification mode fails."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "verify_setup.py",
    "location": "verify_setup.py:124-139",
    "issue": "verify_setup.py mutates the checkout by creating cache directories.",
    "exact_fix": "Make verification read-only by default and move directory creation behind an explicit flag.",
    "verification_steps": [
      "Run verify_setup.py on a clean extraction and confirm no new directories are created unless requested."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "verify_setup.py",
    "location": "verify_setup.py:291-302",
    "issue": "verify_setup.py uses the full pytest suite as a supported check even though the current clean full suite is impractical.",
    "exact_fix": "Default to a fast test profile and reserve full heavy checks for --full.",
    "verification_steps": [
      "Run python verify_setup.py and confirm it completes within a documented time budget."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "agent_workflow/generated/status.md",
    "location": "agent_workflow/generated/status.md:50-69",
    "issue": "Generated status file has stale toolchain and code-count data.",
    "exact_fix": "Regenerate status after fixes or stop treating generated status as current evidence.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py status --output agent_workflow/generated/status.md.",
      "Confirm counts and toolchain entries match the actual environment."
    ]
  },
  {
    "severity": "Medium",
    "category": "Reproducibility/setup issues",
    "file": "agent_workflow/generated/validation.md",
    "location": "agent_workflow/generated/validation.md:4-16",
    "issue": "Generated validation file claims no blocking issues despite actual validation failure in the audit environment.",
    "exact_fix": "Regenerate validation or make the file environment-specific and dated.",
    "verification_steps": [
      "Run python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md.",
      "Confirm the file reflects actual build-path status."
    ]
  },
  {
    "severity": "Medium",
    "category": "Submission polish issues",
    "file": "Top-level ZIP contents",
    "location": "Top-level extracted filenames with mojibake Greek text",
    "issue": "Some top-level PDF/DOC filenames are mojibake/corrupted after extraction.",
    "exact_fix": "Rename to UTF-8-safe names or ASCII names and remove nonessential duplicate documents.",
    "verification_steps": [
      "Extract the ZIP on Linux, macOS, and Windows.",
      "Confirm filenames render correctly."
    ]
  },
  {
    "severity": "Medium",
    "category": "Submission polish issues",
    "file": "docs/CODE_TO_THESIS_MAPPING.md",
    "location": "CODE_TO_THESIS_MAPPING.md:15-17,32-35,191-193",
    "issue": "Code-to-thesis mapping lists stale/nonexistent functions and stale test counts.",
    "exact_fix": "Update the mapping to actual source symbols and counts; add a symbol-checking script.",
    "verification_steps": [
      "Run a script that verifies every documented symbol exists in the referenced file."
    ]
  },
  {
    "severity": "Medium",
    "category": "Submission polish issues",
    "file": "tests/unit/test_kociemba.py",
    "location": "tests/unit/test_kociemba.py:252-255",
    "issue": "test_heuristic_admissibility is a pass placeholder.",
    "exact_fix": "Replace with real admissibility checks or remove the placeholder.",
    "verification_steps": [
      "Ensure the test has assertions and fails when a heuristic overestimates shallow exact distance."
    ]
  },
  {
    "severity": "Medium",
    "category": "Submission polish issues",
    "file": "tests/unit/test_thistlethwaite.py",
    "location": "tests/unit/test_thistlethwaite.py:64-95",
    "issue": "Orientation tests use vacuous >= 0 assertions.",
    "exact_fix": "Assert exact expected coordinates or compare against the trusted cubie model.",
    "verification_steps": [
      "Mutate coordinate extraction and confirm tests fail."
    ]
  },
  {
    "severity": "Medium",
    "category": "Submission polish issues",
    "file": "tests/unit/test_thistlethwaite.py",
    "location": "tests/unit/test_thistlethwaite.py:462-492",
    "issue": "Phase-invariant test comments do not match actual assertions.",
    "exact_fix": "Add assertions for each phase invariant after applying that phase's moves.",
    "verification_steps": [
      "Introduce an intentional phase invariant violation and confirm the test catches it."
    ]
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "webapp/package.json",
    "location": "webapp/package.json:1",
    "issue": "package.json is minified into a single line.",
    "exact_fix": "Pretty-print package.json with stable formatting.",
    "verification_steps": [
      "Run jq . webapp/package.json and preserve valid JSON.",
      "Run npm ci after dependency fixes."
    ]
  },
  {
    "severity": "Low",
    "category": "Submission polish issues",
    "file": "thesis/chapters/08_implementation.tex",
    "location": "08_implementation.tex:20-30,221-225",
    "issue": "Static code/test metrics are hard-coded and stale.",
    "exact_fix": "Generate metrics from a script or move them into a dated reproducibility appendix.",
    "verification_steps": [
      "Run the metric generator and confirm thesis values match current source."
    ]
  }
]
Scores
Score	Value
Overall thesis quality score	74 / 100
Technical quality score	61 / 100
Submission readiness score	42 / 100
The thesis text is substantially improved in nuance, especially around requested scramble length and external-vs-native exact solving. However, the submitted ZIP still has serious reproducibility and consistency problems: the full test command does not complete cleanly, webapp install fails, benchmark artifacts do not match the current generator, generated validation/status artifacts are stale, and several thesis/documentation verification claims are false for the actual extracted repository.


