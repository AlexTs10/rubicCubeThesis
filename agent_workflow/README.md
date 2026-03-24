# Thesis Agent Workflow

This workflow turns the repo itself into the working context for thesis maintenance and verification. It is intentionally simple: generate status, generate a chapter packet, revise if needed, then review and validate.

## Files

- `scripts/thesis_workflow.py`: CLI for status reports, chapter packets, and validation.
- `agent_workflow/program.md`: Coordinator instructions for an agent working in this repo.
- `agent_workflow/prompts/researcher.md`: Evidence-gathering prompt.
- `agent_workflow/prompts/writer.md`: Chapter-writing prompt.
- `agent_workflow/prompts/reviewer.md`: Fact/citation/structure review prompt.
- `agent_workflow/generated/`: Generated packets and reports.

## Commands

```bash
# Full repo status
python scripts/thesis_workflow.py status --output agent_workflow/generated/status.md

# Generate packets only for chapters that still look unfinished
python scripts/thesis_workflow.py packets --remaining

# Generate one specific packet
python scripts/thesis_workflow.py packet 07_evaluation

# Lightweight validation
python scripts/thesis_workflow.py validate --output agent_workflow/generated/validation.md
```

## Recommended Loop

1. Run `status` to confirm whether any workflow targets are still open.
2. Run `packets --remaining` only if the status report shows unfinished chapters.
3. Give the agent `agent_workflow/program.md` plus one generated packet.
4. Use `prompts/researcher.md` if the chapter needs evidence extraction first.
5. Use `prompts/writer.md` to revise the chapter if a fix is needed.
6. Use `prompts/reviewer.md` after the draft or revision to catch weak claims, missing citations, or stale numbers.
7. Run `validate` before a full LaTeX build.

## Scope

This workflow is optimized for the current repo state:

- code and benchmark assets already exist
- the manuscript is already in place and builds with Tectonic
- remaining work is limited to verification, polish, and any targeted fixes

It is not a general research framework. It is a focused completion workflow for this thesis.
