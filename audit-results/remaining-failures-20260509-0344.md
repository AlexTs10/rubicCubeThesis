# Remaining Validation Failures - 2026-05-09 03:44

## npm audit

- Command: `npm --prefix webapp audit --audit-level=moderate`
- Status: failed
- Finding: `postcss <8.5.10` moderate advisory `GHSA-qx2v-qp2m-jg93`, pulled through `next`.
- npm's suggested `npm audit fix --force` would downgrade/install `next@9.3.3`, which is a breaking and inappropriate fix for the current Next.js application.
- Current decision: document the advisory and leave the dependency tree intact until an upstream Next.js release provides a compatible non-breaking remediation.

## Thesis build warnings

- Command: `.venv/bin/python scripts/thesis_workflow.py build --mode auto`
- Status: passed
- Notes: Tectonic emitted underfull hbox warnings in several thesis paragraphs and bibliography entries. These are layout polish warnings, not build blockers.
