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

Example planned result shape:

```json
{
  "node": "CSR-1",
  "file": "examples/configs/cisco-iosxe-basic.txt",
  "prepared": true,
  "commands_total": 38,
  "commands_sent": 38,
  "final_state": "privileged_exec_prompt",
  "ready": true,
  "duration_seconds": 12.4,
  "errors": []
}
```
