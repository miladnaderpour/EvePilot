# 0011 - Use shared service result schemas

## Status

Accepted

## Context

EvePilot has a CLI today and is expected to grow an API service later. Both
interfaces should return a consistent first-layer result shape, but the shared
core should not become tied to FastAPI, HTTP request objects, tenant metadata,
or API-only concerns.

Domain packages also need room to keep their own focused internal dataclasses
and public service schemas without forcing every model into one global file.

## Decision

EvePilot will define shared service result schemas in `evepilot.core`.

The shared schemas are:

- `ServiceResult`
- `ServiceError`
- `ServiceMeta`

These schemas define the outer result shape for CLI and future API responses.
They are Pydantic models because they sit at the interface boundary and must be
easy to serialize.

Domain service functions may return Pydantic schemas for their public results.
CLI and API layers wrap those schemas in `ServiceResult` at the outer interface
layer.

The core package must not include FastAPI request-specific builders. API-only
metadata such as route templates, tenant IDs, actor IDs, or HMAC fingerprints is
deferred until a real API service needs it.

## Boundary Rules

### Interface result boundary

Anything returned from a package service function to CLI or API code must be a
Pydantic schema, not a raw dictionary.

Use this model boundary:

- Internal engine objects are dataclasses.
- Public service return objects are Pydantic schemas.
- CLI/API output is serialized from Pydantic schemas.

For example, `ConfigApplyResult` may stay as an internal dataclass in
`evepilot.bootstrap.config_apply`, but
`evepilot.bootstrap.service.apply_rendered_config()` should return a public
Pydantic schema from `evepilot.bootstrap.schemas`.

### Dependency wiring boundary

CLI and API layers may create dependencies from settings, CLI options, request
state, or database sessions. They must not contain package workflow logic.

CLI/API responsibilities:

- Parse input.
- Load settings.
- Create dependencies such as `EveNgClient` or future database sessions.
- Call package service functions.
- Serialize output.

Package service responsibilities:

- Receive explicit dependencies.
- Orchestrate the domain workflow.
- Return public Pydantic schemas.
- Avoid reading `.env`, CLI flags, or framework request objects directly.

For now, passing an `EveNgClient` into bootstrap service functions is acceptable.
Later, service functions may accept protocols such as a node console resolver if
that boundary becomes useful.

### Model and error placement

Public package service APIs and subdomain internals should stay separated.

Bootstrap package-level public modules:

- `evepilot.bootstrap.service` for public use-case functions.
- `evepilot.bootstrap.schemas` for public Pydantic service result schemas.
- `evepilot.bootstrap.errors` as the bootstrap package error source of truth.

Bootstrap subdomain internals:

- `evepilot.bootstrap.preparation.models` for internal preparation dataclasses.
- `evepilot.bootstrap.config_apply.models` for internal config apply
  dataclasses.

This keeps CLI/API contracts stable without forcing all internal models into one
large global model file.

### Schema file organization

The core package may keep shared cross-cutting schemas in one file:

- `evepilot.core.schemas`

Domain packages should use a `schemas/` package when they grow beyond one small
schema group. Related schemas should be grouped by use case or resource.

Example:

```text
evepilot.bootstrap.schemas/
├── __init__.py
├── config_apply.py
├── preparation.py
└── workflow.py
```

Use `Result` for public package service return schemas, such as
`BootstrapConfigApplyResult`.

Use `In` and `Out` only for future API request/response boundary schemas, such
as `BootstrapConfigApplyIn` or `BootstrapConfigApplyOut`.

## Consequences

- CLI and future API responses can share a consistent top-level shape.
- Domain internals can continue using dataclasses where they are simpler.
- API-specific metadata does not leak into core too early.
- Future API code can add request-aware builders without changing the shared
  schema contract.
- CLI/API layers stay thin while package services own reusable workflow logic.
