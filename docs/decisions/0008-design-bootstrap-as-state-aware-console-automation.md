# 0008 - Design bootstrap as state-aware console automation

## Status

Accepted

## Context

EvePilot will eventually support day-zero bootstrap over EVE-NG console
connections. Some router workflows are simple command pushes, but others require
state awareness, confirmation prompts, reloads, reconnects, and post-reload
continuation.

Examples include initial configuration dialogs, "Press RETURN" prompts, ROMMON,
login/password prompts, privileged EXEC prompts, and future reload workflows
such as controller-mode changes.

## Decision

`evepilot-bootstrap` will be designed as a state-aware console automation
package, not as a blind command sender.

The bootstrap package must separate:

- Console transport
- Console state detection
- Console preparation
- Future workflow execution

Milestone 0.2.0 will implement only console connection, state detection, and
safe preparation. It will not implement a full workflow runner, YAML workflow
engine, reload watcher, templates, or config-file bootstrap.

## Consequences

- Console automation can make decisions based on observed device state.
- Future reload-aware and multi-stage workflows can reuse the same primitives.
- The first bootstrap milestone stays small and testable.
- Blind command-file pushing is deferred until the console/session foundation is
  stable.
- Workflow and template code should not be added until a later milestone needs
  it.
