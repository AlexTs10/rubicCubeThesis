# Remaining non-local audit blockers from ChatGPT Pro audit 20260510-1947

The audit saved under `audit-results/chatgpt-pro-audit-20260510-1947/` reported
14 targets. The following items are not safe to resolve locally without external
institutional data, heavyweight experiment reruns, or third-party artifacts.

- Critical approval/signature blocker: `thesis/chapters/00_approval.tex` still needs the official remaining committee names/titles and examination date from the University of Patras.
- Coverage threshold target: raising the CI gate to 60% requires a broader test campaign across evaluation/statistics/visualization modules. The current gate stays conservative until those tests exist.
- Canonical native-exact artifact: full 3,513-case reproduction requires `data/pattern_databases/corner_db.pkl` and the optional external exact oracle as a companion artifact.
- Benchmark-strength targets: repeated runs, confidence intervals, cold/warm timing separation, and regenerated non-redundant benchmark corpus require a new benchmark campaign.
- External exact backend provenance: upstream commit/tag or source archive hash for `RubikOptimal` is not recoverable from the installed wheel metadata alone.
- Citation archival hardening: replacing mutable web/GitHub references with DOI/ISBN/archive-hash-backed references requires bibliography research outside the source package.
- PDF accessibility tagging: `hyperxmp` now provides an embedded metadata stream, but full tagged PDF output remains dependent on an institutional accessible-PDF workflow.
