# Remaining Pro Audit Items

Source audit folder: `audit-results/chatgpt-pro-audit-20260509-2106/`

The local pass addressed the actionable repository issues from the 24 FIX_TARGETS: external pytest marker collection, canonical-validation prerequisite text, stale appendix/code comments, hash-locked setup messaging, globally unique benchmark case IDs, figure-regeneration documentation, CI thesis-build workflow, and review/draft status wording.

Items that remain blocked or intentionally documented rather than fabricated:

- `thesis/chapters/00_approval.tex`: the final committee names and examination date must come from the official University of Patras Secretariat record. The repository cannot safely invent these values.
- Canonical native validation full rerun: the source-ZIP smoke preset is reproducible locally, but the full 3,513-case canonical rerun requires the generated `data/pattern_databases/corner_db.pkl` and `RubikOptimal` external oracle together. The docs and failure messages now state both prerequisites explicitly.
- Benchmark strength: the checked-in thesis benchmark remains a legacy single-run corpus with adjacent same-face moves and no confidence intervals. The thesis already limits performance claims to that fixed corpus/platform; a stronger secondary benchmark would require a new experiment run, not a text-only repair.
- Thistlethwaite citation: the bibliography key now reflects the Scherphuis historical summary. A stronger primary source should be added only if a reliable source is actually identified.
