# Remaining Failures After ChatGPT Pro Audit Fix Pass

Source audit: `audit-results/chatgpt-pro-audit-20260509-1132/`

## Not Fixed In This Pass

- Formal institutional front matter is still blocked on official committee names, signatures, and examination date. I did not fabricate institutional data.
- Canonical native exact validation still requires the omitted/generated `data/pattern_databases/corner_db.pkl` artifact. The source-ZIP smoke path remains the portable validation path.
- Full benchmark reruns with repeated trials, equal timeout sensitivity, randomized order, cold/warm separation, and isolated peak RSS were not run in this pass. The thesis wording was tightened instead of over-claiming the existing evidence.
- Python dependency locking is still version-pinned rather than hash-locked and platform-complete.
- External optimal backend provenance still lacks an original benchmark-time wheel hash or upstream commit hash.
- `npm audit --audit-level=moderate` still reports the PostCSS advisory through `next`; npm's suggested `--force` fix would downgrade Next to an incompatible old major version, so it was not applied.

## Local Validation Notes

- `python -m pytest tests -q` passed.
- `python verify_setup.py --notebooks --all-artifacts` passed.
- `python scripts/thesis_workflow.py validate` and `build --mode auto` passed via Tectonic in this environment.
- `cd webapp && npm ci && npm test && npm run lint && npm run build` passed under Node 24.9.0 and npm 11.6.0 with `engine-strict=true`.
