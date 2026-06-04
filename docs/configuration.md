# Configuration

EvePilot can be configured using environment variables or a configuration file.

---

## Configuration Methods

Configuration is resolved in the following priority order (highest to lowest):

1. CLI flags (per command)
2. Environment variables
3. Configuration file (`evepilot.toml`)
4. Defaults

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `EVEPILOT_HOST` | EVE-NG server hostname or IP address | Required |
| `EVEPILOT_PORT` | EVE-NG API port | `443` |
| `EVEPILOT_USERNAME` | EVE-NG username | `admin` |
| `EVEPILOT_PASSWORD` | EVE-NG password | Required |
| `EVEPILOT_SSL_VERIFY` | Verify SSL certificates (`true` / `false`) | `true` |
| `EVEPILOT_PROTOCOL` | API protocol (`https` / `http`) | `https` |
| `EVEPILOT_TIMEOUT` | Request timeout in seconds | `30` |
| `EVEPILOT_OUTPUT` | Output format (`json` / `table` / `plain`) | `json` |

Example:

```bash
export EVEPILOT_HOST=10.1.2.3
export EVEPILOT_USERNAME=admin
export EVEPILOT_PASSWORD=eve
export EVEPILOT_SSL_VERIFY=false
```

---

## Configuration File

EvePilot looks for `evepilot.toml` in the following locations (in order):

1. Path specified by `--config` CLI flag
2. Current working directory: `./evepilot.toml`
3. User config directory: `~/.config/evepilot/evepilot.toml`

### Example `evepilot.toml`

```toml
[eveng]
host = "10.1.2.3"
port = 443
username = "admin"
password = "eve"
protocol = "https"
ssl_verify = false
timeout = 30

[output]
format = "json"
```

> **Security note:** Do not commit `evepilot.toml` files that contain credentials to version control. Add `evepilot.toml` to your `.gitignore`.

---

## CLI Flags

Most commands accept connection flags directly:

```bash
evepilot --host 10.1.2.3 --username admin --password eve nodes list --lab EIGRP/Basics.unl
```

Run `evepilot --help` or `evepilot <command> --help` to see all available flags.

---

## SSL Verification

If your EVE-NG instance uses a self-signed certificate, disable SSL verification:

```bash
export EVEPILOT_SSL_VERIFY=false
```

Or in `evepilot.toml`:

```toml
[eveng]
ssl_verify = false
```

> **Warning:** Disabling SSL verification removes protection against man-in-the-middle attacks. Only do this in trusted lab environments.

---

## Output Formats

EvePilot supports multiple output formats for use in different workflows:

| Format | Description |
|---|---|
| `json` | Structured JSON - suitable for piping to `jq` or other tools |
| `table` | Human-readable table |
| `plain` | Minimal plain text - suitable for shell scripting |

Set the default with `EVEPILOT_OUTPUT` or use the `--output` flag per command:

```bash
evepilot nodes list --lab EIGRP/Basics.unl --output table
```
