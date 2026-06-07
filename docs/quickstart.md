# Quickstart

This guide walks through the first steps with EvePilot after installation.

See [Installation](installation.md) if you have not set up EvePilot yet.

> EvePilot is currently in early preview. It is usable for lab testing, but CLI
> commands and JSON schemas may change before version 1.0.0.

---

## 1. Configure Your EVE-NG Connection

Before using EvePilot, provide your EVE-NG server details. See [Configuration](configuration.md) for all options.

The quickest way is environment variables:

```bash
export EVEPILOT_EVE_NG_URL=http://10.1.2.3
export EVEPILOT_EVE_NG_USERNAME=admin
export EVEPILOT_EVE_NG_PASSWORD=eve
```

On Windows (PowerShell):

```powershell
$env:EVEPILOT_EVE_NG_URL = "http://10.1.2.3"
$env:EVEPILOT_EVE_NG_USERNAME = "admin"
$env:EVEPILOT_EVE_NG_PASSWORD = "eve"
```

---

## 2. List Nodes in a Lab

```bash
evepilot nodes all --lab EIGRP/Basics.unl
```

Example output:

```json
{
  "ok": true,
  "code": "nodes.all.completed",
  "data": {
    "nodes": [
      {
        "id": 1,
        "name": "CSR-1",
        "status": 2,
        "type": "qemu",
        "url": "telnet://10.1.2.3:32769",
        "console": {
          "protocol": "telnet",
          "host": "10.1.2.3",
          "port": 32769
        }
      }
    ]
  },
  "error": null,
  "meta": {
    "service": "EvePilot",
    "version": "0.3.0",
    "timestamp": "2026-06-07T12:00:00+00:00",
    "duration_seconds": 0.4,
    "request_id": null
  }
}
```

---

## 3. Get a Node by Name

```bash
evepilot nodes get --lab EIGRP/Basics.unl --node CSR-1
```

Example output:

```json
{
  "ok": true,
  "code": "nodes.get.completed",
  "data": {
    "id": 1,
    "name": "CSR-1",
    "status": 2,
    "type": "qemu",
    "url": "telnet://10.1.2.3:32769",
    "console": {
      "protocol": "telnet",
      "host": "10.1.2.3",
      "port": 32769
    }
  }
}
```

You can pipe this output to other tools:

```bash
evepilot nodes get --lab EIGRP/Basics.unl --node CSR-1 | jq '.data.console.port'
# 32769
```

JSON is the default output format. For a human-friendly rendering, use:

```bash
evepilot nodes get --lab EIGRP/Basics.unl --node CSR-1 --format text
```

---

## 4. Prepare a Console

List available built-in preparation flows:

```bash
evepilot bootstrap flow list
```

Inspect a built-in flow:

```bash
evepilot bootstrap flow show built-in:cisco-router-first-boot
```

Export a built-in flow so you can customize it locally:

```bash
evepilot bootstrap flow export \
  built-in:cisco-router-first-boot \
  --output flows/cisco-router-first-boot.yaml
```

Run the built-in Cisco first-boot preparation flow:

```bash
evepilot bootstrap prepare \
  --lab EIGRP/Basics.unl \
  --node CSR-1 \
  --flow built-in:cisco-router-first-boot
```

EvePilot discovers the node console endpoint from EVE-NG, selects the console
transport, runs the selected preparation flow, and returns structured JSON.

Most commands support `--format json` and `--format text`. Use JSON for
automation and text for quick terminal inspection.

By default, `--transport auto` uses Telnet for most EVE-NG nodes and raw TCP for
Dynamips nodes. You can override the transport if needed:

```bash
evepilot bootstrap prepare \
  --lab EIGRP/Basics.unl \
  --node R-20 \
  --transport raw-tcp
```

Slow router images may need more time to print the next flow-defined console
state. Increase the detection timeout with either option:

```bash
evepilot bootstrap prepare \
  --lab EIGRP/Basics.unl \
  --node C8000V-1 \
  --timeout 240
```

`--detect-console-timeout` is the longer equivalent of `--timeout`.

If the selected flow requires an enable secret or later needs the same value for
an enable password prompt, provide it with an environment variable:

```bash
export EVEPILOT_BOOTSTRAP_ENABLE_SECRET=EvePilotLab123
```

Use the plain secret value. EvePilot sends the required Enter when the flow uses
the secret at a console prompt.

---

## 5. Apply a Rendered Config

EvePilot can apply an already-rendered text config through the prepared console.
It does not render Jinja2 templates or resolve inventory variables. Tools such
as Ansible should create the final config file first.

Try the included example config:

```bash
evepilot bootstrap apply \
  --lab EIGRP/Basics.unl \
  --node CSR-1 \
  --flow built-in:cisco-router-first-boot \
  --file examples/configs/cisco-iosxe-basic.txt
```

Example output:

```json
{
  "ok": true,
  "code": "bootstrap.apply.completed",
  "data": {
    "node": "CSR-1",
    "flow": "built-in:cisco-router-first-boot",
    "transport": "telnet",
    "config_path": "examples/configs/cisco-iosxe-basic.txt",
    "prepared": true,
    "config_apply": {
      "commands_total": 38,
      "commands_sent": 38,
      "ready": false,
      "final_state": null,
      "apply_duration_seconds": 4.2
    },
    "duration_seconds": 7.6
  },
  "error": null,
  "meta": {
    "service": "EvePilot",
    "version": "0.3.0",
    "timestamp": "2026-06-07T12:00:00+00:00",
    "duration_seconds": 7.7,
    "request_id": null
  }
}
```

For terminal inspection:

```bash
evepilot bootstrap apply \
  --lab EIGRP/Basics.unl \
  --node CSR-1 \
  --file examples/configs/cisco-iosxe-basic.txt \
  --format text
```

The config file must match the target device image and interface model. EvePilot
keeps config apply vendor-neutral in this milestone and does not hardcode
platform-specific command error detection.

---

## Next Steps

- Review all [configuration options](configuration.md)
- Read the [roadmap](roadmap.md)
- See [Contributing](../CONTRIBUTING.md) if you want to help build EvePilot
