# Remaining Audit Items After Local Fix Pass

Source audit: `audit-results/chatgpt-pro-audit-20260509-1644/`

The local pass addressed concrete code, documentation, metadata, and thesis-text
issues that could be fixed from repository evidence. The following targets
remain blocked or intentionally deferred because fixing them correctly requires
external institutional facts, heavyweight reruns, or a separate final artifact
decision.

## Remaining Blockers

- `thesis/chapters/00_approval.tex`: the approval/signature page is now included
  in `thesis/main.tex`, but the final signed institutional copy still requires
  the two remaining committee names, roles, and examination date from the
  University of Patras process. These should not be fabricated in source.
- `data/pattern_databases/corner_db.pkl`: the full canonical native-exact
  validation cache is still omitted from the source ZIP. The repository now
  documents it as a generated companion artifact and keeps the source-ZIP smoke
  preset executable, but final canonical reruns need either a generated cache or
  a separately supplied SHA-256 manifest entry.

## Deferred Experimental Work

- Repeated-trial benchmark rerun with confidence intervals, cold/warm timing
  separation, and isolated peak RSS remains a larger experimental rerun, not a
  safe quick patch to the checked-in canonical 100-scramble results.
- Docker TeX dependency immutability is still limited by mutable Debian package
  repositories. The current Dockerfile pins the base image digest; full snapshot
  pinning should be done in a dedicated container-reproducibility pass.
- Fully executable notebook verification is still not part of the default
  source-ZIP smoke profile. The current `scripts/verify_notebooks.py` remains a
  structural check.
- Tagged/accessible PDF polish was not addressed in this loop.
