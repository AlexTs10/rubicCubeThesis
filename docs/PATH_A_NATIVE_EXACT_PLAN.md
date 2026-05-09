# Path A Native Exact Solver Plan

Date: 2026-03-22
Status: Historical execution plan with current-state notes
Scope: Build a native exact Rubik's Cube solver path inside this repository and use it to support an exact move-distance recognizer, without relying on the current external optimal-solver wrapper for the final claim.

Current-state note: this document began as a pre-implementation plan. The repository now contains a native exact solver path in `src/korf/native_exact_solver.py`, native admissible coordinate heuristics in `src/korf/native_coordinate_heuristic.py`, focused tests under `tests/unit/test_native_exact_solver.py` and `tests/unit/test_native_coordinate_heuristic.py`, oracle agreement coverage in `tests/integration/test_native_exact_oracle_agreement.py`, and validation artifacts under `results/validation/native_exact/`. Keep the plan below as historical scope control, not as proof that the current checkout still lacks those files.

## 1. Objective

The target is a native exact solver path that can honestly support the thesis claim:

- the repository contains its own exact optimal solver,
- the repository contains its own exact move-distance recognizer,
- the solver operates under the repository's move metric,
- the solver is validated strongly enough that the thesis can describe it as exact without evasive wording.

This plan is intentionally stricter than "find something that solves cubes." The bar is:

- exact on full cube states, not just subproblems,
- native in this repository,
- testable,
- reproducible,
- internally documented,
- aligned with the thesis text and benchmark artifacts.

## 2. What "Exact" Means Here

For this project, the solver is only considered exact if all of the following are true:

1. It searches the full Rubik's Cube state space, not only corners or reduced groups.
2. It returns a valid solution sequence that solves the input cube.
3. No shorter solution exists under the same move metric.
4. The reported move distance for a state equals the length of the optimal solution returned by the solver.
5. The final public API used by the thesis does not depend on the external `optimal.solver` backend.

## 3. Move Metric Contract

The repository currently counts `U`, `U'`, and `U2` as one move each. That means the codebase is using a face-turn metric / half-turn metric style cost model where quarter-turns and half-turns both cost 1.

The native exact solver must use the same cost model everywhere:

- search branching,
- heuristic lower bounds,
- validation corpus,
- optimality claims,
- benchmark reporting,
- thesis wording.

If this is not held constant, every comparison with the current results becomes invalid.

## 4. Current Ground Truth

At the time this plan was written, the repository did not contain a native exact solver. In the current checkout, the native exact path exists, but the final thesis benchmark corpus at `results/benchmarks/thesis/thesis_results_combined.json` still records the external `optimal_external` backend for the 100-scramble Korf benchmark numbers.

### 4.1 What is reusable

- `src/kociemba/cubie.py` provides a cubie-level state representation and move multiplication.
- `src/kociemba/coord.py` provides ranking/unranking helpers and corner coordinates.
- `src/korf/corner_database.py` is the strongest solver-grade component in the current Korf area.
- `src/korf/pattern_database.py` provides reusable storage and BFS infrastructure conceptually.
- `src/korf/native_exact_solver.py` provides the repository-native exact solver API.
- `src/korf/native_coordinate_heuristic.py` provides native admissible coordinate lower bounds.
- `src/korf/a_star.py` contains reusable pruning ideas, but not a usable exact engine.
- `src/korf/optimal_solver.py` is useful only as a development-time oracle for cross-checking.

### 4.2 What is not acceptable for Path A

- `src/korf/optimal_solver.py` as the final solver path, because it wraps an external backend.
- `src/korf/heuristics.py`, because those heuristics are not proven lower bounds.
- `src/korf/composite_heuristic.py`, because it is explicitly non-admissible.
- `src/korf/distance_estimator.py` as an exact distance recognizer.
- `src/korf/a_star.py` as-is, because it searches facelet states with arbitrary heuristics and does not constitute a Korf-grade exact solver.
- `src/korf/edge_database.py` as-is, because the abstraction is too weak and internally inconsistent for an exact-solver claim.

### 4.3 Known correctness risk already identified

`src/korf/pattern_database.py` currently uses nibble value `15` both as a valid stored distance and as the implicit "uninitialized" sentinel via `is_initialized()`. That ambiguity is not acceptable in an exact solver pipeline unless the represented abstraction can be proven never to reach distance 15. The current code does not prove that.

