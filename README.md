# Rubik's Cube Thesis Repository

**Author:** Alex Toska

**Institution:** University of Patras

**Project Type:** Undergraduate / Bachelor's thesis in ECE
**Current State:** Technical review package. The manuscript, codebase, benchmarks, and local build workflow are present, but this is not yet a final submission bundle: the approval/signature page still requires the remaining committee names and examination date from the University of Patras.

This repository contains the implementation, evaluation, and thesis manuscript for a comparative study of three classical Rubik's Cube solving algorithms:

- Thistlethwaite's 4-phase method
- Kociemba's 2-phase algorithm
- Korf-style optimal search with pattern databases

Source code, tests, scripts, documentation, and LaTeX sources are the editable source of truth. Checked-in benchmark JSON under `results/benchmarks/thesis/` is the canonical evidence for the submitted Chapter 7 benchmark results and can be regenerated with the documented benchmark scripts. Generated PDFs and workflow snapshots under `agent_workflow/generated/` are local outputs, not portable authority.

For final thesis benchmark claims, use the checked-in benchmark artifacts under `results/benchmarks/thesis/` together with the thesis text in `thesis/chapters/07_evaluation.tex`. Do not cite ad hoc demo output or legacy benchmark scripts as final results.

The Next.js frontend under `webapp/` is a synthetic preview layer for demos and presentations. Its move sequences are generated preview outputs rather than live solver telemetry, so use the Python benchmark artifacts and thesis sources when you need authoritative results.

## Where To Start

If you want the current thesis state, start from a clean Python environment. The
supported review range is Python 3.12 through Python 3.14; Python 3.12 is the
recommended baseline for reproducing the thesis environment.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --require-hashes -r requirements.lock
python -m pip install --no-deps -e .
python verify_setup.py
python -m pytest tests -q
python scripts/thesis_workflow.py status
python scripts/thesis_workflow.py validate
python scripts/thesis_workflow.py build --mode auto
python scripts/create_audit_zip.py
```

Use `requirements.lock` as the hash-locked Python dependency snapshot for the
audited environment. Install it with `python -m pip install --require-hashes -r
requirements.lock` when reproducing the audited Python environment. The lock
does not pin TeX/Tectonic, OS packages, or Node tooling. Node and npm are pinned
for the preview app with the root `.nvmrc`, `webapp/package.json`
(`packageManager` and `engines`), and `webapp/.npmrc` (`engine-strict=true`).
Before running `npm ci`, use the pinned Node/npm toolchain explicitly:

```bash
nvm install
nvm use
corepack enable
corepack prepare npm@11.6.0 --activate
cd webapp
npm ci
```

This avoids failing under a system Node LTS release while `engine-strict=true`
is active. Use `requirements.txt` only when you need a flexible dependency
range for local development.

The hash-locked `requirements.lock` is the full audited Python environment.
The editable package keeps only core solver dependencies in base
`pyproject.toml`. Optional extras separate lighter install stacks:
`.[native]`, `.[external-exact]`, `.[benchmark]`, `.[ui]`, `.[test]`,
`.[notebooks]`, `.[dev]`, and `.[thesis]` for the full thesis environment.

The default pytest/verification profile is intentionally the fast reproducibility profile. It excludes tests marked `slow`, `external`, or `cache_building`; run those markers explicitly only when validating generated caches or external backends. Generated workflow snapshots may be written under `agent_workflow/generated/` during local work, but that directory is intentionally excluded from source audit ZIPs.

GitHub Actions keeps that fast profile on pull requests and adds an opt-in
expanded profile for heavier solver validation. Run the `thesis-build`
workflow manually with `run-expanded-validation=true`, or use the weekly
scheduled run, to execute tests marked `slow`, `external`, or
`cache_building` with `pytest -o addopts='' -m "slow or external or
cache_building"`. The workflow uploads collection, test, and canonical
native-exact logs as artifacts; canonical native-exact validation is skipped
unless the companion `data/pattern_databases/corner_db.pkl` cache is supplied.

The thesis build workflow now has a source-defined Docker fallback. If local
`latexmk`/`xelatex`/bibliography tooling and `tectonic` are absent but Docker is
running, `python scripts/thesis_workflow.py build --mode auto` switches to
Docker mode and builds the TeX image from `docker/thesis.Dockerfile` before
compiling `thesis/main.tex`.

For review systems that should not depend on local TeX state, the repository
also includes `.github/workflows/thesis-build.yml`. That workflow validates the
thesis sources, builds `thesis/main.pdf` with the source-defined Docker image,
and uploads the PDF plus a SHA-256 hash as CI artifacts.

