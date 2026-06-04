# 0005 - Start CLI first, but do not limit EvePilot to a CLI

## Status

Accepted

## Context

The first users of EvePilot are likely to run commands from a terminal or CI/CD
pipeline. A CLI is the fastest useful interface for API discovery and JSON
output.

## Decision

EvePilot will start with a CLI interface, but the project should be designed as
an automation toolkit rather than only a command-line tool.

## Consequences

- The CLI can provide the first working user experience.
- Core logic should stay separate from CLI formatting and argument parsing.
- Future API, UI, scheduler, and CI/CD integrations can reuse the same core.
