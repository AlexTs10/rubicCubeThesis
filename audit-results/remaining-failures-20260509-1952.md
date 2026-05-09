# Remaining Failures - 2026-05-09 19:52

## External / Not Fixed In This Loop

- `thesis/chapters/00_approval.tex`: the official committee names/titles and examination date are still required from the University of Patras process. I did not invent these values.
- `results/benchmarks/thesis/thesis_results_combined.json`: the auditor requested a regenerated exact-depth or no-consecutive-same-face canonical benchmark with richer runtime provenance. That is a larger experimental rerun and was not completed in this short loop. The current Chapter 7 limitation disclosure remains in place.
- `thesis/references.bib`: the Thistlethwaite source remains a clearly labeled secondary historical account. I did not add a fabricated primary source.

## Validation Notes

- `python verify_setup.py` initially exposed a nondeterministic timeout test. I made the test deterministic with a zero-timeout case, then `verify_setup.py` passed.
- Thesis build completed with Tectonic. Remaining TeX messages are underfull/overfull box warnings, not build failures.
