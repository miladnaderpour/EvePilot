# Vision

EvePilot is an automation toolkit for EVE-NG labs.

The project exists to help network engineers, NetDevOps practitioners, and
certification candidates automate lab discovery, node orchestration, console
bootstrap, monitoring, and CI/CD-driven network automation workflows.

## Problem

EVE-NG is powerful, but many lab workflows still require manual work:

- Opening node consoles
- Finding console ports
- Starting and stopping nodes
- Applying day-zero configuration
- Rebuilding lab state
- Validating labs
- Integrating labs with CI/CD pipelines

EvePilot aims to reduce this manual work by providing a clean automation layer
around EVE-NG.

## Direction

The first working direction is a vertical slice for lab discovery and console
automation before SSH or management access exists.

Current capabilities include:

- API-based discovery of EVE-NG lab nodes.
- Console endpoint extraction.
- Flow-driven console preparation.
- Rendered text config apply through a prepared console.
- Structured CLI output for automation tools.

Future capabilities may include richer bootstrap workflows, reload-aware
automation, lab lifecycle automation, monitoring, CI/CD integrations, topology
generation, an API service, and a web UI.

## Principles

- Keep core logic clean and testable.
- Treat the EVE-NG API as the primary source of truth.
- Return structured data suitable for automation.
- Keep secrets and local lab details out of public documentation.
- Build small working features before expanding the platform.
