# Event model

The `nativerelay.model` module is platform-neutral. Event types are stable lowercase names; this initial schema uses `process.started`, `process.exited`, and `file.{opened,created,modified,deleted,renamed}`. A collector emits only event types it actually observes.

Every event includes an ID, ISO-8601 timestamp, type, platform, collector name, process PID/optional parent/executable/argv, optional typed resource, metadata, and evidence (`observed`). File paths and process details are metadata and may be sensitive.

```json
{"id":"…","timestamp":"2026-10-06T12:00:00+00:00","type":"file.opened","platform":"linux","collector":"linux-kernel","process":{"pid":4218,"parent_pid":4000,"executable":"/usr/bin/editor","command":null},"resource":{"type":"file","path":"/workspace/src/main.py"},"metadata":{},"evidence":"observed"}
```

IDs default to random UUIDs. `Event.stable_id(collector, boot_id, sequence)` supplies deterministic IDs when a collector has a source boot identity and monotonically assigned event sequence. The Linux collector currently uses UUIDs; its event order and sequence do not promise replay-stable identities.

The event stream is bounded. A full queue drops the incoming event and increments `EventStream.dropped`; Linux collector health also counts drops. A `fanotify` `FAN_Q_OVERFLOW` increments its dropped counter. Consumers must inspect health and capabilities rather than interpret silence as proof that no activity happened.

`Capability` reports event type, state (`available`, `degraded`, `permission_denied`, `unavailable`, `unsupported`), reason, scope, and attribution source. The interface is common; the underlying coverage is platform-specific. `decode_event` rejects malformed or unknown event types with `ValueError`.

Native observations remain separate from interpretations. An open event does not prove contents were read. Process identity is a PID, not an application or agent identity. No consumer-specific concepts are part of this model.
