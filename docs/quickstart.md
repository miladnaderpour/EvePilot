# Quickstart

This guide walks through the first steps with EvePilot after installation.

See [Installation](installation.md) if you have not set up EvePilot yet.

> EvePilot is currently in early development. The first CLI workflow focuses on
> EVE-NG node discovery and console endpoint extraction.

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
[
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
  },
  {
    "id": 2,
    "name": "CSR-2",
    "status": 2,
    "type": "qemu",
    "url": "telnet://10.1.2.3:32770",
    "console": {
      "protocol": "telnet",
      "host": "10.1.2.3",
      "port": 32770
    }
  }
]
```

---

## 3. Get a Node by Name

```bash
evepilot nodes get --lab EIGRP/Basics.unl --node CSR-1
```

Example output:

```json
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
```

You can pipe this output to other tools:

```bash
evepilot nodes get --lab EIGRP/Basics.unl --node CSR-1 | jq '.console.port'
# 32769
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

---

## Next Steps

- Review all [configuration options](configuration.md)
- Read about the [planned capabilities](../README.md#planned-capabilities) and roadmap
- See [Contributing](../CONTRIBUTING.md) if you want to help build EvePilot
