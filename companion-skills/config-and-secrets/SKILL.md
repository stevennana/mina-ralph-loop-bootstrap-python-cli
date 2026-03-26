---
name: config-and-secrets
description: Use when a Python CLI project needs concrete guidance for pydantic-settings, environment-variable contracts, dotenv usage, secret handling, config precedence, or operator-facing settings documentation.
---

# Config And Secrets

Use this skill when configuration policy is becoming part of the product contract.

## Focus

- pydantic-settings model shape
- environment-variable naming and prefixes
- `.env` and `.env.example` policy
- precedence between defaults, env vars, and secrets sources
- documentation for required vs optional config

## Workflow

1. Inspect current settings models, runtime entry points, and documented env vars.
2. Separate committed defaults from operator-provided secrets.
3. Keep naming consistent across code, docs, and deployment units.
4. Make required settings explicit in docs and examples.
5. Add tests when precedence or validation rules are non-trivial.

## Guardrails

- Never commit live secrets, tokens, or private endpoints.
- Do not create multiple overlapping config paths without precedence rules.
- Prefer one settings model or one clear adapter boundary over scattered env lookups.
