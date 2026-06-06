# 0010 - Apply rendered text configs through console

## Status

Accepted

## Context

After Milestone 0.2.0, EvePilot can discover EVE-NG node console endpoints and
prepare routers through flow-driven console automation.

The next useful capability is applying configuration through the console after a
device reaches a ready privileged prompt.

Configuration rendering is a separate responsibility. Tools such as Ansible are
well suited for rendering Jinja2 templates, resolving inventory variables, and
producing device-specific configuration text. EvePilot should not duplicate that
template-rendering role.

## Decision

Milestone 0.3.0 will apply already-rendered plain text configuration files
through the prepared console.

This capability should use `apply` naming, not `push` naming. The word `push`
can imply future SSH, NETCONF, RESTCONF, or API workflows. Milestone 0.3.0 is
specifically console-based config apply.

EvePilot will:

- Read a plain text config file.
- Prepare the console using the selected bootstrap preparation flow.
- Send the rendered config text line by line.
- Skip blank lines and lines whose stripped value starts with `!` by default.
- Wait for console output or prompt behavior between commands.
- Return a structured JSON result for automation tools.

EvePilot will not:

- Render Jinja2 templates.
- Resolve inventory variables.
- Manage Ansible inventory.
- Replace Ansible or other upstream renderers.
- Implement multi-stage reload workflows in Milestone 0.3.0.
- Implement advanced router error parsing in Milestone 0.3.0.
- Add comment-handling flags such as `--keep-comments` or
  `--no-skip-comments` in Milestone 0.3.0.

The CLI output should remain JSON-first so tools such as Ansible, CI/CD jobs, and
`jq` can consume the result reliably.

Lines beginning with `#` may be treated as generated comments in a later
milestone, but they should not be filtered by default in Milestone 0.3.0.

Example future command:

```bash
evepilot bootstrap apply \
  --lab EIGRP/Basics.unl \
  --node CSR-1 \
  --flow built-in:cisco-router-first-boot \
  --file rendered-configs/CSR-1.txt
```

Suggested internal package:

```text
evepilot.bootstrap.config_apply
```

Suggested internal names:

- `ConfigApplyResult`
- `ConfigCommandResult`
- `load_config_lines()`
- `apply_config_lines()`

Avoid names such as:

- `config_push`
- `push_config`
- `ConfigPushResult`

Example result shape:

```json
{
  "node": "CSR-1",
  "file": "rendered-configs/CSR-1.txt",
  "prepared": true,
  "commands_total": 5,
  "commands_sent": 5,
  "final_state": "privileged_exec_prompt",
  "ready": true,
  "duration_seconds": 12.4,
  "errors": []
}
```

## Consequences

- EvePilot stays focused on console execution and EVE-NG lab automation.
- Ansible remains responsible for Jinja2 rendering and variable resolution.
- The first config-apply milestone stays small and testable.
- JSON output keeps the CLI friendly to automation tools.
- Skipping blank lines and Cisco `!` separator/comment lines avoids sending
  harmless formatting noise to device consoles.
- `duration_seconds` can be included in results if it is cheap to collect, but
  it is not required for the first implementation.
- Advanced config error parsing can be added later without changing the initial
  boundary.
- Reload-aware and multi-stage workflows remain deferred to a later milestone.
