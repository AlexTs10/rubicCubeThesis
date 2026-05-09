# Remaining Failures - 2026-05-09 10:49

## External or Deferred Blockers

- Formal approval/signature page remains an external institutional blocker. `thesis/chapters/00_approval.tex` still needs the official committee members and examination date before it can be included in `thesis/main.tex`; these details should not be fabricated locally.
- Canonical native exact validation still requires the generated `data/pattern_databases/corner_db.pkl` cache. The source ZIP now documents this clearly and provides `--preset source-zip` as the cache-free smoke validation.
- Full benchmark rerun with repeated trials, randomized solver order, isolated peak-RSS subprocess measurement, and contemporaneous run metadata was not performed in this loop.
- Hash-locked Python dependencies and full TeX/Node artifact hashes remain deferred. `requirements.lock` is still a pinned package snapshot, not a cryptographic lock file.
- External exact backend provenance is improved with package version and installed license-file hash, but the original benchmark artifact still lacks a wheel hash or upstream commit hash captured at run time.

## Validation Notes

- `npm audit --audit-level=moderate` still reports the known Next.js/PostCSS advisory. `npm audit fix --force` proposes installing `next@9.3.3`, which would be an unsafe breaking downgrade, so no automatic fix was applied.
- The thesis build succeeds. Remaining TeX warnings are underfull hboxes only; the Chapter 5 overfull table introduced during this loop was fixed.
