# Remaining Validation Failures - 2026-05-08 23:16

## npm audit

Command:

```bash
npm --prefix webapp audit --audit-level=moderate
```

Status: failed after `npm --prefix webapp audit fix` reduced the advisory set.

Remaining advisories:

- `postcss <8.5.10` through `next/node_modules/postcss`
- `next 9.3.4-canary.0 - 16.3.0-canary.5` depends on the vulnerable bundled `postcss`

Why not auto-fixed:

`npm audit` reports that the only available automatic remediation is:

```bash
npm audit fix --force
```

That would install `next@9.3.3`, which is a breaking downgrade from the current Next 16 line. The webapp lockfile was updated to Next `16.2.6`, root `postcss` `8.5.14`, patched `brace-expansion`, and patched `picomatch`, but Next still bundles `postcss` `8.4.31`.

Follow-up:

Track a non-breaking Next release that updates the bundled PostCSS dependency, or explicitly test a newer canary only if the thesis webapp accepts canary framework risk.
