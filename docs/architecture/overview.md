# Architecture Overview

EvePilot should stay simple at the start while leaving room for future
interfaces and automation engines.

## Major Components

### EvePilot Core

Shared Python logic used by all interfaces. The core owns configuration loading,
typed models, console URL parsing, and reusable orchestration helpers.

### EVE-NG API Client

HTTP client responsible for authentication and EVE-NG API calls. It should keep
API transport details separate from CLI output and higher-level workflows.

### Console Discovery

Logic that maps lab nodes to console endpoints. The primary source should be
EVE-NG node metadata returned by the API.

### Bootstrap Engine

Planned module for day-zero device onboarding over console. This should be added
after API-based discovery is working.

### Lab Lifecycle Engine

Planned module for start, stop, wipe, reload, and reset operations.

### Monitoring Collector

Planned module for host health, node status, resource usage, and API health
checks.

### Interfaces

The CLI is the first interface. Future interfaces may include an API service,
web UI, scheduler, and CI/CD runner integrations.

## Initial Shape

```text
+------------------+
| CLI / Automation |
+--------+---------+
         |
         v
+------------------+
| EvePilot Core    |
+--------+---------+
         |
         v
+------------------+
| EVE-NG API Client|
+--------+---------+
         |
         v
+------------------+
| EVE-NG API       |
+--------+---------+
         |
         v
+------------------+
| Lab Nodes        |
| Console / SSH    |
+------------------+
```