On a clean reviewer machine with Docker but no local TeX installation, the
single thesis-build command is:

```bash
python scripts/thesis_workflow.py build --mode docker
shasum -a 256 thesis/main.pdf
```

The compiled thesis PDF is written to `thesis/main.pdf`.
The archive-verifiable source manifest is written to
`REPRODUCIBILITY_MANIFEST.json`, and the matching audit ZIP is written under
`audit-results/packages/`.

## Repo Layout

```text
repository-root/
├── src/                        # Solver implementations and evaluation code
├── tests/                      # Unit and integration tests
├── data/                       # Generated-cache documentation and excluded large databases
├── demos/                      # Runnable demo scripts
├── docker/                     # Source-defined thesis build container
├── docs/                       # Technical docs and supporting notes
├── figures/                    # Thesis and benchmark figures
├── notebooks/                  # Educational and exploratory notebooks
├── papers/                     # Bibliography notes; local PDFs are excluded from audit ZIPs
├── scripts/                    # Workflow, benchmarking, and utility scripts
├── results/                    # Benchmark outputs and generated reports
├── thesis/                     # LaTeX manuscript and references
├── ui/                         # Streamlit execution UI
├── webapp/                     # Next.js synthetic preview app
└── agent_workflow/             # Repo-local thesis workflow prompts and outputs
```

## Algorithms

### Thistlethwaite

- 4-phase group-theoretic reduction
- strong educational value and clear subgroup structure
- lower average solve time than Kociemba on the current thesis benchmark corpus, but clearly longer solutions

### Kociemba

- 2-phase IDA* approach
- best overall practical performance in this repository
- optional PyPI/native-extension `kociemba` backend is required for the full thesis test/benchmark environment; this is distinct from repository-native solver code

### Korf / IDA*

- exact benchmark path provided by `KorfOptimalSolver` when `RubikOptimal` is installed
- strongest optimality guarantees in the repository, but only on completed runs within the configured timeout
- native exact search support is implemented separately in `src/korf/native_exact_solver.py` and validated on the native-exact corpus; the canonical 100-scramble thesis benchmark still records the external optimal backend
- the full canonical native-exact validation requires the generated `data/pattern_databases/corner_db.pkl` companion cache; the source ZIP includes a smaller `--preset source-zip` smoke check instead
- the internal Python heuristic/composite path is retained for exploratory experiments and is not presented as generally admissible
- the exact `KorfOptimalSolver` wrapper is imported lazily
- the first exact-optimal solve may generate large backend tables and is much faster under PyPy
- computationally expensive, so benchmark tractability is lower than the other solvers

The benchmark/evaluation path now uses the external exact backend with enforced timeouts. In the corrected thesis benchmark, it solved 97/100 scrambles overall and timed out on 3 of 25 cases at requested scramble length 20.

Importing `src.korf` does not load the exact solver backend. The optional `RubikOptimal` package is only imported when `KorfOptimalSolver` is instantiated or `solve_optimal()` is called.

### Optional Exact Backend

`RubikOptimal>=1.1.0` is listed in `requirements.txt` for the full thesis benchmark environment and under the `external-exact` project extra. On this machine, the installed distribution is `RubikOptimal 1.1.0`, importable as `optimal`, with package metadata pointing to Herbert Kociemba's `RubiksCube-OptimalSolver` repository. The installed wheel includes `RubikOptimal-1.1.0.dist-info/LICENSE` with SHA-256 `53927bd0b739d38c87a0a82236fd9b070c2dfff11c0c119be50372005d5047ad`, `RubikOptimal-1.1.0.dist-info/METADATA` with SHA-256 `53c0f4acad5f676edd194e155c92d259c559c03d050b50897ccaeba26ad236e0`, and `optimal/solver.py` with SHA-256 `a6f6d67ca3f3cd3bbc93004e3db62abef4dc3d1996470f016048201ff80d4246`. The PyPI metadata does not expose a `License` field, so do not invent a license label in thesis-facing documentation; inspect the package or upstream repository if a formal license statement is needed.

The benchmark JSON records package metadata and file hashes, but the upstream
commit/tag is not known from the installed wheel metadata and remains a
third-party provenance gap unless the exact upstream source archive is supplied
as a companion artifact.

## Reproduction Tiers

