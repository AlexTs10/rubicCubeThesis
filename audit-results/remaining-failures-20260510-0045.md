# Remaining validation and submission blockers

Generated after applying the ChatGPT Pro audit targets saved under
`audit-results/chatgpt-pro-audit-20260510-0000/`.

## Blockers requiring external input or larger follow-up work

1. **Approval and signature front matter**
   - The thesis still needs the official committee names, roles, approval date, and signature-ready details from the university process.
   - This cannot be invented locally without risking an incorrect submission artifact.

2. **Canonical native-exact validation regeneration**
   - The checked-in JSON validation artifacts remain archived evidence.
   - The full canonical native-exact run still depends on companion artifacts outside the source ZIP, especially `corner_db` and the RubikOptimal backend.
   - The source-ZIP preset was validated locally as a smoke/archival check and passed all 261 configured cases.

3. **Statistical benchmark depth**
   - The benchmark evidence remains bounded to the predefined legacy corpus and configured resource limits.
   - A new multi-run benchmark campaign with confidence intervals was not performed in this loop.

4. **Coverage gate level**
   - The CI coverage gate was made explicit at the currently achievable project level.
   - Full local coverage validation passed at 49.46%, but the audit-requested 70% threshold is not yet realistic without broader test investment in evaluation, visualization, pruning, and table-generation modules.

5. **External exact backend archival metadata**
   - Existing artifacts retain reproducibility hashes and environment metadata.
   - A reliable upstream commit/release identifier for the external backend remains unavailable from the local ZIP/PyPI metadata and is still recorded as absent rather than guessed.

## Validation completed

- `git diff --check`: passed
- `python -m pytest tests -q`: `289 passed, 30 deselected`
- `python -m pytest tests -q --cov=src --cov-report=term-missing:skip-covered --cov-fail-under=49`: `289 passed, 30 deselected`, total coverage `49.46%`
- `python -m pytest tests -q -m external`: `1 skipped, 318 deselected`
- `python -m pytest tests -q -m slow`: `2 passed, 314 deselected, 3 xfailed`
- `python -m pytest tests -q -m cache_building`: `23 passed, 1 skipped, 295 deselected`
- `python verify_setup.py`: `7/7 checks passed`
- `python scripts/verification/native_exact_validation.py --preset source-zip --output-dir /tmp/rubic-native-sourcezip-check-0000b`: `261` cases, `0` failures
- `python scripts/thesis_workflow.py validate && python scripts/thesis_workflow.py build --mode auto`: passed, produced `thesis/main.pdf` with TeX layout warnings only
- `cd webapp && npm test && npm run build`: passed
