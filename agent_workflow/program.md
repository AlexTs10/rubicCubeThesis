# Thesis Completion Program

Use this repo as the single source of truth for finishing the thesis.

## Objective

Finish the thesis incrementally without inventing claims, citations, benchmark numbers, or architecture details.

## First Move

1. Run `python scripts/thesis_workflow.py status --output agent_workflow/generated/status.md`.
2. If the target chapter does not already have a packet, run `python scripts/thesis_workflow.py packet <chapter_key>`.
3. Read the generated packet, the current chapter file, and the listed supporting files before editing anything.

## Working Rules

- Edit only the target chapter unless the task explicitly requires `thesis/references.bib` or another listed file.
- Keep the thesis language and formatting consistent with the surrounding LaTeX chapters.
- Use only benchmark numbers that are present in `results/benchmarks/thesis/thesis_bench_d*.json` or directly summarized in a generated packet.
- Prefer local papers already stored in `papers/` over new web research.
- If a claim is not supported by local evidence, either qualify it clearly or omit it.
- Do not rewrite finished chapters just because you can. Focus on missing sections, weak sections, and factual cleanup.

## Workflow

1. Research
   Read the packet, extract the needed evidence, and note what can be stated safely.
2. Draft
   Write or expand the target chapter with concrete references to code, data, figures, and citations.
3. Review
   Check that every strong claim is traceable to a cited source, a local benchmark, or a code artifact.
4. Validate
   Run `python scripts/thesis_workflow.py validate` before asking for final compilation.

## Completion Criteria

- The target chapter is no longer a stub.
- Citations used in the chapter exist in `thesis/references.bib`.
- Figures and tables referenced in the chapter exist locally.
- The chapter meaningfully advances the thesis rather than restating the spec.
