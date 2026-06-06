# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for EvePilot.

ADRs document important technical and product decisions that affect the project
shape over time. Each ADR should be short, public-safe, and written in terms of
context, decision, and consequences.

## Decisions

| ADR | Status | Decision |
| --- | --- | --- |
| [0001](0001-use-monorepo.md) | Accepted | Use a monorepo |
| [0002](0002-python-first-core.md) | Accepted | Start with a Python core |
| [0003](0003-eve-ng-api-as-source-of-truth.md) | Accepted | Use the EVE-NG API as the primary source of truth |
| [0004](0004-console-inspection-fallback-only.md) | Accepted | Keep console process inspection as fallback only |
| [0005](0005-cli-first-interface.md) | Accepted | Start CLI first, but do not limit EvePilot to a CLI |
| [0006](0006-provide-installer-scripts-for-services.md) | Accepted | Provide installer scripts for service components |
| [0007](0007-use-src-layout-and-namespace-packages.md) | Accepted | Use src layout and namespace packages |
| [0008](0008-design-bootstrap-as-state-aware-console-automation.md) | Accepted, refined by 0009 | Design bootstrap as state-aware console automation |
| [0009](0009-design-bootstrap-preparation-as-flow-driven.md) | Accepted | Design bootstrap preparation as flow-driven |
| [0010](0010-apply-rendered-text-configs-through-console.md) | Accepted | Apply rendered text configs through console |
