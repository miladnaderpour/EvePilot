# Installation

## Requirements

- Python 3.11 or later
- Access to an EVE-NG instance (Community or Professional)
- Network access to the EVE-NG API (default port 443 or 80)

---

## Install from Source (Development)

EvePilot currently uses a monorepo layout with editable local packages. Install
the core package, EVE-NG integration package, and CLI app from the repository:

```bash
# Clone the repository
git clone https://github.com/milad-naderpour/evepilot.git
cd evepilot

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Install EvePilot packages in editable mode
pip install -e packages/evepilot-core -e packages/evepilot-eve-ng -e apps/cli
```

After installation, verify the CLI works:

```bash
evepilot --help
```

---

## Install with Development Dependencies

If you plan to contribute or run tests, install the editable packages and test
tools:

```bash
pip install -e packages/evepilot-core -e packages/evepilot-eve-ng -e apps/cli pytest ruff mypy
```

This installs the CLI and development tools such as `pytest`, `ruff`, and
`mypy`.

---

## Upgrading

When new changes are available:

```bash
git pull
pip install -e packages/evepilot-core -e packages/evepilot-eve-ng -e apps/cli
```

---

## Uninstalling

```bash
pip uninstall evepilot-cli evepilot-eve-ng evepilot-core
```

---

## Troubleshooting

**`evepilot: command not found`**

Make sure your virtual environment is activated and the CLI package installed
without errors.

**SSL errors connecting to EVE-NG**

If your EVE-NG instance uses a self-signed certificate, you may need to disable SSL verification. See [Configuration](configuration.md) for options.

**Python version errors**

EvePilot requires Python 3.11 or later. Check your version with:

```bash
python --version
```
