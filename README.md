# EvePilot

**EvePilot** is an automation toolkit for **EVE-NG** labs.

The goal of EvePilot is to help network engineers, NetDevOps practitioners, and certification candidates automate EVE-NG lab environments for lab discovery, node orchestration, console bootstrap, monitoring, and CI/CD-driven network automation workflows.

EvePilot starts with a simple but powerful problem:

> How can we programmatically discover EVE-NG lab nodes and their console endpoints so routers and switches can be bootstrapped automatically before SSH or management access exists?

Over time, EvePilot is intended to grow into a broader automation platform for EVE-NG environments.

---

## Vision

EVE-NG is a powerful platform for network labs, but many workflows are still manual:

- Opening node consoles manually
- Finding console ports manually
- Starting and stopping nodes manually
- Applying day-zero configuration manually
- Rebuilding labs manually
- Validating labs manually
- Integrating labs with CI/CD pipelines manually

EvePilot aims to reduce that manual work.

The long-term vision is to make EVE-NG labs easier to control, automate, monitor, validate, and reuse as part of modern NetDevOps workflows.

---

## Planned Capabilities

EvePilot is designed to grow in phases.

### Phase 1 - EVE-NG API Discovery

Initial focus:

- Authenticate to the EVE-NG API
- List labs
- List nodes in a lab
- Retrieve node metadata
- Retrieve console URLs and ports
- Map node names to console endpoints
- Return structured JSON output for automation tools

Example use case:

```text
Node name: CSR-1
Lab: EIGRP/Basics.unl

Result:
telnet://10.1.2.3:32769
```

---

### Phase 2 - Console Bootstrap

After console endpoint discovery, EvePilot will support day-zero device onboarding.

Planned features:

- Connect to router/switch console
- Detect initial prompts
- Handle initial configuration dialog
- Push bootstrap configuration
- Configure management IP
- Enable SSH
- Save configuration
- Wait until the device becomes reachable over SSH

This is useful because a new router in an EVE-NG lab may not have any management IP yet. In that situation, normal automation tools such as Ansible cannot connect over SSH. The only available access method is the console.

---

### Phase 3 - Lab Lifecycle Automation

Future lab operations may include:

- Start lab
- Stop lab
- Start node
- Stop node
- Wipe node
- Reload node
- Export node configuration
- Import startup configuration
- Reset lab state
- Prepare lab before automated testing

---

### Phase 4 - CI/CD Integration

EvePilot is intended to support CI/CD-driven network lab workflows.

Possible integrations:

- GitHub Actions
- GitLab CI
- Jenkins
- Ansible Automation Platform
- Custom pipeline runners

Example future workflow:

```text
Git push
  |
  v
CI/CD pipeline starts EVE-NG lab
  |
  v
EvePilot discovers nodes
  |
  v
EvePilot bootstraps devices
  |
  v
Ansible applies full configuration
  |
  v
Tests validate routing, reachability, and services
  |
  v
Pipeline reports success or failure
```

---

### Phase 5 - Monitoring and Observability

Future monitoring features may include:

- EVE-NG host health
- CPU and memory usage
- Node status
- Running/stopped node inventory
- Console availability
- Lab resource usage
- API health checks
- Integration with monitoring stacks

---

### Phase 6 - Lab Generation and UI

Long-term ideas:

- Terraform-driven lab generation
- API-based topology creation
- Reusable lab templates
- Web UI
- Node control panel
- Automation job history

---

## Why EvePilot?

EvePilot is not intended to replace EVE-NG.

It is intended to act as an automation layer around EVE-NG.

The main goals are:

- Make EVE-NG easier to automate
- Support day-zero device bootstrap
- Help integrate network labs with CI/CD workflows
- Reduce repetitive manual lab tasks
- Create a reusable framework for lab orchestration
- Support network automation learning and testing

---

## First Milestone

The first working version will focus on API-based node discovery.

Minimum target features:

- Login to EVE-NG API
- Query nodes from a specific lab
- Find a node by name
- Extract console URL
- Parse console host and port
- Return clean JSON output

Example command idea:

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
  }
]
```

Example command idea:

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

---

## Current Scope

The project is currently in the early design and implementation phase.

The first implementation will focus on:

- Python-based core logic
- Clean project structure
- EVE-NG API client
- Typed data models
- Console URL parsing
- JSON output
- Testable components

The CLI will be the first interface, but EvePilot should be understood as an automation toolkit, not only as a CLI tool.

---

## Possible Future Architecture

```text
+-------------------+
|   CI/CD Pipeline  |
| GitHub/Jenkins    |
+---------+---------+
          |
          v
+-------------------+
|     EvePilot      |
| Automation Layer  |
+---------+---------+
          |
          v
+-------------------+
|     EVE-NG API    |
| Labs / Nodes      |
+---------+---------+
          |
          v
+-------------------+
| Network Devices   |
| Console / SSH     |
+-------------------+
```

Future architecture may include:

```text
CLI
API service
Web UI
Scheduler
Monitoring collector
Lab builder
Bootstrap engine
CI/CD integration module
```

---

## Example Use Cases

### 1. Discover Console Port

Find the console endpoint of a router by name:

```text
Input:
  lab = EIGRP/Basics.unl
  node = CSR-1

Output:
  telnet://10.1.2.3:32769
```

---

### 2. Bootstrap a New Router

A new router has no management IP.

EvePilot discovers the console port, connects to the console, pushes bootstrap configuration, enables SSH, and prepares the device for normal automation.

---

### 3. Prepare a Lab for Ansible

EvePilot performs day-zero bootstrap.

Then Ansible connects over SSH and applies the full configuration.

---

### 4. Use EVE-NG in CI/CD

A pipeline starts a lab, applies configurations, runs validation tests, and reports the result automatically.

---

## Technology Stack

Initial stack:

- Python
- EVE-NG API
- Requests / HTTP client
- Pydantic models
- Typer or Click for CLI
- Pytest for testing

Possible future stack:

- FastAPI
- Vue.js
- PostgreSQL
- Terraform integration
- Ansible integration
- Prometheus / Grafana integration

---

## Development Principles

EvePilot should follow these principles:

- Keep the core logic clean and testable
- Separate API logic from CLI logic
- Use typed models where possible
- Return structured JSON for automation
- Avoid hardcoded console ports
- Treat EVE-NG API as the primary source of truth
- Use Linux process inspection only as fallback/debugging
- Build small features first, but keep the architecture open for future growth

---

## License

This project is licensed under the **Apache License 2.0**.

---

## Project Status

Early development.

Current focus:

```text
Lab node discovery
Console URL and port extraction
Structured JSON output
```

---

## Author

Created by **Milad Naderpour** as a personal NetDevOps project for EVE-NG automation, CI/CD lab workflows, and network engineering practice.

---

## Disclaimer

EvePilot is an independent personal project and is not affiliated with, endorsed by, or sponsored by EVE-NG or any vendor.

Use it carefully in lab environments. Always validate automation before applying it to important systems.
