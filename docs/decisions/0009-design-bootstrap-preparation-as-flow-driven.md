# 0009 - Design bootstrap preparation as flow-driven

## Status

Accepted

## Context

Generic console state detection is useful for diagnostics and validation, but it
is not enough to safely prepare every router image.

Different images, versions, and lab states may show different prompts depending
on first boot, existing startup configuration, controller mode, license mode,
failed setup, ROMMON state, or configured login credentials.

EvePilot should not hardcode all router behavior in Python. Users must be able
to define exact preparation flows for their own images and labs. EvePilot may
also ship default built-in flows for common images.

## Decision

Bootstrap preparation must be flow-driven.

EvePilot must support user-provided bootstrap preparation flows. Built-in flows
may be shipped for common router images, but they are defaults and examples, not
the only supported behavior.

Built-in flows must be discovered from packaged YAML resources. The YAML file
name stem is the public built-in flow reference, for example
`built-in:cisco-router-first-boot`. The YAML `name` field must match the file
name stem.

Custom user flows must be loaded from file paths and should not be added to the
built-in package resource directory.

For Milestone 0.2.0, custom flows are loaded from explicit file paths. A later
milestone may add user-friendly flow name resolution.

Future flow resolution should use this order:

1. `built-in:<name>`
2. Explicit existing file path
3. `./flows/<name>`
4. Error

This would allow users to pass `--flow my-router-flow.yaml` after placing the
file in a local `flows/` directory, without changing the built-in flow behavior.

Users should be able to inspect available built-in flows before running them.
The CLI should support:

```text
evepilot bootstrap flow list
evepilot bootstrap flow show built-in:cisco-router-first-boot
evepilot bootstrap flow export built-in:cisco-router-first-boot --output flows/cisco-router-first-boot.yaml
```

Flow export should preserve the original YAML text instead of regenerating YAML
from dataclasses.

Startup handling must wake a silent console before state matching. The runner
should perform an initial read, send Enter for a small configured number of wake
attempts when no output is received, and fail with a flow-run error if the
console remains silent.

Console output must be treated as a stream. The runner must not treat one read
as one complete decision. It should buffer console chunks across reads, detect
state from recent buffered output, and continue reading until a flow-defined
state is found or a detection timeout is reached.

State matching should run against recent buffered output instead of individual
lines only. Router prompts such as `Password:`, `Router>`, and `Router#` may not
end with a newline, and async console reads may split a prompt across multiple
chunks.

Users must be able to override the console state detection timeout from the CLI.
For bootstrap preparation, `--timeout` and `--detect-console-timeout` should set
the same runtime value.

## Async Console Transport

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

`RawTcpConsoleSession` should use plain TCP without Telnet negotiation. This is
needed for EVE-NG node types that expose console ports as raw serial streams,
such as Dynamips. The CLI should support these transport options:

- `--transport auto`
- `--transport telnet`
- `--transport raw-tcp`

Automatic transport selection should use raw TCP for Dynamips nodes and Telnet
for other node types unless a user explicitly overrides the transport.

Future transports, such as SSH-port-forwarded console access, must be added by
implementing the same session protocol instead of changing the flow runner.

SSH forwarding matters because EVE-NG console URLs may expose dynamic Telnet
ports that are not reachable from the workstation. In some deployments, only SSH
to the EVE-NG host is allowed, while console ports are reachable only from the
EVE-NG server itself.

The future transport path should be:

```text
local EvePilot
  -> SSH to EVE-NG host
    -> connect from EVE-NG host to 127.0.0.1:<console-port>
```

SSH forwarding is not part of Milestone 0.2.0.

Flow files must define both state markers and steps. State markers describe how
to recognize a console state using plain string patterns and/or regex patterns.
Steps describe what to do when a named state is detected.

The flow runner must use flow-defined markers to detect the current console
state before executing a step. It must not blindly start from the first step
every time.

Matcher debug logs should record detection start, plain or regex pattern
matches, no-match diagnostics, ambiguous matches, and the final selected state.
Logs must not include secret variable values.

The runner should:

1. Connect to the console.
2. Read current console output.
3. Detect the current state using the flow-defined state markers.
4. Find the step that handles that state.
5. Execute that step.
6. Follow the step's `next` rule.
7. Continue until a ready state, stop rule, error, or timeout is reached.

This makes flows resumable. If a user manually answered an earlier prompt before
running EvePilot, the runner can continue from the currently detected state
instead of restarting from step one.

The flow runner executes explicit user or default instructions such as `wait`,
`send`, `send_if_no_output`, `expect`, and `expect_send`.

## Milestone 0.2.0 Action Surface

Milestone 0.2.0 supports only the following flow actions:

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

The `ready` action marks the final prepared state:

```yaml
- name: ready
  when_state: privileged_exec_prompt
  action: ready
```

Each non-terminal flow step may use a small flow-control field named `next`.
Omitting `next` means the runner should detect the current state again after
the step completes. The `ready` action is terminal and must not define `next`.

Supported `next` values for Milestone 0.2.0:

- `detect`: read console output again, detect state, and execute the matching
  step. This is useful when a flow author wants the detect behavior to be
  explicit.
- `stop`: stop the flow.
- `step:<step-name>`: jump to a specific named step.

For Milestone 0.2.0, the preferred design is state-driven matching through
`when_state`. `skip_when_state` may be added later if a real flow needs it, but
it should not be part of the first flow-control surface.

Milestone 0.2.0 should move toward this package shape:

```text
packages/evepilot-bootstrap/
`-- src/evepilot/bootstrap/
    |-- errors.py
    |-- transport/
    |   |-- __init__.py
    |   `-- console.py
    `-- preparation/
        |-- __init__.py
        |-- flow_loader.py
        |-- flow_matcher.py
        |-- flow_runner.py
        |-- flow_validator.py
        |-- models.py
        `-- flows/
            |-- __init__.py
            `-- cisco-router-first-boot.yaml
```

Initial flow models should be shaped around these concepts:

- `FlowStateMarker`: how to recognize a named state.
- `FlowStep`: what to do when that state is detected.
- `next`: how the runner should continue after a step executes.

`FlowStep.optional` is reserved in Milestone 0.2.0. Flows may parse it, but the
runner must not rely on optional-step behavior until it is implemented and
tested.

`FlowRunResult.output_sample` currently stores the latest output returned by the
console. A later milestone should cap this value to a bounded sample before
larger command output or config push workflows are added.

## Consequences

- Custom lab and router behavior can be handled without changing Python code.
- Built-in flows can provide practical starters for common images.
- New built-in flows can be added by adding a YAML resource with a unique file
  name stem, without changing Python registry code.
- Duplicate built-in flow file name stems must fail validation.
- Built-in YAML `name` values must match their file name stems.
- Custom flow-name lookup can be added later without changing the current
  explicit path behavior.
- C8000v, CSR1000v, IOSv, reload workflows, and lab-specific behavior can be
  added incrementally.
- Console preparation logic becomes explicit and testable.
- Async console transport keeps flow execution independent from Telnet details.
- SSH-port-forwarded console access can be added later without rewriting the
  flow runner.
- Flow-driven preparation is isolated from future config injection, reload, and
  verification logic.
- Flows can resume from the current router state instead of assuming a fresh
  first-boot sequence.
- Flow control stays small by using `next` rather than a separate `jump_to`
  field.
- The first flow runner should keep the action set small.
- Workflow features such as `reload_wait`, branching, loops, templates, and
  variable rendering should be deferred until later milestones.
