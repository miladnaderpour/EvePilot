# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| Latest (`main`) | Yes |

As EvePilot is in early development, only the latest version on `main` receives security fixes.

---

## Reporting a Vulnerability

If you discover a security vulnerability in EvePilot, **please do not open a public GitHub issue.**

Report it privately by emailing:

**milad.naderpour@gmail.com**

Include in your report:
- A description of the vulnerability
- Steps to reproduce it
- The potential impact
- Any suggested fix (optional)

You will receive an acknowledgement within **5 business days**.

If the vulnerability is confirmed, a fix will be prioritized and a security advisory will be published after the fix is released.

---

## Scope

Security issues of interest include:

- Credential exposure (e.g., EVE-NG API tokens or passwords logged or stored insecurely)
- Command injection via crafted lab or node names
- Insecure handling of telnet/console connections
- Dependency vulnerabilities with a direct exploit path

Out of scope:
- Vulnerabilities in EVE-NG itself (report those to the EVE-NG project)
- Issues that require physical access to the machine running EvePilot
- Theoretical vulnerabilities with no practical exploit path

---

## Disclosure Policy

EvePilot follows a **coordinated disclosure** model. Please allow reasonable time for a fix to be developed and released before any public disclosure.
