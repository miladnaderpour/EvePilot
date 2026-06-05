# Configuration

EvePilot can be configured using environment variables or a local `.env` file.
Environment variables use the `EVEPILOT_` prefix and are case-sensitive.

---

## Configuration Methods

Configuration is resolved in the following priority order (highest to lowest):

1. Environment variables
2. `.env` file in the current working directory
3. Defaults

---

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `EVEPILOT_EVE_NG_URL` | EVE-NG base URL, including protocol | Required |
| `EVEPILOT_EVE_NG_USERNAME` | EVE-NG username | Required |
| `EVEPILOT_EVE_NG_PASSWORD` | EVE-NG password | Required |
| `EVEPILOT_EVE_NG_VERIFY_SSL` | Verify SSL certificates (`true` / `false`) | `false` |
| `EVEPILOT_EVE_NG_TIMEOUT_SECONDS` | Request timeout in seconds | `10.0` |
| `EVEPILOT_LOG_LEVEL` | Logging level | `INFO` |
| `EVEPILOT_LOG_FORMAT` | Logging format (`json` / `text`) | `json` |
| `EVEPILOT_LOG_OUTPUT` | Logging output (`stdout` / `file`) | `stdout` |
| `EVEPILOT_LOG_FILE_PATH` | File logging path when output is `file` | `logs/evepilot.log` |
| `EVEPILOT_LOG_TARGETS_JSON` | Advanced multi-target logging configuration | unset |

Example:

```bash
export EVEPILOT_EVE_NG_URL=http://10.1.2.3
export EVEPILOT_EVE_NG_USERNAME=admin
export EVEPILOT_EVE_NG_PASSWORD=eve
export EVEPILOT_EVE_NG_VERIFY_SSL=false
export EVEPILOT_LOG_OUTPUT=stdout
export EVEPILOT_LOG_LEVEL=INFO
export EVEPILOT_LOG_FORMAT=json
```

---

## `.env` File

EvePilot also loads a local `.env` file from the current working directory.

Example `.env`:

```text
EVEPILOT_EVE_NG_URL=http://10.1.2.3
EVEPILOT_EVE_NG_USERNAME=admin
EVEPILOT_EVE_NG_PASSWORD=eve
EVEPILOT_EVE_NG_VERIFY_SSL=false
EVEPILOT_LOG_LEVEL=INFO
EVEPILOT_LOG_FORMAT=json
EVEPILOT_LOG_OUTPUT=stdout
```

> **Security note:** Do not commit `.env` files that contain credentials to
> version control. `.env` is ignored by the project `.gitignore`.

---

## SSL Verification

If your EVE-NG instance uses a self-signed certificate, disable SSL verification:

```bash
export EVEPILOT_EVE_NG_VERIFY_SSL=false
```

Or in `.env`:

```text
EVEPILOT_EVE_NG_VERIFY_SSL=false
```

> **Warning:** Disabling SSL verification removes protection against man-in-the-middle attacks. Only do this in trusted lab environments.

---

## Output

The first CLI commands return structured JSON suitable for piping to `jq` or
other automation tools:

```bash
evepilot nodes --lab EIGRP/Basics.unl
```

## Logging

Simple logging configuration creates one logging target:

```text
EVEPILOT_LOG_OUTPUT=stdout
EVEPILOT_LOG_LEVEL=INFO
EVEPILOT_LOG_FORMAT=json
EVEPILOT_LOG_FILE_PATH=logs/evepilot.log
```

The default log file path is `logs/evepilot.log` for local development.
Installed Linux services should use `/var/log/evepilot/evepilot.log`,
configured by the installer script through `/etc/evepilot/evepilot.env`.

Advanced logging configuration can define multiple targets with
`EVEPILOT_LOG_TARGETS_JSON`:

```text
EVEPILOT_LOG_TARGETS_JSON='[
  {
    "name": "stdout-json",
    "output": "stdout",
    "level": "INFO",
    "format": "json"
  },
  {
    "name": "file-text",
    "output": "file",
    "level": "INFO",
    "format": "text",
    "file_path": "logs/evepilot.log"
  }
]'
```

For Milestone 0.1.0, supported outputs are `stdout` and `file`. Supported
formats are `json` and `text`. Structured log timestamps use UTC.

Multiple log files should be configured through advanced logging targets, not
through additional hardcoded config keys.
