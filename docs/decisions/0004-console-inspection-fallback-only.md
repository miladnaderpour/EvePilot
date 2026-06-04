# 0004 - Keep console process inspection as fallback only

## Status

Accepted

## Context

Console endpoints may sometimes be discoverable through Linux process and socket
inspection on the EVE-NG host. That approach can be useful for debugging, but it
is more fragile than API-based discovery.

## Decision

EvePilot will keep console and process inspection as a fallback or diagnostic
approach only.

## Consequences

- Normal workflows remain API-driven.
- The project avoids depending on EVE-NG host internals when the API is enough.
- Fallback discovery can still be documented and explored for troubleshooting.
