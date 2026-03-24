# Thesis LaTeX Project

This directory contains the thesis manuscript and its build assets. The manuscript is complete and buildable with the current Tectonic path. The remaining work is review, formatting polish, and final PDF verification.

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
└── specs/                    # Chapter-specific writing specs
```

## Build Paths

### Preferred Commands

From the repository root:

```bash
python scripts/thesis_workflow.py build --mode auto
python scripts/thesis_workflow.py build --mode docker
```

From `thesis/`:

```bash
make
make docker
make local
make clean
make view
```

`build --mode auto` prefers a local `tectonic` build, then falls back to a local `pdflatex` + bibliography toolchain that matches [`main.tex`](/Users/alextoska/Desktop/rubicCubeThesis/thesis/main.tex), and finally to Docker. If Docker is installed but not running on macOS, start it with:

```bash
open -a Docker
```

### Manual Local Compilation

```bash
tectonic --keep-intermediates --keep-logs --reruns 0 --pass tex main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass bibtex_first main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass tex main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass tex main.tex
tectonic --keep-intermediates --keep-logs --reruns 0 --pass bibtex_first main.tex
```

If you are using a classic TeX toolchain instead of `tectonic`, follow the current bibliography configuration in [`main.tex`](/Users/alextoska/Desktop/rubicCubeThesis/thesis/main.tex):

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Workflow Commands

```bash
# Regenerate the thesis status snapshot
python scripts/thesis_workflow.py status --output agent_workflow/generated/status.md

# Re-run workflow validation
python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md

# Rebuild chapter packets if needed
python scripts/thesis_workflow.py packets --remaining
```

## Editing Guide

1. Edit individual chapter files in `chapters/`, not `main.tex`.
2. Add citations to `references.bib` and use `\cite{key}` in the chapter text.
3. Keep figure assets in `figures/` or refer to repo-level diagrams with verified relative paths.
4. Re-run the workflow status and validation commands after substantial chapter edits.

## Progress Tracking

- [x] Manuscript chapters complete
- [x] Appendices complete
- [x] Benchmark figures and JSON inputs present
- [x] Workflow validation reports no open workflow targets
- [ ] Abstracts and front matter final review
- [ ] Final proofreading and formatting pass
- [ ] Final PDF inspection