For a checklist organized by claim tier, see [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

| Tier | Commands | Required external artifacts/backends | Claims covered |
| --- | --- | --- | --- |
| Minimal source-contained review | `python verify_setup.py`, `python -m pytest tests -q`, `python scripts/verification/native_exact_validation.py --preset source-zip` | None beyond the Python lockfile | Fast regression health and source-ZIP native-exact smoke validation |
| Thesis PDF rebuild | `python scripts/thesis_workflow.py build --mode auto` or `--mode docker` | Local TeX/Tectonic or Docker | Manuscript build and PDF hash generation |
| Web preview rebuild | `nvm install && nvm use`, `corepack prepare npm@11.6.0 --activate`, `cd webapp && npm ci && npm test && npm run build` | Node 24.9.x/npm 11.6.x | Synthetic Next.js preview only |
| Containerized web preview rebuild | `docker build -f docker/webapp.Dockerfile -t rubic-cube-thesis-webapp .` then `docker run --rm rubic-cube-thesis-webapp` | Docker and the source tree | Synthetic Next.js preview tests/build without host Node guessing |
| Full benchmark reproduction | `python -m pip install ".[external-exact]"`, `python scripts/benchmarks/regenerate_thesis_benchmarks.py` | `RubikOptimal` and optional native solver backends | Chapter 7 benchmark artifacts |
| Canonical native-exact validation | `python scripts/generate_corner_database.py --output data/pattern_databases/corner_db.pkl`, then `python scripts/verification/native_exact_validation.py --preset canonical` | Generated `corner_db.pkl` companion cache and `RubikOptimal` oracle | Archived 3,513-case native-exact comparison |

## Thesis Workflow

The repo includes a lightweight workflow driver in [`scripts/thesis_workflow.py`](scripts/thesis_workflow.py):

- `status`: chapter coverage, citations, benchmark assets, and codebase stats
- `validate`: lightweight readiness checks
- `packet` / `packets`: chapter packets for agent-assisted writing or review
- `build`: local or Docker thesis compilation

Useful source files:

- [`thesis/README.md`](thesis/README.md)

Optional local snapshots can be regenerated with:

```bash
python scripts/thesis_workflow.py status --output agent_workflow/generated/status.md
python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md
```

Those generated files are host-specific and are not included in source audit archives.

## Local Verification Snapshot

These generated results are local evidence, not a portable source of truth. Re-run
the commands below in a clean Python 3.12 environment for the current machine.

- `python -m pytest tests --collect-only -q` reports the collected test count for the current checkout; the default fast profile excludes `slow`, `external`, and `cache_building`
- `python -m pytest tests -q` runs the supported fast profile; heavyweight solver-quality, external-backend, and cache-generation checks are opt-in marker profiles
- `python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered --cov-fail-under=49` is the conservative coverage gate for the current source tree; raise the threshold only after adding tests for the low-coverage evaluation and generated-table modules
- Runtime-generated solver tables default to a user cache such as `$XDG_CACHE_HOME/rubic_cube_thesis/`; repository `data/` remains read-only unless an explicit cache-generation command is run.
- `python verify_setup.py` runs the Python-only setup profile and fast tests by default; it does not verify thesis PDF or webapp artifacts unless `--all-artifacts` is supplied. Use `--full` for heavyweight Python tests and `--all-artifacts` when local TeX/Docker plus webapp dependencies are available
- `cd webapp && npm ci && npm run build` succeeds from a clean dependency install
- `python scripts/thesis_workflow.py build --mode auto` rebuilds `thesis/main.pdf` with local TeX/Tectonic when available, or with the repo-local Docker image from `docker/thesis.Dockerfile` when Docker is running; the Dockerfile pins `debian:bookworm-slim` by digest
- the manuscript chapters and appendices are present in `thesis/chapters/`

There is no active top-level `TESTING_REPORT.md` in this checkout. Treat any older testing report copied from another branch or artifact bundle as historical unless it is regenerated from the commands above. This repository should be called final-submission ready only after the University approval/signature page has the official committee metadata and examination date.

## Next.js Preview

From the repository root:

```bash
cd webapp
nvm install
nvm use
corepack enable
corepack prepare npm@11.6.0 --activate
npm ci
npm run build
npm run dev
```

For a host-independent reviewer path, run from the repository root:

```bash
docker build -f docker/webapp.Dockerfile -t rubic-cube-thesis-webapp .
docker run --rm rubic-cube-thesis-webapp
```

Use this only for the synthetic demo frontend. The authoritative execution path remains the Streamlit UI in `ui/` and the Python benchmark pipeline.

## Thesis Sources

Main manuscript entrypoint:

- [`thesis/main.tex`](thesis/main.tex)

Important supporting files:

- [`thesis/references.bib`](thesis/references.bib)
- [`docs/CODE_TO_THESIS_MAPPING.md`](docs/CODE_TO_THESIS_MAPPING.md)
- [`docs/demos_and_ui.md`](docs/demos_and_ui.md)
