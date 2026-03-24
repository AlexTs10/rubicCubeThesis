# Rubik's Cube Thesis Repository

**Author:** Alex Toska

**Institution:** University of Patras

**Project Type:** Undergraduate / Bachelor's thesis in ECE
**Current State:** Thesis manuscript, codebase, benchmarks, and local build workflow are all present

This repository contains the implementation, evaluation, and thesis manuscript for a comparative study of three classical Rubik's Cube solving algorithms:

- Thistlethwaite's 4-phase method
- Kociemba's 2-phase algorithm
- Korf-style optimal search with pattern databases

Generated artifacts such as `thesis/main.pdf`, benchmark outputs under `results/benchmarks/thesis/`, and workflow outputs under `agent_workflow/generated/` are not the source of truth. The source of truth lives in `src/`, `tests/`, `scripts/`, `docs/`, and `thesis/`.

The Next.js frontend under `webapp/` is a synthetic preview layer for demos and presentations. Use the Python benchmark artifacts and thesis sources when you need authoritative results.

## Where To Start

If you want the current thesis state, use these commands from the repo root:

```bash
python verify_setup.py
python -m pytest tests -q
python scripts/thesis_workflow.py status --output agent_workflow/generated/status.md
python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md
python scripts/thesis_workflow.py build --mode auto
```

The compiled thesis PDF is written to `thesis/main.pdf`.

## Repo Layout

```text
rubicCubeThesis/
├── src/                        # Solver implementations and evaluation code
├── tests/                      # Unit and integration tests
├── demos/                      # Runnable demo scripts
├── docs/                       # Technical docs and supporting notes
├── papers/                     # Literature collection and bibliography notes
├── scripts/                    # Workflow, benchmarking, and utility scripts
├── results/                    # Benchmark outputs and generated reports
├── thesis/                     # LaTeX manuscript and references
└── agent_workflow/             # Repo-local thesis workflow prompts and outputs
```

## Algorithms

### Thistlethwaite

- 4-phase group-theoretic reduction
- strong educational value and clear subgroup structure
- slower and longer solutions than Kociemba on the benchmark set

### Kociemba

- 2-phase IDA* approach
- best overall practical performance in this repository
- optional native `kociemba` backend is used when available for faster short-timeout solves

### Korf / IDA*

- exact benchmark path provided by `KorfOptimalSolver` when `RubikOptimal` is installed
- strongest optimality guarantees in the repository, but only on completed runs within the configured timeout
- the internal Python heuristic/composite path is retained for exploratory experiments and is not presented as generally admissible
- the exact `KorfOptimalSolver` wrapper is imported lazily
- the first exact-optimal solve may generate large backend tables and is much faster under PyPy
- computationally expensive, so benchmark tractability is lower than the other solvers

The benchmark/evaluation path now uses the external exact backend with enforced timeouts. In the corrected thesis benchmark, it solved 97/100 scrambles overall and timed out on 3 of 25 depth-20 cases.

Importing `src.korf` does not load the exact solver backend. The optional `RubikOptimal` package is only imported when `KorfOptimalSolver` is instantiated or `solve_optimal()` is called.

## Thesis Workflow

The repo includes a lightweight workflow driver in [scripts/thesis_workflow.py](/Users/alextoska/Desktop/rubicCubeThesis/scripts/thesis_workflow.py):

- `status`: chapter coverage, citations, benchmark assets, and codebase stats
- `validate`: lightweight readiness checks
- `packet` / `packets`: chapter packets for agent-assisted writing or review
- `build`: local or Docker thesis compilation

Useful files:

- [agent_workflow/generated/status.md](/Users/alextoska/Desktop/rubicCubeThesis/agent_workflow/generated/status.md)
- [agent_workflow/generated/validation.md](/Users/alextoska/Desktop/rubicCubeThesis/agent_workflow/generated/validation.md)
- [thesis/README.md](/Users/alextoska/Desktop/rubicCubeThesis/thesis/README.md)

## Current Verification Snapshot

- `python -m pytest tests --collect-only -q` reports `269 tests collected`
- `python -m pytest tests -q` reports `268 passed, 1 skipped`
- `verify_setup.py` passes in this environment (`7/7` checks; nested full suite completed in `512.03s`)
- the thesis builds locally with `tectonic`
- the manuscript chapters and appendices are present in `thesis/chapters/`

## Thesis Sources

Main manuscript entrypoint:

- [thesis/main.tex](/Users/alextoska/Desktop/rubicCubeThesis/thesis/main.tex)

Important supporting files:

- [thesis/references.bib](/Users/alextoska/Desktop/rubicCubeThesis/thesis/references.bib)
- [docs/CODE_TO_THESIS_MAPPING.md](/Users/alextoska/Desktop/rubicCubeThesis/docs/CODE_TO_THESIS_MAPPING.md)
- [docs/demos_and_ui.md](/Users/alextoska/Desktop/rubicCubeThesis/docs/demos_and_ui.md)
