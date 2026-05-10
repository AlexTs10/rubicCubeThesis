# ChatGPT Pro External Audit - 2026-05-10 14:46

Source thread: https://chatgpt.com/c/6a006d42-afcc-83eb-b8be-18c59bfbf174

The ChatGPT response and JSON copy controls failed in Chrome with "Failed to copy to clipboard"; this file is a faithful manual transcription from the completed visible response exposed in the browser accessibility tree.

## Summary

The auditor used only `repo-audit-20260510-1430.zip`. It reported that it extracted and inspected the uploaded archive, LaTeX thesis sources, checked-in PDF, benchmark JSON, validation artifacts, Python/package config, CI workflow, Dockerfile, README/setup docs, tests, and representative code paths.

The auditor reported running:

- `python -m pytest tests -q`: 289 passed, 30 deselected.
- `python scripts/verification/native_exact_validation.py --preset source-zip --output-dir /tmp/native_exact_source_zip`: 261 cases, 0 failures.
- `python scripts/verify_notebooks.py`: all 6 notebooks passed source smoke check.
- `python scripts/thesis_workflow.py validate`: failed on the audit host because no complete thesis build path was ready.
- `cd thesis && make`: failed for the same host-toolchain reason.
- PDF inspection: `thesis/main.pdf` exists, 112 pages, embedded fonts, no form fields.

Scores:

- Overall thesis quality score: 82/100
- Technical quality score: 78/100
- Submission readiness score: 70/100

The auditor concluded that critical blockers remain because the approval/signature page is not final, and technical quality/submission readiness are below 90.

## Findings

### Critical Blockers

1. `thesis/chapters/00_approval.tex`: final institutional approval page is still a template, with placeholder committee rows and blank examination date. This is non-local and requires official institutional data.

### Thesis Writing Issues

1. `thesis/chapters/07_evaluation.tex`: Chapter 7 discusses the timing table before the solution-length table sequence finishes, creating confusing PDF reading order.
2. `thesis/chapters/05_korf.tex`: pseudocode renders `$None$` poorly as split math text in Algorithm 5.2.
3. `thesis/chapters/05_korf.tex`: long file paths wrap badly in the compiled PDF.

### Technical/Code Issues

1. `.github/workflows/thesis-build.yml` and `README.md`: coverage gate is still only 49%, with evaluation/statistics/validation/visualization modules under-tested.
2. `src/korf/validation.py`: `load_cube20_data()` remains a loud `NotImplementedError` stub.
3. `webapp/package.json`: webapp runtime engines are pinned exactly to Node 24.9.0 and npm 11.6.0, which is brittle for CI/build reproducibility.

### Research/Experimental Issues

1. `thesis/chapters/07_evaluation.tex`: main benchmark corpus is small and lacks repeated runs, confidence intervals, cold/warm timing split, and full original runtime provenance.
2. `thesis/chapters/07_evaluation.tex`: requested scramble length is not actual optimal depth, so depth-based conclusions remain limited.
3. `thesis/chapters/00_abstract_en.tex`, `results/validation/native_exact/README.md`, and `results/validation/native_exact/MANIFEST.json`: canonical native-exact validation cannot be regenerated from the source ZIP alone because it requires omitted cache/oracle artifacts.

### Citation/Reference Issues

1. `thesis/chapters/07_evaluation.tex` and `README.md`: external backend provenance is not fully embedded in the benchmark artifact.
2. `docs/THESIS_OUTLINE.md` and `docs/PATH_A_NATIVE_EXACT_PLAN.md`: historical/supporting docs still contain outdated planning references.

### Reproducibility/Setup Issues

1. `README.md`, `thesis/README.md`, and `scripts/thesis_workflow.py`: documented review build depends on local TeX/Tectonic or Docker availability.
2. `verify_setup.py` and `README.md`: the default verification profile does not verify thesis/webapp artifacts.

### Submission Polish Issues

1. `README.md`: administrative completion is still marked pending, which is acceptable for technical review but not final submission.
