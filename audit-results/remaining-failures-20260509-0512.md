# Remaining Validation / Audit Blockers

Generated: 2026-05-09 05:12 Europe/Athens

## Final institutional approval page remains blocked

- Source audit target: `thesis/main.tex`; `thesis/chapters/00_approval.tex`
- Status: not fixed locally because the repository does not contain the official committee names or examination date.
- Current handling: `thesis/main.tex` and `thesis/README.md` now explicitly describe the PDF as a review build and state that final institutional front matter is pending.
- Required user/institution input: final three committee entries, signature-page order, and examination date.

## npm audit remains blocked on upstream Next/PostCSS advisory

- Command: `npm --prefix webapp audit --audit-level=moderate`
- Status: fails with 2 moderate vulnerabilities through `next -> postcss`.
- Reason not auto-fixed: `npm audit fix --force` proposes a breaking downgrade to `next@9.3.3`, which would be inappropriate for this app.
- Current validation status: `npm --prefix webapp run lint`, `npm --prefix webapp test`, and `npm --prefix webapp run build` pass after `npm --prefix webapp ci`.

## PDF metadata verification note

- `thesis/main.tex` now defines `pdftitle`, `pdfauthor`, `pdfsubject`, and `pdfkeywords`.
- `mdls` confirms title and keywords on macOS. `/opt/homebrew/bin/pdfinfo thesis/main.pdf` hung in this local shell, so it was killed and was not used as validation evidence.
