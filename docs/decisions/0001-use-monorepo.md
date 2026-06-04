# 0001 - Use a monorepo

## Status

Accepted

## Context

EvePilot is expected to grow beyond a single command-line script. Future
components may include a CLI, API service, web UI, bootstrap engine, monitoring
module, and CI/CD integrations.

## Decision

EvePilot will use a monorepo structure.

## Consequences

- Shared core logic can be reused by multiple interfaces.
- The project can grow without splitting repositories too early.
- Initial structure must stay simple to avoid overengineering.
