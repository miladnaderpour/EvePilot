# Architecture Overview

EvePilot should stay simple at the start while leaving room for future
interfaces and automation engines.

## Major Components

### EvePilot Core

Shared Python logic used by all interfaces. The core owns configuration loading,
shared models, logging, base exceptions, and public result schemas such as
`ServiceResult`.

### EVE-NG Integration

EVE-NG-specific package responsible for authentication, lab node discovery,
console endpoint parsing, and public node discovery service functions.

The low-level API client keeps HTTP details isolated. The service layer returns
public Pydantic schemas that CLI and future API code can serialize.

### Console Discovery

Logic that maps lab nodes to console endpoints. The primary source should be
EVE-NG node metadata returned by the API.

### Bootstrap Service

Public bootstrap use-case layer. It coordinates console preparation, flow
management, and rendered config apply while keeping CLI/API code thin.

Current service functions include:

- Console preparation.
- Built-in flow listing, display, and export.
- Rendered text config apply through a prepared console.

### Flow-Driven Preparation

Preparation flows are YAML definitions that describe console states and actions.
The runner is state-aware and resumable, using flow-defined markers instead of
blind command sending.

### Config Apply

Config apply sends already-rendered text configuration through the console after
preparation reaches a ready state. Rendering Jinja2 templates and resolving
inventory variables remain the responsibility of upstream tools such as Ansible.

The config apply layer is vendor-neutral. Platform-specific error detection is
deferred to future flow/profile-driven error patterns.

### Lab Lifecycle Engine

Planned module for start, stop, wipe, reload, and reset operations.

### Monitoring Collector

Planned module for host health, node status, resource usage, and API health
checks.

### Interfaces

The CLI is the first interface. It wraps results in `ServiceResult` and supports
JSON and text output. Future interfaces may include an API service, web UI,
scheduler, and CI/CD runner integrations.

## Current Shape

```text
CLI / Automation
  |
  v
ServiceResult output boundary
  |
  +--> evepilot.eve_ng.service
  |      |
  |      +--> EveNgClient
  |      +--> EVE-NG API
  |      +--> node and console schemas
  |
  +--> evepilot.bootstrap.service
         |
         +--> preparation flow loader/runner
         +--> console transport
         +--> config apply
         +--> bootstrap schemas
```
