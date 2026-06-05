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

Flow files must define both state markers and steps. State markers describe how
to recognize a console state using plain string patterns and/or regex patterns.
Steps describe what to do when a named state is detected.

The flow runner must use flow-defined markers to detect the current console
state before executing a step. It must not blindly start from the first step
every time.

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

The `ready` action marks the final prepared state:

```yaml
- name: ready
  when_state: privileged_exec_prompt
  action: ready
  next: stop
```

Each flow step must support a small flow-control field named `next`.

Supported `next` values for Milestone 0.2.0:

- `detect`: read console output again, detect state, and execute the matching
  step.
- `next`: continue to the next step in order.
- `stop`: stop the flow.
- `step:<step-name>`: jump to a specific named step.

For Milestone 0.2.0, the preferred design is state-driven matching through
`when_state`. `skip_when_state` may be added later if a real flow needs it, but
it should not be part of the first flow-control surface.

The generic detector is an optional helper for debugging and validation. It must
not be the main decision engine for preparing all router types.

Milestone 0.2.0 should move toward this package shape:

```text
packages/evepilot-bootstrap/
`-- src/evepilot/bootstrap/
    |-- console.py
    |-- errors.py
    |-- flow_loader.py
    |-- flow_runner.py
    |-- models.py
    `-- flows/
        |-- __init__.py
        `-- cisco_c8000v_first_boot.yaml
```

The detector may remain as a diagnostic helper.

Initial flow models should be shaped around these concepts:

- `FlowStateMarker`: how to recognize a named state.
- `FlowStep`: what to do when that state is detected.
- `next`: how the runner should continue after a step executes.

Flow startup options may later support behavior such as an initial read delay and
sending Enter when the console is silent.

## Consequences

- Custom lab and router behavior can be handled without changing Python code.
- Built-in flows can provide practical starters for common images.
- C8000v, CSR1000v, IOSv, reload workflows, and lab-specific behavior can be
  added incrementally.
- Console preparation logic becomes explicit and testable.
- Flows can resume from the current router state instead of assuming a fresh
  first-boot sequence.
- Flow control stays small by using `next` rather than a separate `jump_to`
  field.
- The first flow runner should keep the action set small.
- Workflow features such as `reload_wait`, branching, loops, templates, and
  variable rendering should be deferred until later milestones.
