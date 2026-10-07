# Event model

`nativerelay.model` is the platform-neutral source of truth for the normalized contract. JSON is its serialization, with `schema_version: 1`; it is used for inspection and exchange rather than as a separate architecture.

## Event families

| Event | Meaning |
|---|---|
| `process.started` | The native source reported a process start. |
| `process.exited` | The native source reported a process exit. It does not imply every thread independently exited. |
| `file.opened` | The source reported an open operation; this does not prove bytes were read. |
| `file.created` | The source reported creation. Unsupported by the Linux Phase 1 collector. |
| `file.modified` | The source reported a modification notification; changed bytes and durable storage are unknown. |
| `file.deleted` | The source reported deletion. Unsupported by the Linux Phase 1 collector. |
| `file.renamed` | The source reported a rename. Unsupported by the Linux Phase 1 collector. |

Collectors emit only observations their native source supports. `evidence` is `observed` for NativeRelay Phase 1 events; derived observations must be labelled `derived` and must not be presented as kernel facts.

## Shape and identity

Each `Event` contains `id`, `timestamp`, `type`, `platform`, `collector`, `process`, optional `resource`, `metadata`, `evidence`, optional `sequence`, and schema version in its JSON representation. Process fields are PID, optional parent PID, optional executable, and optional command/argv. Command is absent (`null`) unless explicitly opted in by the collector. A resource contains a type and path; no file content is read.

IDs are random UUIDs by default and remain unchanged after emission. `Event.stable_id(collector, boot_id, sequence)` is available when a source identity and durable sequence exist. Linux currently uses UUIDs. PID is an operating-system identifier that can be reused; it is not a durable process identity. A consumer needing correlation across reuse should use lifecycle boundaries and its own higher-level identity.

Timestamps are timezone-aware ISO-8601 instants. Linux uses userspace receipt/normalization time, not the original kernel event time. Linux assigns an optional monotonically increasing sequence in its normalized publication order, shared across its collector threads for one run. This does not claim kernel causality or ordering between different collectors. Sequence gaps can signal events that were dropped from the bounded stream.

## Capabilities and health

A `Capability` is per event type and includes `status`, `reason`, `scope`, and attribution source. Status values are `supported` (implemented but not started), `available` (initialized and currently able to observe), `degraded`, `permission_denied`, `unavailable`, and `unsupported`. `available` is not a guarantee of complete coverage. Linux process and filesystem sources initialize independently.

A timeout from `EventStream.receive(timeout=...)` means no event arrived before the deadline; it does not mean no operating-system activity occurred. `EventStream.dropped` counts queue drops. Linux health also reports fanotify overflow, parse/path errors, startup failures, and queue loss. CN_PROC loss is not precisely counted in Phase 1, so process observations remain best effort even when available. `EventStream.close()` stops accepting events, drains buffered events, and then `receive()` raises `StreamClosed`; its optional `error` carries a producer failure. Linux collector shutdown closes its stream.

## Example JSON

```json
{"schema_version":1,"id":"b2d8d00f-96a1-4ce6-9912-6bf3ea913002","sequence":18,"timestamp":"2026-10-07T12:00:00+00:00","type":"file.opened","platform":"linux","collector":"linux-kernel","process":{"pid":4218,"parent_pid":4000,"executable":"/usr/bin/editor","command":null},"resource":{"type":"file","path":"/workspace/src/main.py"},"metadata":{},"evidence":"observed"}
```

Consumers should branch on known event types and schema version, query capabilities rather than infer support from silence, and inspect stream/collector health for gaps. NativeRelay does not identify applications, AI agents, sessions, or runs.
