# Changelog

All notable changes to EvePilot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.3.0] - 2026-06-07

EvePilot 0.3.0 is an early preview release for lab testing. CLI commands and
JSON schemas may still change before version 1.0.0.

### Added

- Initial project structure and repository setup
- README with vision, planned capabilities, and architecture overview
- Apache 2.0 license
- Git ignore rules for local configuration, credentials, caches, and build outputs
- Initial public documentation structure for vision, roadmap, architecture,
  decisions, and research
- Project guidelines for repository layout, Python namespace, and service
  installer expectations
- Contribution guidelines for scoped commit messages
- Architecture decision for Python `src/` layout and shared namespace packages
- Milestone 0.1.0 Python scaffold with core package, EVE-NG package, CLI app,
  and focused tests
- EVE-NG-specific errors separated from core base exceptions
- EVE-NG domain error factories for stable codes, messages, and details
- Multi-target logging configuration for stdout and file outputs with JSON and
  text formats
- Project guidelines for logging configuration, UTC log timestamps, and
  dataclass/model naming
- Documentation for local and Linux service log file path conventions
- Bootstrap design guideline and architecture decision for state-aware console
  automation
- Initial bootstrap package scaffold with flow models and domain errors
- Bootstrap flow models, state matcher, validation, YAML loader, and generic
  Cisco router built-in flow
- Built-in bootstrap flow discovery from packaged YAML resource file names with
  YAML `name` validation
- Future flow resolution rule for local user-managed flow names
- Async bootstrap flow runner skeleton with in-memory console session tests
- Console wake retry handling for silent bootstrap console sessions
- Async console transport design for Telnet now and SSH-port-forwarded console
  access later
- Async Telnet console session using `telnetlib3`
- Bootstrap package layout split into `transport` and `preparation` subpackages
- Bootstrap design refinement for flow-driven preparation
- Bootstrap flow design rule for resumable flows with flow-defined state markers
- Bootstrap flow-control design using step-level `next` rules
- Milestone 0.2.0 bootstrap flow action surface
- Bootstrap preparation variable resolution from `EVEPILOT_BOOTSTRAP_`
  environment variables
- Resource-first CLI command structure for node discovery commands
- CLI `bootstrap prepare` command for running a preparation flow against a node
  console
- Buffered, retry-based console state detection for real router boot behavior
- Raw TCP console transport and automatic transport selection for Dynamips nodes
- CLI `bootstrap flow list`, `bootstrap flow show`, and `bootstrap flow export`
  commands for built-in preparation flows
- Built-in Cisco router flow support for enable password prompts after
  first-boot secret setup
- CLI detection timeout override with `--timeout` and
  `--detect-console-timeout`
- Debug logging for flow matching, selected states, and no-match diagnostics
- Architecture decision for Milestone 0.3.0 rendered text config apply
- Example rendered Cisco IOS XE config for future console config apply
- Project identity update with `evepilot.io`, brand assets, and brand guide
- Project documentation (CHANGELOG, CONTRIBUTING, SECURITY, NOTICE)
- GitHub issue and pull request templates
- Developer documentation (installation, quickstart, configuration)

### Changed

- Move CLI workflow logic into package service layers for EVE-NG and bootstrap
  domains.
- Wrap CLI JSON output in shared `ServiceResult` envelopes.
- Add `--format json` and `--format text` support for CLI commands.
- Keep config apply vendor-neutral and defer platform-specific error detection
  to future flow/profile-driven BYOE error patterns.
- Simplify public config apply output by hiding per-command command results by
  default.
- Submit flow secrets with Enter automatically when the environment value has no
  newline.

### Preview Scope

Users can test a complete early workflow:

1. Connect to EVE-NG.
2. List lab nodes.
3. Get a node console endpoint.
4. Prepare a router console.
5. Apply already-rendered plain text config.
6. Receive JSON or text CLI output.

---

<!-- Releases will be added below as they are published -->

<!-- Template:
## [x.y.z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in a future release

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security vulnerability fixes
-->
