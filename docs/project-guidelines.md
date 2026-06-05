# EvePilot Project Guidelines

This document records the initial architectural and development guidelines for
EvePilot.

EvePilot is an automation toolkit for EVE-NG environments. It is not only a CLI
tool. The CLI is the first interface, but the project is designed to grow into a
broader automation platform with an API service, web UI, monitoring, lab
lifecycle automation, and CI/CD integrations.

## Repository Model

EvePilot will use a monorepo structure.

The repository may grow toward this shape as implementation begins:

```text
EvePilot/
|-- apps/
|-- packages/
|-- scripts/
|-- docs/
|-- examples/
|-- infra/
|-- tests/
|-- README.md
`-- pyproject.toml
```

Planned responsibilities:

- `apps/` contains runnable applications.
- `packages/` contains reusable internal packages.
- `scripts/` contains installation, upgrade, and operational scripts.
- `docs/` contains public documentation, architecture, decisions, and research.
- `examples/` contains sample integrations.
- `infra/` contains future deployment, Docker, Terraform, and CI/CD assets.
- `tests/` contains shared and integration tests.

Do not create empty top-level directories before the project has real files for
them. Keep the repository honest about what exists today.

## Applications

Runnable applications should live under `apps/`.

Planned applications:

```text
apps/
|-- cli/
|-- api/
`-- web/
```

The CLI is the first application, but EvePilot should not be described as only a
CLI tool.

## Internal Packages

Reusable logic should live under `packages/`.

Planned packages:

```text
packages/
|-- evepilot-core/
|-- evepilot-eve-ng/
|-- evepilot-bootstrap/
`-- evepilot-monitoring/
```

Package responsibilities:

- `evepilot-core` contains shared models, exceptions, configuration helpers, and
  common utilities.
- `evepilot-eve-ng` contains the EVE-NG API client, lab discovery, node
  discovery, and console endpoint parsing.
- `evepilot-bootstrap` contains the future console bootstrap engine for day-zero
  device onboarding.
- `evepilot-monitoring` contains future EVE-NG host and node monitoring logic.

## Python Layout

Each Python app or package should use the `src/` layout.

Example:

```text
packages/evepilot-eve-ng/
|-- pyproject.toml
`-- src/
    `-- evepilot/
        `-- eve_ng/
            |-- __init__.py
            |-- client.py
            |-- models.py
            `-- console.py
```

The `src/` layout prevents accidental local imports and makes packaging and
testing more reliable.

## Python Namespace

Use one shared Python namespace:

```text
evepilot
```

Domain modules should live under this namespace:

```text
evepilot.core
evepilot.eve_ng
evepilot.bootstrap
evepilot.monitoring
```

Preferred imports:

```python
from evepilot.eve_ng.client import EveNgClient
from evepilot.core.exceptions import EvePilotError
```

Avoid unrelated top-level import package names such as:

```text
evepilot_core
evepilot_eve_ng
evepilot_model
evepilot_schema
```

Installable package names may differ from import package names, but the import
namespace should stay clean and domain-based.

## `__init__.py` Rule

Because `evepilot` is a shared namespace, do not put `__init__.py` directly
inside:

```text
src/evepilot/
```

Correct:

```text
src/evepilot/core/__init__.py
src/evepilot/eve_ng/__init__.py
```

Incorrect:

```text
src/evepilot/__init__.py
```

The top-level `evepilot` directory must remain a namespace package.

## Exception Boundaries

`EvePilotError` is the global parent exception. It lives in
`evepilot.core.exceptions` so every package can share one common catch point.

Each package or domain must define its own domain-specific errors instead of
adding every error type to `evepilot.core.exceptions`.

Example:

```text
evepilot.core.exceptions
`-- EvePilotError

evepilot.eve_ng.errors
|-- EveNgError
|-- EveNgApiError
|-- EveNgAuthError
|-- EveNgNotFoundError
`-- EveNgConsoleError
```

CLI and API layers may catch `EvePilotError` globally, while package internals
should raise their own domain-specific error classes.

Domain `errors.py` files are the source of truth for domain error classes,
stable error codes, messages, and error factory helpers.

Example:

```python
def node_not_found_error(*, lab_path: str, node_name: str) -> EveNgNotFoundError:
    return EveNgNotFoundError(
        code="eve_ng.node_not_found",
        message="EVE-NG node was not found.",
        details={"lab_path": lab_path, "node_name": node_name},
        status_code=404,
    )
