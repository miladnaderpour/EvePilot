# Config Apply Example

Milestone 0.3.0 will apply already-rendered plain text configuration files
through a prepared console session.

EvePilot does not render Jinja2 templates and does not resolve inventory
variables. Tools such as Ansible should generate the final text file. EvePilot
then sends that rendered text to the router console line by line.

## Example Rendered Config

See:

```text
examples/configs/cisco-iosxe-basic.txt
```

This file is intentionally plain IOS XE text. It includes Cisco `!` separator
and comment lines because rendered configs commonly include them.

## Planned Command

```bash
evepilot bootstrap apply \
  --lab EIGRP/Basics.unl \
  --node CSR-1 \
  --flow built-in:cisco-router-first-boot \
  --file examples/configs/cisco-iosxe-basic.txt
```

## Line Filtering

For Milestone 0.3.0, EvePilot should skip:

- Empty lines.
- Lines where the stripped value starts with `!`.

EvePilot should not skip lines beginning with `#` by default in Milestone 0.3.0.
Generated `#` comments can be handled by future options if a real workflow needs
that behavior.

## Output

The CLI should return structured JSON so Ansible, CI/CD jobs, and tools such as
`jq` can consume the result.

JSON is the default output format. Text output is available for terminal
inspection:

```bash
evepilot bootstrap apply \
  --lab EIGRP/Basics.unl \
  --node CSR-1 \
  --file examples/configs/cisco-iosxe-basic.txt \
  --format text
```

The top-level CLI result may use `duration_seconds` for the full command
runtime. The internal config-apply result should use `apply_duration_seconds`
for the line-by-line config application time only.

Example planned result shape:

```json
{
  "ok": true,
  "code": "bootstrap.apply.completed",
  "data": {
    "node": "CSR-1",
    "config_path": "examples/configs/cisco-iosxe-basic.txt",
    "prepared": true,
    "preparation": {
      "flow_name": "cisco-router-first-boot",
      "final_state": "privileged_exec_prompt",
      "ready": true
    },
    "config_apply": {
      "commands_total": 38,
      "commands_sent": 38,
      "ready": false,
      "final_state": null,
      "apply_duration_seconds": 4.2
    },
    "duration_seconds": 12.4
  },
  "error": null,
  "meta": {
    "service": "EvePilot",
    "version": "0.3.0",
    "timestamp": "2026-06-07T12:00:00+00:00",
    "duration_seconds": 12.4,
    "request_id": null
  }
}
```
