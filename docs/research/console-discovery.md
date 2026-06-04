# Console Discovery Research

Console discovery is the first practical EvePilot workflow.

## Primary Method

Use EVE-NG API node metadata to retrieve console information.

Expected output should include:

- Node ID
- Node name
- Node status
- Node type
- Console protocol
- Console URL
- Parsed host
- Parsed port

Example:

```json
{
  "id": 1,
  "name": "CSR-1",
  "status": 2,
  "type": "qemu",
  "console": "telnet",
  "url": "telnet://10.1.2.3:32769",
  "host": "10.1.2.3",
  "port": 32769
}
```

## Fallback Method

If API metadata is incomplete, host-side diagnostics may inspect listening
sockets and EVE-NG wrapper processes.

Possible diagnostic sources:

- `ss`
- `/proc`
- EVE-NG wrapper process arguments

This should remain a fallback or debugging path, not the normal discovery
method.

## Implementation Notes

- Do not hardcode console ports.
- Parse URLs with a structured URL parser.
- Keep parsing logic testable without a live EVE-NG server.
- Keep credentials and local lab details in private ignored notes.
