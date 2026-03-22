# Harness Engineering Reference

Source:
- OpenAI, "Harness engineering: leveraging Codex in an agent-first world"
- https://openai.com/index/harness-engineering/

Use this reference to keep the bootstrap aligned with the article's operating model.

## Core Takeaways

### Humans steer, agents execute

The engineer's job shifts from handwriting code to shaping the environment:

- define intent
- build scaffolding
- add feedback loops
- encode missing capability into the repository

### The repository is the system of record

Do not treat `AGENTS.md` as the encyclopedia.

- keep `AGENTS.md` short
- point it at a structured `docs/` tree
- move product, architecture, quality, reliability, security, plans, and references into versioned markdown

The agent can only rely on what is discoverable in-repo.

### Progressive disclosure beats one giant instruction file

The repository should have:

- a short entry point
- a clear docs map
- deeper docs only where needed
- execution plans and debt tracked in-repo

### Strict structure enables speed

The article emphasizes rigid architecture and mechanically-enforced invariants.

For this skill's v1 preset, keep the repo legible with:

- a layered app architecture
- predictable paths
- deterministic commands
- a narrow set of blessed scripts and checks

### Plans are first-class artifacts

Keep active plans, completed plans, and debt together in the repo.
The Ralph loop relies on this.

### Evaluation must be separate from execution

The loop should include:

- deterministic checks
- a separate evaluator pass
- promotion only when the task is substantively complete

### Throughput changes the merge philosophy

The harness article argues for:

- short-lived work
- fast correction
- light blocking
- encoded guardrails instead of heavy manual review

The Ralph loop should therefore optimize for:

- small vertical slices
- deterministic gates
- repeatable operator guidance

### Entropy is real

Agent-generated repositories accumulate drift unless cleanup is explicit.

Bake in:

- quality docs
- reliability/security docs
- task history
- completed plans
- debt tracking

## What This Skill Must Preserve

When bootstrapping a new repo, preserve these article-derived properties:

1. docs first
2. agent-legible repo structure
3. deterministic verification
4. separate evaluator and promotion logic
5. repeatable loop commands
6. explicit cleanup and debt tracking
