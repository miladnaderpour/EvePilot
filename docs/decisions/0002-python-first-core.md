# 0002 - Start with a Python core

## Status

Accepted

## Context

The first milestone needs HTTP API access, typed data models, console URL
parsing, JSON output, and tests. Python is a strong fit for network automation
and integrates well with common NetDevOps tools.

## Decision

EvePilot will start with a Python-based core.

## Consequences

- The first implementation can use familiar automation libraries and testing
tools.
- Core logic can later be reused by a CLI, API service, or other interfaces.
- Frontend or service components should not be introduced until the core use
case is working.
