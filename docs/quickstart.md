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
evepilot nodes --lab EIGRP/Basics.unl
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

## 3. Get the Console Endpoint for a Node

```bash
evepilot node-console --lab EIGRP/Basics.unl --node CSR-1
```

Example output:

```json
{
  "node": "CSR-1",
  "console": {
    "protocol": "telnet",
    "host": "10.1.2.3",
    "port": 32769
  }
}
```

You can pipe this output to other tools:

```bash
evepilot node-console --lab EIGRP/Basics.unl --node CSR-1 | jq '.console.port'
# 32769
```

---

## 4. Connect to a Console (Phase 2)

> Console bootstrap is planned for Phase 2 and is not yet available.

---

## Next Steps

- Review all [configuration options](configuration.md)
- Read about the [planned capabilities](../README.md#planned-capabilities) and roadmap
- See [Contributing](../CONTRIBUTING.md) if you want to help build EvePilot
