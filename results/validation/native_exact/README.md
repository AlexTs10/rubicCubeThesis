# Native Exact Validation Reports

This directory contains time-stamped validation outputs for the native exact solver path.

## Canonical Thesis Reports

The thesis claims about the native exact solver and the full native corner pattern database are based on the reports identified in `MANIFEST.json` in this directory.

The reproducible command for the thesis corpus is:

```bash
python scripts/verification/native_exact_validation.py --preset canonical --output-dir results/validation/native_exact
```

The `canonical` preset expands to the exact corpus recipe used for the thesis claim:

- exhaustive depth `3`
- oracle depths `4 5 6 7 8 9`
- `2` samples per oracle depth
- max depth `12`
- timeout `20.0 s`
- seed `42`
- native corner database enabled

This canonical command is not fully reproducible from the source ZIP alone,
because the source ZIP intentionally omits the generated full
`data/pattern_databases/corner_db.pkl` cache. From a source-only ZIP, use
`--preset source-zip` as an executable smoke check of the validation path. The
canonical preset should fail with a prerequisite message unless the full corner
cache has been generated or supplied as a separate artifact.

New reports written by the script preserve the corpus recipe in `config.corpus_generation`, so the exact corpus can be reconstructed from the JSON alone.

The key comparison pair is:

- `native_exact_validation_20260322_144046.json`
  - corner PDB enabled
  - `3513` total cases
  - `1` failure under a `20.0 s` timeout
- `native_exact_validation_20260322_144158.json`
  - corner PDB disabled
  - `3513` total cases
  - `3` failures under the same `20.0 s` timeout

The two reports use the same validation corpus and differ only in whether the full native corner PDB is active.

## Supplemental Reports

- `native_exact_validation_20260322_130107.json`
  - earlier `3509`-case validation run with `0` failures
- `native_exact_validation_20260322_130141.json`
  - sampled depth-8 follow-up with `0` failures
- `native_exact_validation_20260322_130238.json`
  - sampled failure-boundary run showing `2` depth-9 native timeouts under `20.0 s`

These reports remain useful for chronology and exploratory validation, but the thesis comparison about the corner PDB improvement should cite the canonical pair above.

## Reproducibility Notes

- The checked-in JSON artifacts are preserved as canonical evidence.
- If you regenerate the reports with the canonical preset, the output schema includes `config.corpus_generation` with the full corpus recipe.
- The bare script invocation now defaults to the canonical thesis preset.
- Source-ZIP reviewers should expect `--preset source-zip` to pass without large
  generated caches and `--preset canonical` to require `corner_db.pkl`.

## Legacy Reports

Older files from the same day predate the richer output schema and do not include a `config` block. They are preserved as historical exploratory artifacts and are not the preferred citation targets for the final thesis text.
