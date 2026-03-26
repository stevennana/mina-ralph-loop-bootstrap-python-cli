# ARCHITECTURE.md

## Goal
Build {{PROJECT_NAME}} as an agent-legible codebase with strong boundaries, a short instruction surface, and enough extension seams to support future change without overbuilding v1.

## System Overview
{{PROJECT_NAME}} is a Python CLI and worker application with:
{{SYSTEM_OVERVIEW_BULLETS}}

## Architectural Priorities
{{ARCHITECTURAL_PRIORITIES_BULLETS}}

## Layered Domain Model
Use a strict forward-only dependency shape inside each domain:

`Types -> Config -> Ports -> Services -> Adapters -> CLI/Worker`

## Primary Domains
{{PRIMARY_DOMAINS_MARKDOWN}}

## CLI / Worker Shape
### CLI
{{CLI_SHAPE_BULLETS}}

### Worker
{{WORKER_SHAPE_BULLETS}}

## Persistence Strategy
{{PERSISTENCE_STRATEGY_BULLETS}}

## Verification Shape
{{VERIFICATION_SHAPE_BULLETS}}
