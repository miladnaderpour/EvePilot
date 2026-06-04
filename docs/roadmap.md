# Roadmap

EvePilot is planned to grow in phases. The roadmap is intentionally lightweight
while the project is in early development.

## Phase 1 - EVE-NG API Discovery

- Authenticate to the EVE-NG API.
- List available labs.
- List nodes in a lab.
- Retrieve node metadata.
- Extract console URLs, hosts, and ports.
- Return structured JSON output.

## Phase 2 - Console Bootstrap

- Connect to router and switch consoles.
- Detect initial prompts.
- Handle initial configuration dialogs.
- Push bootstrap configuration.
- Enable management access such as SSH.
- Wait for devices to become reachable.

## Phase 3 - Lab Lifecycle Automation

- Start and stop labs.
- Start, stop, wipe, reload, and reset nodes.
- Export and import startup configuration.
- Prepare labs before automated testing.

## Phase 4 - Monitoring

- Collect EVE-NG host health.
- Track node status and resource usage.
- Check console and API availability.
- Prepare metrics for monitoring systems.

## Phase 5 - CI/CD Integrations

- Support GitHub Actions, GitLab CI, Jenkins, and custom runners.
- Start labs from pipelines.
- Bootstrap devices before configuration management.
- Report validation results back to the pipeline.

## Phase 6 - API Service and UI

- Add an API service for remote orchestration.
- Add a web UI for lab control and job visibility.
- Explore reusable topology templates and lab generation.
