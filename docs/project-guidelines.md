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

## CLI Command Model

EvePilot CLI commands should use a resource-first structure:

```text
evepilot <resource> <action>
```

Examples:

```text
evepilot nodes all --lab EIGRP/Basics.unl
evepilot nodes get --lab EIGRP/Basics.unl --node CSR-1
evepilot topology get --lab EIGRP/Basics.unl
evepilot bootstrap prepare --lab EIGRP/Basics.unl --node CSR-1
```

Prefer product resources such as `nodes`, `topology`, and `bootstrap` over
provider-first commands such as `eve-ng get-nodes`. EVE-NG is the first
provider, but the CLI should leave room for future providers such as CML, GNS3,
or containerlab.

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

`evepilot-bootstrap` must be designed as a state-aware, flow-driven console
automation package.

Do not implement bootstrap as a blind command sender.

The bootstrap package must separate:

- Console transport
- Flow-defined console state matching
- Console preparation
- Future workflow execution

Console transport belongs under `evepilot.bootstrap.transport`.

Flow-driven console preparation belongs under `evepilot.bootstrap.preparation`.

The root `evepilot.bootstrap` package should remain a public facade for common
imports and future high-level bootstrap orchestration.

Bootstrap preparation must be driven by explicit user-provided or built-in
flows. Built-in flows may be shipped for common router images, but they are
defaults and examples, not the only supported behavior.

Built-in flows must be discovered from package resources. Do not maintain a
manual hardcoded built-in flow registry in Python code. Each built-in flow's
file name stem is its public `built-in:<name>` reference. The YAML `name` field
must match the file name stem.

Custom user flows must be loaded from file paths, usually under a local
`flows/` directory. Users should not add custom flows to the built-in package
resource directory.

For Milestone 0.2.0, custom flows use explicit file paths. Later, EvePilot may
support local flow-name resolution with this order:

1. `built-in:<name>`
2. Explicit existing file path
3. `./flows/<name>`
4. Error

This would allow `--flow my-router-flow.yaml` to resolve to
`./flows/my-router-flow.yaml` without changing built-in flow resolution.

Users should be able to inspect available built-in flows before running them.
The CLI should support:

```text
evepilot bootstrap flow list
evepilot bootstrap flow show built-in:cisco-router-first-boot
evepilot bootstrap flow export built-in:cisco-router-first-boot --output flows/cisco-router-first-boot.yaml
```

Flow export should preserve the original YAML text instead of regenerating YAML
from dataclasses.

Bootstrap flows must be resumable.

Startup handling must wake a silent console before state matching. The runner
should perform an initial read, send Enter for a small configured number of wake
attempts when no output is received, and fail with a flow-run error if the
console remains silent.

Console output is stream-based. The flow runner must not assume that one read is
one complete decision. It must buffer console chunks across reads, detect state
from recent buffered output, and retry until a flow-defined state is found or a
detection timeout is reached.

The matcher must evaluate recent buffered output, not only individual lines.
Many router prompts do not end with a newline, and async reads may split prompts
across multiple chunks.

Users must be able to override the console state detection timeout from the CLI.
For bootstrap preparation, `--timeout` and `--detect-console-timeout` should set
the same runtime value.

### Async Console Transport

`evepilot-bootstrap` must use an async console transport abstraction.

The flow runner must depend on an `AsyncConsoleSession` protocol, not directly
on Telnet or any other transport implementation.

The console protocol should expose:

```python
class AsyncConsoleSession(Protocol):
    async def connect(self) -> None: ...
    async def read(self, timeout_seconds: float) -> str: ...
    async def send(self, text: str) -> None: ...
    async def close(self) -> None: ...
```

The flow runner should use:

```python
async def run_flow(
    flow: FlowDefinition,
    session: AsyncConsoleSession,
) -> FlowRunResult:
    ...
```

Milestone 0.2.0 should implement:

- `AsyncConsoleSession`
- `TelnetConsoleSession`
- `RawTcpConsoleSession`
- Async `run_flow()`

`TelnetConsoleSession` should use `telnetlib3`.

`RawTcpConsoleSession` should use plain TCP without Telnet negotiation. It is
needed for EVE-NG node types that expose console ports as raw serial streams,
such as Dynamips.

The CLI should support `--transport auto`, `--transport telnet`, and
`--transport raw-tcp`. Automatic transport selection should use raw TCP for
Dynamips nodes and Telnet for other node types unless a user explicitly
overrides the transport.

Future transports, such as SSH-port-forwarded console access, must be added by
implementing the same session protocol instead of changing the flow runner.

SSH forwarding is not part of Milestone 0.2.0.

A flow file must define state markers using plain string patterns and/or regex
patterns. EvePilot must use these flow-defined markers to detect the current
console state before executing a step.

Matcher debug logs should record detection start, plain or regex matches,
no-match diagnostics, ambiguous matches, and the final selected state. Secret
values must never be logged.

The flow runner must not blindly start from the first step every time. It should
detect the current state, find the matching step for that state, execute it, then
follow the step's `next` rule when one is explicitly defined.

This allows EvePilot to continue correctly even if the user manually answered an
earlier prompt before running the flow.

Supported `next` values for Milestone 0.2.0:

- `detect`: read console output again, detect state, and execute the matching
  step. This is useful when a flow author wants the detect behavior to be
  explicit.
- `stop`: stop the flow.
- `step:<step-name>`: jump to a specific named step.

`skip_when_state` may be added later, but for Milestone 0.2.0 the preferred
design is state-driven matching through `when_state`.

Omitting `next` means the runner should detect the current state again after the
step completes. The `ready` action is terminal and must not define `next`.

Flow instructions should describe concrete actions such as:

- `wait`
- `send`
- `send_if_no_output`
- `expect`
- `expect_send`
- `ready`

Actions such as `reload_wait`, `branch`, `loop`, `render_template`,
`set_variable`, and config push are intentionally deferred to later milestones.

Flow variables should resolve from environment variables with the
`EVEPILOT_BOOTSTRAP_` prefix:

```text
<flow-variable-name> -> EVEPILOT_BOOTSTRAP_<FLOW_VARIABLE_NAME_UPPER>
```

Example:

```text
enable_secret -> EVEPILOT_BOOTSTRAP_ENABLE_SECRET
```

Secret variable values must not be logged.

Initial flow models should be shaped around:

- `FlowStateMarker`: how to recognize a named state.
- `FlowStep`: what to do when that state is detected.
- `next`: how the runner should continue after a step executes.

`FlowStep.optional` is reserved in Milestone 0.2.0. Flows may parse it, but the
runner must not rely on optional-step behavior until it is implemented and
tested.

`FlowRunResult.output_sample` currently stores the latest output returned by the
console. A later milestone should cap this value to a bounded sample before
larger command output or config push workflows are added.

Milestone 0.2.0 should focus on console connection, flow models/loading, a small
flow runner, and safe preparation. It should not implement full config push,
reload watchers, templates, or a YAML workflow engine beyond the small
preparation-flow shape needed now.

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
