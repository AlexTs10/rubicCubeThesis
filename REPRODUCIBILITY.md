# Reproducibility Checklist

This file separates what the source ZIP proves directly from what requires
generated caches, external solver packages, or institutional data.

## Source-ZIP Reproducible

Run these from a clean Python 3.12 environment after installing
`requirements.lock`:

```bash
python verify_setup.py
python -m pytest tests -q
python scripts/verification/native_exact_validation.py --preset source-zip
python scripts/verify_notebooks.py
```

This tier covers fast regression health, notebook executability, and the
source-contained 261-case native-exact smoke validation. It does not claim to
reproduce the full canonical native-exact corpus or the full benchmark campaign.

## Requires Generated Cache

The canonical native-exact validation requires the full corner pattern database:

```bash
python scripts/generate_corner_database.py --output data/pattern_databases/corner_db.pkl
python scripts/verification/native_exact_validation.py --preset canonical
```

`data/pattern_databases/corner_db.pkl` is intentionally omitted from source
audit ZIPs, so the source ZIP alone cannot reproduce the archived canonical
3,513-case run exactly. Final archival reruns should either generate the cache
locally or receive it as a companion artifact with a SHA-256 manifest entry.

## Requires External Backend

Full thesis benchmark reproduction additionally depends on optional external
solver packages, including `RubikOptimal`:

```bash
python -m pip install ".[external-exact]"
python scripts/benchmarks/regenerate_thesis_benchmarks.py
```

The checked-in thesis benchmark JSON remains the authoritative evidence for the
Chapter 7 numbers in this technical review package. A fresh rerun may differ in
timing because the original campaign did not record repeated trials, confidence
intervals, complete kernel/process metadata, or an upstream source commit for
the external exact backend.

## Thesis PDF Build

Use Docker for the most reviewer-independent PDF build path:

```bash
python scripts/thesis_workflow.py build --mode docker
shasum -a 256 thesis/main.pdf
```

If Docker is unavailable, `--mode auto` attempts local `latexmk`/XeLaTeX,
manual XeLaTeX, Tectonic, and finally Docker when a container runtime is
available. The GitHub Actions thesis workflow records the PDF hash as a CI
artifact.

## Final Submission Preconditions

The source package is a technical review package until the University of Patras
approval/signature page has the final committee names, titles, and examination
date. Do not label the package as a final submission bundle while
`thesis/chapters/00_approval.tex` still contains placeholders.
