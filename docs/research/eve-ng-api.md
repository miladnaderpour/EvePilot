# EVE-NG API Research

This document tracks public-safe notes about EVE-NG API behavior relevant to
EvePilot.

## Initial Discovery Targets

- Authenticate to the EVE-NG API.
- List labs.
- Query nodes from a specific lab.
- Read node metadata such as ID, name, status, type, console protocol, and URL.
- Parse console URLs into host and port fields.

## Expected API Areas

```text
POST /api/auth/login
GET /api/labs
GET /api/labs/{lab_path}/nodes
```

Exact request and response details should be verified against a real lab before
implementation.

## Node Metadata To Capture

- `id`
- `name`
- `status`
- `type`
- `console`
- `url`

## Open Questions

- How lab paths should be encoded for nested folders.
- Whether Community and Professional editions return identical node fields.
- How EVE-NG represents stopped nodes without active console endpoints.
- Whether API sessions use cookies, tokens, or both in the target versions.
