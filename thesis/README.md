# Thesis LaTeX Project

This directory contains the thesis manuscript and its build assets. A review PDF can be built with the current XeLaTeX-compatible workflow or the tested Tectonic path. The final institutional submission build is not complete until `chapters/00_approval.tex` contains the official committee names and examination date and is included in `main.tex`.

## Structure

```text
thesis/
├── main.tex
├── references.bib
├── Makefile
├── chapters/
│   ├── 00_titlepage.tex
│   ├── 00_approval.tex
│   ├── 00_acknowledgements.tex
│   ├── 00_abstract_gr.tex    # Complete
│   ├── 00_abstract_en.tex    # Complete
│   ├── 01_introduction.tex   # Complete
│   ├── 02_background.tex     # Complete
│   ├── 03_thistlethwaite.tex # Complete
│   ├── 04_kociemba.tex       # Complete
│   ├── 05_korf.tex           # Complete
│   ├── 06_heuristics.tex     # Complete
│   ├── 07_evaluation.tex     # Complete
│   ├── 08_implementation.tex # Complete
│   ├── 09_conclusions.tex    # Complete
│   ├── appendix_a.tex        # Complete
│   └── appendix_b.tex        # Complete
├── figures/                  # Benchmark figures copied from ../figures/
```

## Build Paths

### Preferred Review-Build Command

From the repository root:

```bash
python scripts/thesis_workflow.py build --mode auto
```

`build --mode auto` is the documented review-build path. It prefers `latexmk -xelatex` when available, then a manual `xelatex` + bibliography pass sequence, then the tested local `tectonic` path, and finally Docker. Do not use `pdflatex` for this manuscript because Greek/Unicode listing content requires a Unicode-capable engine. If none of local TeX, Tectonic, or a running Docker daemon is available, the command fails explicitly instead of pretending that the checked-in PDF was rebuilt.

From `thesis/`:

```bash
make
make docker
make local
make clean
make view
```

For Docker-only validation:

```bash
python scripts/thesis_workflow.py build --mode docker
```

Docker mode builds the default image from `docker/thesis.Dockerfile` in this
repository and then runs `latexmk -xelatex` inside that image. This keeps the
review build path source-defined when the host machine does not already have a
TeX installation.

The Docker route requires Docker Engine/OrbStack/Colima to be installed and the
daemon to be running before `build --mode docker` is invoked. A machine without
any local TeX engine and without a running container runtime can still inspect
the checked-in `thesis/main.pdf`, but cannot independently rebuild it until one
of those prerequisites is installed.

If Docker is installed but not running on macOS, start it with:

```bash
open -a Docker
```

### Manual Local Compilation

```bash
tectonic --keep-intermediates --keep-logs --reruns 0 --pass tex main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass bibtex_first main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass tex main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass tex main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass tex main.tex
```

If you are using a classic TeX toolchain instead of `tectonic`, build with XeLaTeX:

```bash
latexmk -xelatex main.tex
```

Or run the passes manually:

```bash
xelatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

## Workflow Commands

```bash
# Print the current thesis status
python scripts/thesis_workflow.py status

# Re-run workflow validation
python scripts/thesis_workflow.py validate

# Rebuild chapter packets if needed
python scripts/thesis_workflow.py packets --remaining
```

## Editing Guide

1. Edit individual chapter files in `chapters/`, not `main.tex`.
2. Add citations to `references.bib` and use `\cite{key}` in the chapter text.
3. Keep figure assets in `figures/` or refer to repo-level diagrams with verified relative paths.
4. Re-run the workflow status and validation commands after substantial chapter edits.

Generated workflow snapshots can be written to `agent_workflow/generated/` for
local review, but that directory is excluded from source audit archives because
the files are host-specific.

## Internal QA Notes

The submission archive should be judged from the regenerated validation output
and built PDF, not from a persistent checklist in this README. Re-run the
workflow validation/build commands on the final build machine before submitting.
