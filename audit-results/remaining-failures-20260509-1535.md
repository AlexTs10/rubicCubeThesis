# Remaining Failures After ChatGPT Pro Audit 20260509-1514

## Still blocked by external or non-local inputs

- **C1 institutional approval page**: `thesis/chapters/00_approval.tex` still needs official committee names and examination date before it can be included in `thesis/main.tex`.
- **R2 benchmark statistical strength**: the checked-in 100-scramble benchmark remains a single-run corpus without repeated runs, confidence intervals, or cold/warm split. The thesis text now labels this limitation more explicitly, but a full rerun is still needed to remove the issue.
- **R4 full canonical native exact validation from source ZIP**: the source ZIP still intentionally excludes `data/pattern_databases/corner_db.pkl`. The source-ZIP smoke preset passes; the canonical preset requires the external/generated full corner cache.
- **RS1 cryptographic Python lock**: `requirements.lock` is still not a hash-locked, platform/ABI-constrained environment lock.
- **RS2 apt-level Docker reproducibility**: `docker/thesis.Dockerfile` still depends on live Debian package repositories after the pinned base image digest.
- **SP1 tagged PDF**: `thesis/main.pdf` is still not tagged for accessibility. No institutional requirement/exemption is available in the repository.

## Locally mitigated in this pass

- Removed the circular `reproducibility_manifest_sha256` from benchmark metadata and regenerated `REPRODUCIBILITY_MANIFEST.json`.
- Aligned the Chapter 6 Manhattan heuristic formula with the implementation.
- Clarified requested scramble length semantics, external exact backend wording, benchmark limitations, and Chapter 8 artifact references.
- Fixed stale source references in Chapters 5 and 6.
- Added validation for externally supplied `RubikCube` states.
- Fixed basename-only `PatternDatabase.save`.
- Preserved external backend stdout parsing even in verbose mode.
- Added explicit IDA* timeout/depth-limit/solution status fields.
- Quieted Kociemba initialization when `verbose=False`.
- Removed unsupported learning claims from `CompositeHeuristic`.
