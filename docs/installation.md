# Installation

## Requirements

- Python 3.10 or later
- Access to an EVE-NG instance (Community or Professional)
- Network access to the EVE-NG API (default port 443 or 80)

---

## Install from Source (Development)

EvePilot is still in the design and early implementation phase. Once Python
packaging is added, install directly from the repository:

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

# Install EvePilot in editable mode after packaging is available
pip install -e .
```

After installation, verify the CLI works:

```bash
evepilot --version
```

---

## Install with Development Dependencies

If you plan to contribute or run tests, install the development dependencies
after the packaging configuration defines them:

```bash
pip install -e ".[dev]"
```

This should install additional tools such as `pytest`, `black`, `ruff`, and
`mypy` once the development dependency group is defined.

---

## Upgrading

When new changes are available:

```bash
git pull
pip install -e .
```

---

## Uninstalling

```bash
pip uninstall evepilot
```

---

## Troubleshooting

**`evepilot: command not found`**

Make sure your virtual environment is activated and the install completed without errors.

If the project does not contain packaging metadata yet, the `evepilot` command
will not be available until the CLI package is implemented.

**SSL errors connecting to EVE-NG**

If your EVE-NG instance uses a self-signed certificate, you may need to disable SSL verification. See [Configuration](configuration.md) for options.

**Python version errors**

EvePilot requires Python 3.10 or later. Check your version with:

```bash
python --version
```
