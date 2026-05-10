# Rubik's Cube Thesis Webapp

This Next.js app is a synthetic frontend preview for demos only. It does not run
the repository's Python solvers and is excluded from benchmark evidence, solver
correctness claims, and optimality claims.

Use the thesis PDF, `results/benchmarks/thesis/`, and the Python evaluation
pipeline as the authoritative sources for technical claims.

## Supported Toolchain

The supported local toolchain is the Node/npm pair pinned by the repository:
Node 24.9.x from the root `.nvmrc` and npm 11.6.x from `packageManager`. The
`engine-strict=true` setting in `.npmrc` is intentional so reviewers do not
accidentally build the preview app under an older system Node release.

For a host-independent check, run the Docker path from the repository root:

```bash
docker build -f docker/webapp.Dockerfile -t rubic-cube-thesis-webapp .
docker run --rm rubic-cube-thesis-webapp
```