```

Callers should prefer these helpers instead of constructing domain errors
inline.

## Configuration

EvePilot uses `pydantic-settings` for runtime configuration.

Environment variables must use the `EVEPILOT_` prefix and must be
case-sensitive.

Example:

```text
EVEPILOT_EVE_NG_URL=http://10.1.2.3
EVEPILOT_EVE_NG_USERNAME=admin
EVEPILOT_EVE_NG_PASSWORD=eve
EVEPILOT_EVE_NG_VERIFY_SSL=false
```

## Logging Configuration

EvePilot logging must support simple and advanced configuration modes.

Simple mode uses:

```text
EVEPILOT_LOG_OUTPUT
EVEPILOT_LOG_LEVEL
EVEPILOT_LOG_FORMAT
EVEPILOT_LOG_FILE_PATH
```

Advanced mode uses:

```text
EVEPILOT_LOG_TARGETS_JSON
```

If `EVEPILOT_LOG_TARGETS_JSON` is set, it overrides the simple logging settings
and defines multiple logging targets.

For Milestone 0.1.0, supported outputs are:

- `stdout`
- `file`

Supported formats are:

- `json`
- `text`

The public logging API must remain:

```python
setup_logging(settings)
get_logger(name)
```

Application code must not know whether logs go to stdout, file, Redis, or
another backend.

In `setup_logging(settings)`, build targets like this: if `log_targets_json`
exists, parse it; otherwise, create one default target from the simple
variables.

## Log File Path

The default log file path is `logs/evepilot.log` for local development.

Installed Linux services should use `/var/log/evepilot/evepilot.log`,
configured by the installer script through `/etc/evepilot/evepilot.env`.

The code must not require root permissions during local development.

Multiple log files should be supported through advanced logging targets, not
through many hardcoded config keys.

## Logging Timestamp Timezone

EvePilot logs must use UTC timestamps by default.

Milestone 0.1.0 does not expose timezone configuration. This keeps log output
consistent for OpenSearch, Docker, systemd, CI/CD, and future distributed
components.

The logging implementation may be designed internally so timezone support can be
added later, but the public configuration should stay simple for now.

## Dataclass and Model Naming

EvePilot uses dataclasses for internal domain and runtime models, and Pydantic
models for configuration and future API boundaries.

### Dataclasses

Internal dataclasses should use clear domain names without unnecessary suffixes.

Good:

```text
ConsoleEndpoint
LogTarget
EveNgNode
NodeDiscoveryResult
```

Avoid:

```text
ConsoleEndpointData
LogTargetModel
EveNgNodeDTO
```

Dataclasses should normally use:

```python
@dataclass(frozen=True, slots=True)
```

Use mutable dataclasses only when mutation is intentional.

### Pydantic Settings

Runtime configuration should use Pydantic settings classes.

Current primary settings class:

```text
Settings
```

Future grouped settings may use names such as:

```text
LoggingSettings
EveNgSettings
```

### API Schemas

Future API request and response schemas should use:

```text
In  = request/input schema
Out = response/output schema
```

Examples:

```text
BootstrapRequestIn
NodeConsoleOut
LabNodesOut
```

### External Payloads

Typed models representing raw external API responses should use the `Payload`
suffix.

Examples:

```text
EveNgNodePayload
EveNgLabPayload
```

### Results and Commands

Operation result objects should use the `Result` suffix.

Examples:

```text
NodeDiscoveryResult
ConsoleParseResult
```

Command/request objects for internal workflows should use the `Command` suffix.

Examples:

```text
DiscoverNodeCommand
BootstrapNodeCommand
```

### For Milestone 0.1.0

Use only these now:

```text
ConsoleEndpoint
LogTarget
EveNgNode
Settings
EvePilotError
EveNgError
```

## Bootstrap Design

`evepilot-bootstrap` must be designed as a state-aware console automation
package.

Do not implement bootstrap as a blind command sender.

The bootstrap package must separate:

- Console transport
- Console state detection
- Console preparation
- Future workflow execution

Milestone 0.2.0 should implement only console connection, state detection, and
preparation.

Future reload workflows must be supported by extending the same primitives, not
by rewriting them.

## Service Installer Scripts

Service components should be installable through provided scripts. Users should
not be required to manually create systemd unit files for normal installation.

Planned scripts:

```text
scripts/
|-- install-api-service.sh
|-- upgrade-api-service.sh
`-- uninstall-api-service.sh
```

The intended API service installation flow is:

```bash
git clone https://github.com/milad-naderpour/evepilot.git
cd evepilot
sudo ./scripts/install-api-service.sh
```

The installer should handle:

- Creating the `evepilot` Linux service user.
- Creating required directories.
- Creating a Python virtual environment.
- Installing internal packages.
- Creating `/etc/evepilot/evepilot.env` if it is missing.
- Generating the systemd service file.
- Reloading systemd.
- Enabling and starting the service.
- Printing status and next steps.

Manual systemd instructions may exist as fallback or reference documentation,
but installer scripts should be the primary product-level installation path.
