# 0006 - Provide installer scripts for service components

## Status

Accepted

## Context

Future EvePilot service components may need to run as Linux services. The API
service is the clearest example. A user should not need to manually create
service users, directories, virtual environments, environment files, and systemd
unit files for normal installation.

Manual systemd instructions are useful as fallback or reference documentation,
but they are not the preferred product experience.

## Decision

EvePilot service components should be installable through provided installer
scripts.

The planned primary flow for the API service is:

```bash
sudo ./scripts/install-api-service.sh
```

The script should handle service setup internally, including user creation,
directory setup, Python environment setup, package installation, environment
file creation, systemd unit generation, daemon reload, service enablement,
service start, and status output.

Upgrade and uninstall flows should also be script-driven:

```bash
sudo ./scripts/upgrade-api-service.sh
sudo ./scripts/uninstall-api-service.sh
```

## Consequences

- Users get a cleaner installation experience.
- Linux service setup becomes repeatable.
- Documentation can focus on the supported install path.
- Manual systemd instructions can stay available as fallback reference.
- The project takes on responsibility for maintaining safe installer scripts.
- Installer scripts must be careful with permissions, credentials, existing
  files, and destructive operations.
