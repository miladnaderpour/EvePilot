# Quickstart

This guide walks through the first steps with EvePilot after installation.

See [Installation](installation.md) if you have not set up EvePilot yet.

> EvePilot is currently in early development. The commands below describe the
> intended first CLI workflow once the initial Python package is implemented.

---

## 1. Configure Your EVE-NG Connection

Before using EvePilot, provide your EVE-NG server details. See [Configuration](configuration.md) for all options.

The quickest way is environment variables:

```bash
export EVEPILOT_HOST=10.1.2.3
export EVEPILOT_USERNAME=admin
export EVEPILOT_PASSWORD=eve
```

On Windows (PowerShell):

```powershell
$env:EVEPILOT_HOST = "10.1.2.3"
$env:EVEPILOT_USERNAME = "admin"
$env:EVEPILOT_PASSWORD = "eve"
```

---

## 2. List Labs

List all available labs on your EVE-NG instance:

```bash
evepilot labs list
```

Example output:

```json
[
  {
    "id": "EIGRP/Basics.unl",
    "name": "Basics",
    "path": "/EIGRP/"
  },
  {
    "id": "BGP/Route-Reflector.unl",
    "name": "Route-Reflector",
    "path": "/BGP/"
  }
]
```

---

## 3. List Nodes in a Lab

```bash
evepilot nodes list --lab EIGRP/Basics.unl
```

Example output:

```json
[
  {
    "id": 1,
    "name": "CSR-1",
    "status": 2,
    "type": "qemu",
    "console": "telnet",
    "url": "telnet://10.1.2.3:32769",
    "host": "10.1.2.3",
    "port": 32769
  },
  {
    "id": 2,
    "name": "CSR-2",
    "status": 2,
    "type": "qemu",
    "console": "telnet",
    "url": "telnet://10.1.2.3:32770",
    "host": "10.1.2.3",
    "port": 32770
  }
]
```

---

## 4. Get the Console Endpoint for a Node

```bash
evepilot console get --lab EIGRP/Basics.unl --node CSR-1
```

Example output:

```json
{
  "id": 1,
  "name": "CSR-1",
  "status": 2,
  "type": "qemu",
  "console": "telnet",
  "url": "telnet://10.1.2.3:32769",
  "host": "10.1.2.3",
  "port": 32769
}
```

You can pipe this output to other tools:

```bash
evepilot console get --lab EIGRP/Basics.unl --node CSR-1 | jq '.url'
# "telnet://10.1.2.3:32769"
```

---

## 5. Connect to a Console (Phase 2)

> Console bootstrap is planned for Phase 2 and is not yet available.

---

## Next Steps

- Review all [configuration options](configuration.md)
- Read about the [planned capabilities](../README.md#planned-capabilities) and roadmap
- See [Contributing](../CONTRIBUTING.md) if you want to help build EvePilot
