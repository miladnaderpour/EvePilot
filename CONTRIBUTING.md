# Contributing to EvePilot

Thank you for your interest in contributing to EvePilot.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Getting Started

Before contributing, please:

1. Read the [README](README.md) to understand the project goals and architecture.
2. Check the [open issues](../../issues) to see what is already being worked on.
3. For significant changes, open an issue first to discuss your approach before writing code.

---

## Development Setup

### Prerequisites

- Python 3.10 or later
- A running EVE-NG instance (for integration testing)
- `pip` and `venv`

### Local Setup

```bash
# Clone the repository
git clone https://github.com/milad-naderpour/evepilot.git
cd evepilot

# Create and activate a virtual environment
python -m venv .venv

# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
# Format code
black .

# Check linting
ruff check .

# Type checking
mypy .
```

---

## Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, releasable code |
| `dev` | Active development |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation changes |

Branch from `dev` for all features and fixes. Target `dev` in your pull request.

---

## Coding Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints on all public functions and methods
- Use Pydantic models for structured data
- Keep API client logic separate from CLI logic
- Return structured data (dicts or Pydantic models) from core functions - let the CLI layer format output
- Write tests for new functionality using `pytest`
- Do not hardcode hostnames, ports, or credentials

---

## Commit Messages

Use the following format:

```text
<type>(<scope>): <short summary>

- Bullet point 1
- Bullet point 2
- Bullet point 3
```

Allowed types:

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change with no functional effect |
| `test` | Adding or updating tests |
| `chore` | Build, tooling, or dependency changes |
| `security` | Security-related change |

Example:

```text
feat(eve-ng): add console URL discovery

- Add EVE-NG node lookup by lab path and node name
- Parse console protocol, host, and port from node URL
- Return structured node data for CLI and automation use
```

---

## Pull Requests

1. Target the `dev` branch (not `main`)
2. Fill out the pull request template completely
3. Link the related issue (if any)
4. Ensure all tests pass before requesting review
5. Keep PRs focused - one concern per PR

---

## Reporting Bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) issue template.

Include:
- EvePilot version
- Python version
- EVE-NG version (if relevant)
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or output

---

## Requesting Features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) issue template.

Describe:
- The problem you are trying to solve
- The solution you have in mind
- Any alternatives you have considered

---

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
