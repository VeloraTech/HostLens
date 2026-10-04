# HostLens Event Model

The HostLens event model defines the common representation used to describe observable activity on a host.

The purpose of the model is not to make every operating system behave identically.

It is to provide a consistent structure for events while preserving information about:

* what happened
* where it happened
* which process was involved
* when it happened
* which platform produced the observation
* where the observation came from
* how confident the collector can be about the observation

---

## 1. Event structure

A HostLens event is conceptually structured around:

```text
Event
├── identity
├── type
├── timestamp
├── process
├── resource
├── platform
├── source
└── evidence
```

A simplified example:

```json
{
  "id": "evt_01J...",
  "type": "file.access",
  "timestamp": "2026-10-04T12:30:14.421Z",

  "process": {
    "pid": 4821,
    "name": "node"
  },

  "resource": {
    "path": "/workspace/.env"
  },

  "platform": "linux",
  "source": "native",
  "confidence": "observed"
}
```

The exact schema is not yet considered stable.

---

# 2. Event identity

Each event should have an identifier suitable for correlation.

Example:

```json
{
  "id": "evt_01J..."
}
```

The identifier should allow consumers to distinguish two events that happen to contain otherwise identical information.

Event IDs should not be treated as globally meaningful outside the HostLens context unless the final specification explicitly guarantees that property.

---

# 3. Event type

The `type` field identifies the general category of the event.

Examples:

```text
process.start
process.exit

file.access
file.create
file.write
file.delete
file.rename

network.connect
network.close

command.execute
```

Event types should describe **observable activity**, not interpretations.

Prefer:

```text
file.access
```

over:

```text
secret.accessed
```

The latter assumes meaning that may not be known from the underlying observation.

---

# 4. Timestamp

Every event should contain a timestamp.

Example:

```json
{
  "timestamp": "2026-10-04T12:30:14.421Z"
}
```

The timestamp represents when the underlying collector considers the event to have occurred.

Collectors should document any limitations around timestamp precision or ordering.

Consumers should not automatically assume that receiving events in a particular order means that the underlying operations occurred in exactly that order.

---

# 5. Process context

Where available, events should identify the process associated with the observation.

Example:

```json
{
  "process": {
    "pid": 4821,
    "parent_pid": 4700,
    "name": "node",
    "executable": "/usr/bin/node"
  }
}
```

The minimum process information will depend on the event and platform.

Potential fields include:

```text
pid
parent_pid
name
executable
start_time
```

Process information should only be included when it can be obtained reliably.

---

# 6. Resource context

Events involving a host resource should expose that resource in a structured form.

For file events:

```json
{
  "resource": {
    "type": "file",
    "path": "/workspace/src/index.js"
  }
}
```

For network events, a future representation could contain:

```json
{
  "resource": {
    "type": "network",
    "address": "example.com",
    "port": 443
  }
}
```

The resource schema will evolve as additional event families are introduced.

---

# 7. Platform information

Every normalized event should retain information about the platform that produced it.

Example:

```json
{
  "platform": "linux"
}
```

Possible values include:

```text
linux
windows
macos
```

This matters because two events with the same normalized type may have different underlying guarantees.

Consumers should be able to inspect the platform when platform-specific behavior matters.

---

# 8. Source information

HostLens should preserve information about how an event was obtained.

Example:

```json
{
  "source": "native"
}
```

The source field may eventually distinguish between mechanisms such as:

```text
native
kernel
userspace
polling
```

The final vocabulary should be defined once real collectors exist.

The purpose is to prevent consumers from treating every event as though it has identical provenance.

---

# 9. Evidence and confidence

HostLens distinguishes evidence from interpretation.

A collector may know that an operation occurred without knowing everything about it.

For example:

```text
Observed:
PID 4821 opened /workspace/.env
```

That does not automatically establish:

```text
PID 4821 read the contents of /workspace/.env
```

Therefore events may contain evidence metadata.

Conceptually:

```json
{
  "confidence": "observed"
}
```

Possible future values could include:

```text
observed
derived
```

The final vocabulary should be kept small.

The project should avoid creating a complicated confidence scale unless implementation experience demonstrates a need for one.

---

# 10. Event families

HostLens is expected to organize events into a small number of families.

## Process

Examples:

```text
process.start
process.exit
```

These describe process lifecycle events.

---

## File

Examples:

```text
file.access
file.create
file.write
file.delete
file.rename
```

These describe filesystem activity.

Importantly:

```text
file.write
```

does not imply:

```text
file.access
```

unless the underlying collector actually observed both.

Similarly:

```text
file.access
```

should not automatically be interpreted as reading file contents.

---

## Network

Potential future events:

