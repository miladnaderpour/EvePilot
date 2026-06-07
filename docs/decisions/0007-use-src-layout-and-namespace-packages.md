# 0007 - Use src layout and namespace packages

## Status

Accepted

## Context

EvePilot is planned as a monorepo with multiple Python apps and internal
packages. Those packages need to share a clean import namespace while avoiding
accidental imports from the repository root during development and testing.

## Decision

EvePilot Python packages will use the `src/` layout and a shared `evepilot`
namespace package.

The top-level `src/evepilot/` directory must not contain `__init__.py`.
Domain packages such as `evepilot.core` and `evepilot.eve_ng` must contain their
own `__init__.py` files.

## Consequences

- Package imports behave more like installed packages during tests.
- Multiple internal packages can contribute modules under the shared
  `evepilot` namespace.
- The top-level namespace stays clean and domain-based.
- Contributors must avoid adding `src/evepilot/__init__.py` in any package.
