# Remaining Validation Failures - 2026-05-09 01:18

## npm audit

- Command: `npm --prefix webapp audit --audit-level=moderate`
- Result: failed with two moderate advisories.
- Cause: `next` currently depends on a vulnerable bundled `postcss <8.5.10` range.
- Available automated fix: `npm audit fix --force`, but npm reports that it would install `next@9.3.3`, a breaking downgrade from the current Next 16 line.
- Local decision: do not force the downgrade in this repair pass. Keep `npm ci`, `npm run build`, and `npm run lint` green, and revisit when a non-breaking Next/PostCSS advisory fix is available.