```text
network.connect
network.close
```

Network monitoring is not part of the initial implementation.

---

## Command

Potential future event:

```text
command.execute
```

The exact meaning and privacy implications of command execution events need to be defined before implementation.

---

# 11. Example events

### Process start

```json
{
  "type": "process.start",
  "timestamp": "2026-10-04T12:30:10.120Z",
  "process": {
    "pid": 4821,
    "parent_pid": 4700,
    "name": "node"
  },
  "platform": "linux",
  "source": "native",
  "confidence": "observed"
}
```

### File access

```json
{
  "type": "file.access",
  "timestamp": "2026-10-04T12:30:14.421Z",
  "process": {
    "pid": 4821,
    "name": "node"
  },
  "resource": {
    "type": "file",
    "path": "/workspace/.env"
  },
  "platform": "linux",
  "source": "native",
  "confidence": "observed"
}
```

### File creation

```json
{
  "type": "file.create",
  "timestamp": "2026-10-04T12:31:01.812Z",
  "process": {
    "pid": 4821,
    "name": "node"
  },
  "resource": {
    "type": "file",
    "path": "/workspace/output.json"
  },
  "platform": "linux",
  "source": "native",
  "confidence": "observed"
}
```

---

# 12. Observed vs derived information

HostLens should make a clear distinction between observations and information calculated from those observations.

### Observed

```text
process 4821 opened file X
```

### Derived

```text
process 4821 is a descendant of process 4700
```

### Interpretation

```text
AI agent accessed sensitive information
```

The first category comes directly from telemetry.

The second can be generated by HostLens when the derivation is deterministic and well-defined.

The third belongs to consuming applications.

---

# 13. Event loss

System telemetry can be lost.

Possible causes include:

* collector limitations
* permission restrictions
* event queue overflow
* process termination
* unsupported filesystem or environment
* operating-system limitations

HostLens should not silently present an incomplete stream as complete.

The event model therefore needs a mechanism for communicating collection gaps.

A future representation could look like:

```json
{
  "type": "collector.gap",
  "reason": "buffer_overflow",
  "timestamp": "2026-10-04T12:32:00.000Z"
}
```

The exact representation is intentionally not finalized.

---

# 14. Capability information

Event availability should be discoverable before applications depend on it.

Conceptually:

```json
{
  "platform": "linux",
  "capabilities": {
    "process.start": true,
    "process.exit": true,
    "file.access": true,
    "file.write": true,
    "network.connect": false
  }
}
```

Capabilities should describe what the active collector can provide.

This prevents applications from confusing:

```text
no event observed
```

with:

```text
the platform cannot provide this event
```

---

# 15. Privacy

The event model should avoid unnecessarily carrying sensitive data.

For example, a file-access event should normally contain:

```text
path
process
timestamp
```

rather than:

```text
file contents
environment variables
credentials
cookies
request bodies
```

HostLens observes host activity.

It does not need to capture application data to fulfill that purpose.

Sensitive fields should be introduced only when there is a clear use case and an explicit design for controlling them.

---

# 16. Streaming

HostLens is primarily intended to expose events as a stream.

Conceptually:

```text
Collector
   │
   ├── Event
   ├── Event
   ├── Event
   ├── Event
   └── ...
        │
        ▼
     Consumer
```

Consumers should be able to process events as they arrive without requiring HostLens to persist an entire history.

Persistence and replay may be added later, but they should remain separate concerns from the core event model.

---

# 17. Versioning

The event schema will eventually need explicit versioning.

A schema change can affect:

* event fields
* event types
* capability names
* collector guarantees
* consumer compatibility

The project should therefore avoid treating the initial schema as permanently stable.

Until the first stable release, breaking changes are expected.

Once a stable API is introduced, compatibility rules should be documented here.

---

# 18. Design rules

The event model follows several rules.

### Rule 1 — Describe events, not intentions

Use:

```text
file.access
```

not:

```text
agent.stole_secret
```

### Rule 2 — Do not strengthen evidence

If a collector observes a file open, do not report a file-content read unless that was actually observed.

### Rule 3 — Preserve provenance

Consumers should be able to determine where an event came from.

### Rule 4 — Preserve platform differences

Normalization must not hide meaningful limitations of the underlying platform.

### Rule 5 — Keep the model small

New event types and fields should have a concrete use case.

### Rule 6 — Prefer explicit gaps

If telemetry was lost or unavailable, communicate that rather than implying complete coverage.

---

# Status

This document describes the **proposed event model**.

It is not yet a stable public API.

The schema will be refined alongside the first Linux collector so that the abstraction reflects real operating-system telemetry rather than a purely theoretical model.
