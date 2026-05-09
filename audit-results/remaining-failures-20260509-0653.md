# Remaining Validation / Submission Issues

Generated: 2026-05-09 06:53 Europe/Athens

## Failed Checks

- `cd webapp && npm audit --audit-level=moderate` fails because `next@16.2.6`
  depends on `postcss <8.5.10`, matching GitHub advisory
  `GHSA-qx2v-qp2m-jg93`. `npm audit fix --force` proposes downgrading to
  `next@9.3.3`, which is a breaking and inappropriate automatic remediation.

## Unresolved Audit Blockers Requiring External Input

- Final institutional approval/front-matter data remains pending. The repository
  still needs official committee names/titles/signature date before the approval
  page can be completed and included as final submission front matter.

## Documented Residual Risks

- Python dependency locking is still `requirements.lock` without hashes. The
  setup verifier now checks this pinned file exactly, but a cryptographic
  lockfile such as a hash-generated pip-tools lock or `uv.lock` remains a
  future hardening step.
- The canonical native exact validation still requires a generated full corner
  database cache. The repository now includes `scripts/generate_corner_database.py`
  and documents the prerequisite, but the large `corner_db.pkl` artifact remains
  excluded from source audit ZIPs.
- Citation-content verification from the ZIP remains limited because source PDFs
  are not included. Bibliography metadata and acquisition logs are present, but
  a claim-to-reference evidence table or permitted evidence bundle is still
  needed for full source-text verification.
