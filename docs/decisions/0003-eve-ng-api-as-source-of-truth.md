# 0003 - Use the EVE-NG API as the primary source of truth

## Status

Accepted

## Context

The first EvePilot milestone is lab node discovery and console endpoint
extraction. EVE-NG already exposes lab and node metadata through its API.

## Decision

EvePilot will treat the EVE-NG API as the primary source of truth for labs,
nodes, status, and console endpoint metadata.

## Consequences

- Discovery logic stays aligned with EVE-NG's own view of the lab.
- The implementation avoids hardcoded console ports.
- Lower-level host inspection should be reserved for fallback or debugging.
