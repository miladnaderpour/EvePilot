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
