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

The first priority is API-based discovery of labs, nodes, and console endpoints.
This gives automation tools a reliable way to find devices before SSH or
management access exists.

Future capabilities may include console bootstrap, lab lifecycle automation,
monitoring, CI/CD integrations, topology generation, and a web UI.

## Principles

- Keep core logic clean and testable.
- Treat the EVE-NG API as the primary source of truth.
- Return structured data suitable for automation.
- Keep secrets and local lab details out of public documentation.
- Build small working features before expanding the platform.