## 5. Non-Negotiable Acceptance Criteria

Path A will only be declared complete if all of the following are satisfied.

### 5.1 API criteria

We must expose a native public API that is clearly separate from the external wrapper:

- `solve_exact_native(cube, ...)`
- `optimal_distance_native(cube, ...)`

Optional convenience aliases may exist later, but there must be a direct native API used in tests and benchmarks.

### 5.2 Correctness criteria

The solver must:

- solve already-solved cubes with zero moves,
- solve all one-move states with depth 1,
- solve all two-move states with optimal depth 2 after duplicate-state normalization,
- solve a curated shallow corpus with exact lengths,
- agree with a trusted oracle on a curated sample of deeper random states,
- always return a sequence that actually solves the cube when replayed.

### 5.3 Heuristic criteria

Every heuristic used by the native exact solver must be admissible. For this project that means:

- lower-bound only,
- no empirical "usually okay" logic,
- no weighted combinations above 1,
- no fallback to non-admissible estimators in the exact path.

### 5.4 Search criteria

The native exact solver must use:

- cubie-level states,
- deterministic move ordering,
- canonical pruning rules documented in code,
- iterative deepening / exact branch-and-bound behavior suitable for optimal search.

### 5.5 Validation criteria

Before thesis claims are updated, we need:

- deterministic tests,
- development cross-checks against the external oracle,
- explicit reporting of where the native solver is proven vs. where it is only sampled,
- honest documentation of any performance ceiling.

## 6. Things We Will Not Fake

The implementation must not do any of the following:

- call the external backend from inside the native solver path,
- claim exactness because it matched a handful of examples,
- mix approximate heuristics into the exact path,
- keep ambiguous storage that can silently alias "unvisited" and "distance 15",
- overstate solver readiness in the thesis before the validation stage is complete.

## 7. High-Level Architecture

The most realistic architecture for this repository is:

1. Cubie-state input and move application.
2. Exact-safe pattern database infrastructure.
3. A cubie-based native IDA* solver.
4. An admissible lower bound stack that starts with a full corner PDB.
5. Later extension to stronger edge-based admissible abstractions if the first slice is too weak.
6. A native distance API built on the exact solver.
7. Development-only cross-checks against the existing external oracle.

This is deliberately staged so exactness is established first on small validated ranges before performance work begins.

## 8. Detailed Execution Phases

## Phase 0: Freeze the claim boundary

Goal:
Define exactly what counts as success before editing code.

Tasks:

- Record the current non-native status of `src/korf/optimal_solver.py`.
- Freeze the metric contract: all 18 face turns cost 1.
- Decide naming for the new native modules so they cannot be confused with the wrapper.
- Historical naming decision: the current native exact API lives in `src/korf/native_exact_solver.py`.

Exit condition:

- The native path has a namespaced home and a written correctness contract.

## Phase 1: Exact-safe storage layer

Goal:
Repair or replace the current pattern database storage so it can safely back admissible heuristics.

Tasks:

- Redesign the sentinel strategy in `src/korf/pattern_database.py`.
- Remove ambiguous treatment of value 15 as both "distance 15" and "uninitialized".
- Decide whether to keep nibble packing or move to byte packing for the first exact-safe version.
- Preserve save/load and statistics behavior.
- Add focused unit tests for packing, unpacking, sentinel behavior, and persistence.

Design principle:

Correctness first, compression second. If a byte-per-entry implementation is safer for the first exact version, use it and optimize later.

Exit condition:

- We can store and retrieve pattern distances without ambiguous values.

## Phase 2: Native exact search kernel

Goal:
Create a cubie-based exact search engine that does not depend on facelet `RubikCube` copies per node.

Tasks:

- Build a new search module around `CubieCube`.
- Implement deterministic move ordering.
- Implement same-face pruning.
- Implement opposite-face canonical ordering.
- Keep path storage compact.
- Add a clean stop/timeout surface without weakening exactness semantics.

Important constraint:

Timeout behavior must not be mistaken for "no solution." Exactness only applies to completed runs.

Exit condition:

- A native search kernel can solve trivial and shallow cases optimally using a supplied admissible integer heuristic.

## Phase 3: Corner PDB admissible heuristic

Goal:
Use the strongest existing trustworthy piece as the first real lower bound.

Tasks:

