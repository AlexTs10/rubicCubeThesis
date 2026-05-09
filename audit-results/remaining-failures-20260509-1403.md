# Remaining Audit Items

Generated during the 2026-05-09 ChatGPT Pro audit loop after applying local fixes.

## External blocker

- `thesis/chapters/00_approval.tex` still requires official committee names, roles, and examination date before final institutional submission. I did not fabricate these values. The review PDF build remains valid, but the approval page should stay excluded until the official data is available.

## Documented limitation

- `requirements.lock` is exact-version pinned but not hash-locked. This remains documented as a reproducibility limitation because converting to a hash-locked lockfile requires regenerating dependency hashes for the target installer/index environment and revalidating installation with `pip install --require-hashes -r requirements.lock`.

## Non-blocking validation output

- The thesis rebuild passed via Tectonic and produced `thesis/main.pdf`.
- TeX emitted existing underfull hbox warnings. No build-stopping LaTeX errors occurred.