- Verify `corner_index()` and `index_to_corner_state()` with round-trip tests.
- Verify move application consistency on corner coordinates.
- Build or load a corner PDB through exact-safe storage.
- Expose `corner_lower_bound(cubie)`.
- Confirm the corner bound is admissible on the shallow validation corpus.

Expected outcome:

This will likely be exact enough for shallow states and too slow for broad deep-state coverage, but that is acceptable for the first milestone.

Exit condition:

- The native solver is running on cubie states with an admissible corner-only lower bound.

## Phase 4: Validation corpus and exactness scaffolding

Goal:
Create the proof harness before adding more complexity.

Tasks:

- Generate solved, 1-move, 2-move, 3-move, and deduplicated shallow states.
- Add replay checks for returned solutions.
- Add depth assertions for known-optimal shallow states.
- Add heuristic admissibility checks on the shallow corpus.
- Add cross-checks against the external oracle on a curated small sample.

Important rule:

The external oracle may be used here only as a validator, never as part of the native solving path.

Exit condition:

- We have a red/green test harness that can detect wrong optimal depths and invalid solutions.

## Phase 5: First native exact milestone

Goal:
Reach the first honest milestone: a native exact solver that is proven correct on shallow corpora and sampled against an oracle on a controlled deeper set.

Tasks:

- Finalize the first solver API.
- Prove exactness on shallow corpora by exhaustive or near-exhaustive testing.
- Run oracle agreement on a controlled sample of random deeper states.
- Measure search expansion and runtime ceilings.

Decision gate:

At this point we decide whether the native solver is:

- correct but too weak,
- correct and useful enough to extend,
- or architecturally blocked and needing a deeper redesign.

Exit condition:

- We know exactly how far the native solver can currently be trusted.

## Phase 6: Stronger admissible heuristics

Goal:
Improve the lower bound without compromising exactness.

Tasks:

- Re-evaluate the current edge abstraction from first principles.
- Decide whether to redesign edge subsets or introduce a different admissible coordinate split.
- Prove index-space definitions and persistence strategy.
- Add tests that verify indexing round-trips and move consistency for any new abstraction.
- Only then integrate the new lower bound into the exact solver.

Important warning:

We should not try to "salvage" the current `edge_database.py` by wording alone. If the abstraction is weak or under-specified, redesign it.

Exit condition:

- A stronger admissible heuristic stack exists and remains fully lower-bound safe.

## Phase 7: Native exact distance recognizer

Goal:
Make the move-distance requirement explicit and exact.

Tasks:

- Implement `optimal_distance_native(cube)` as the length of the native optimal solution.
- Add tests asserting `optimal_distance_native(cube) == len(solve_exact_native(cube))`.
- Ensure timeout/incomplete-search behavior is reported distinctly from true distances.

Exit condition:

- The repository contains a native exact distance API with explicit semantics. In the current checkout, this API is in `src/korf/native_exact_solver.py`.

## Phase 8: Benchmark and tractability analysis

Goal:
Determine what the native solver can realistically do on this machine and within thesis scope.

Tasks:

- Run controlled benchmarks on shallow and moderate depths.
- Record exact success rates, runtimes, and node expansions.
- Distinguish proven-correct regions from merely sampled regions.
- Determine whether deeper-state experiments are thesis-appropriate or misleading.

Exit condition:

- We have evidence for what the native solver can honestly claim in evaluation.

## Phase 9: Public integration

Goal:
Expose the native exact path cleanly without breaking the rest of the repository.

Tasks:

- Update package exports.
- Add documentation for setup and usage.
- Decide whether demos should call the native solver or keep the external wrapper available separately.
- Keep the external wrapper clearly labeled as external for comparison only.

Exit condition:

- The repo exposes a native exact path unambiguously. Current public exports are documented in `src/korf/__init__.py`.

## Phase 10: Thesis reconciliation

Goal:
Update the thesis only after the native implementation has passed the required gates.

Tasks:

- Rewrite Chapter 5 to describe the actual native architecture.
- Rewrite heuristic sections so they distinguish exact admissible heuristics from exploratory non-admissible ones.
- Rewrite the distance-recognition wording so it maps directly to the native API.
- Remove or rewrite any claim that still depends on the external wrapper.
- Update evaluation methodology and limitations with the measured native solver ceilings.

Exit condition:

- Every exactness claim in the thesis is backed by the actual code and tests.

## Phase 11: Final audit

Goal:
Run the same level of scrutiny on the new exact path that was applied to the rest of the thesis repository.

Tasks:

- re-run tests,
- rebuild reproducible artifacts,
- verify docs and thesis consistency,
- verify screenshots or figures if any new ones are introduced,
- inspect for stale references to the old external-only exact path.

Exit condition:

- No surviving mismatch between code, outputs, and thesis claims.

## 9. Verification Matrix

Every stage needs a matching proof artifact.

### Storage layer

- unit tests for packing/unpacking,
- persistence round-trip tests,
- explicit uninitialized-state tests.

### Coordinate layer

- rank/unrank round-trip tests,
- move application consistency tests,
- solved-state index tests.

### Search layer

- solved cube returns empty solution,
- replay of returned moves solves the state,
- shallow optimal-depth checks,
- deterministic behavior on repeated runs.

### Heuristic layer

- heuristic is zero on solved state,
- heuristic never exceeds known-optimal shallow distances,
- heuristic agrees with pattern-database semantics on indexed states.

### Native distance API

- distance equals solution length,
- solved cube distance is zero,
- shallow corpus exact-depth agreement,
- timeout semantics tested separately.

### Oracle agreement

- sampled random-state equality with the existing external oracle,
- disagreement capture with saved failing seeds and serialized states.

## 10. Risks and Hard Truths

This path is feasible as an engineering program, but it has real risks.

### Risk 1: Performance ceiling

A corner-only heuristic may be exact and still too slow beyond shallow to moderate depths.

Mitigation:

- treat the corner-only native solver as the first correctness milestone,
- only add stronger heuristics after the first milestone is proven.

### Risk 2: Edge abstraction redesign may be large

The current edge database implementation does not look trustworthy enough for an exact claim.

Mitigation:

- do not build the native solver around it yet,
- redesign from first principles if needed.

### Risk 3: Storage optimizations can create silent bugs

Compressed lookup tables are attractive, but ambiguity in packed values destroys trust.

Mitigation:

- start with exact-safe semantics even if memory usage increases.

### Risk 4: Thesis pressure can push premature claims

The biggest danger is not technical failure. It is overstating partial progress as exact completion.

Mitigation:

- do not edit the thesis exactness claims until the validation gates pass.

## 11. Sequential Subagent Plan

The work should be delegated in sequence, not all at once, so each subagent result can tighten the next stage.

### Subagent 1

Role:
Audit and recommend the first exact-safe storage changes.

Deliverable:

- precise change list for `pattern_database.py`,
- test cases required before and after the change,
- whether nibble packing should be retained initially.

### Subagent 2

Role:
Design the cubie-based native search module and move-pruning contract.

Deliverable:

- proposed module layout,
- solver interface,
- move-ordering and pruning rules,
- performance and correctness tradeoffs.

### Subagent 3

Role:
Design the shallow validation corpus and exactness harness.

Deliverable:

- corpus generation method,
- known-depth sources,
- cross-check methodology against the external oracle.

### Subagent 4

Role:
Audit the edge-abstraction path and determine whether it can be repaired or must be replaced.

Deliverable:

- accept/reject recommendation for current `edge_database.py`,
- redesigned state-space definition if rejection is warranted.

### Subagent 5

Role:
Benchmark and verification support once the first native solver slice exists.

Deliverable:

- controlled benchmark script plan,
- logging requirements,
- failure-capture strategy.

### Subagent 6

Role:
Thesis reconciliation after implementation.

Deliverable:

- list of thesis sections that must change,
- exact wording boundaries for native vs external claims.

## 12. Historical Immediate Next Slice

The following list is preserved as historical planning context from before the
current native exact path was implemented. It is not a live task list for the
current checkout:

1. Fix the pattern database storage ambiguity.
2. Add exact-safe tests for storage.
3. Create a new cubie-based native exact solver module skeleton. Current implementation: `src/korf/native_exact_solver.py`.
4. Integrate a corner-only admissible lower bound.
5. Add shallow exactness tests.

Only after those steps passed should deeper heuristic work begin.

## 13. Completion Definition

Path A is complete only if the repository can demonstrate all of the following at the same time:

- a native solver path exists,
- that path does not call the external backend,
- that path returns optimal solutions under the repository's metric,
- a native exact move-distance API exists,
- tests and validation support the claim,
- the thesis wording matches the truth exactly.

The current checkout contains the native path described above, while the final
deep thesis benchmark still uses the external exact backend. Treat this document
as historical scope control, not as the current completion status.
