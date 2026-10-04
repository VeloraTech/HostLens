# NativeRelay Architecture

NativeRelay is designed as a layered system:

```text
┌─────────────────────────────────────────────┐
│              Consumer Application           │
│                                             │
│  AgentTrace · IDEs · Security Tools · etc. │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                  NativeRelay Core               │
│                                             │
│  Event Model · Normalization · Capabilities │
└──────────────────────┬──────────────────────┘
                       │
              Native Event Adapters
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│   Linux    │  │  Windows   │  │   macOS    │
│ Collector  │  │ Collector  │  │ Collector  │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      ▼               ▼               ▼
 Native OS        Native OS        Native OS
 telemetry        telemetry        telemetry
```

The central architectural rule is:

> **Collectors understand operating systems. Core understands events. Applications understand meaning.**

---

## 1. Core

The NativeRelay core should remain as platform-independent as possible.

Its responsibilities include:

* defining the event model
* validating events
* normalizing platform-specific data
* exposing capabilities
* providing a common API to consumers
* handling event streams
* defining versioning and compatibility rules

The core should **not** contain operating-system-specific collection logic.

For example, the core should understand an event such as:

```json
{
  "type": "file.access",
  "operation": "open",
  "pid": 4821,
  "path": "/workspace/.env",
  "platform": "linux"
}
```

It should not need to know which Linux API produced that event.

---

## 2. Collectors

Collectors are responsible for obtaining native telemetry from the host operating system.

A collector:

1. connects to a native telemetry mechanism
2. receives an operating-system event
3. extracts the relevant information
4. converts it into the NativeRelay event model
5. reports capability or collection limitations

Conceptually:

```text
Native OS event
      │
      ▼
┌──────────────┐
│   Collector  │
└──────┬───────┘
       │
       ▼
NativeRelay event
```

Collectors should not reinterpret events beyond what is necessary to normalize them.

---

## 3. Platform isolation

Platform-specific code should be isolated behind collector interfaces.

A consumer should be able to use:

```text
NativeRelay API
```

without directly depending on:

```text
Linux APIs
Windows APIs
macOS APIs
```

This allows the same application to consume NativeRelay events while the underlying collection mechanism changes by platform.

The abstraction should not erase meaningful platform differences.

---

## 4. Capability model

Not every platform can provide every event with the same reliability or permissions.

NativeRelay therefore treats capabilities as part of the API.

A consumer should be able to ask:

```text
What can this host observe?
```

rather than assuming:

```text
Every NativeRelay installation supports every event.
```

Conceptually:

```json
{
  "platform": "linux",
  "capabilities": {
    "process": true,
    "file_access": true,
    "network": false
  }
}
```

The actual capability schema will be defined separately in the event-model and platform-support specifications.

### Why this matters

A common abstraction becomes dangerous when it hides unsupported behavior.

NativeRelay should prefer:

```text
unsupported
```

over silently returning:

```text
no events
```

when the platform cannot actually provide the requested telemetry.

---

## 5. Event normalization

Operating systems describe similar activity differently.

NativeRelay translates those native representations into common event types.

For example:

```text
Linux native event
        │
        ▼
Linux Collector
        │
        ▼
FileOpened
        │
        ▼
Consumer
```

and:

```text
Windows native event
        │
        ▼
Windows Collector
        │
        ▼
FileOpened
        │
        ▼
Consumer
```

The consumer should not need to understand the underlying API simply to consume the event.

However, the event should retain platform/source information where that information is useful.

---

## 6. Event lifecycle

The intended flow is:

```text
┌──────────────┐
│ Native Event │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Collector  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Normalization│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ NativeRelay     │
│ Event Stream  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Consumer      │
└──────────────┘
```

The consumer may then:

* display the event
* correlate it with another event
* persist it
* build an activity timeline
* derive higher-level information
* trigger an action

NativeRelay itself should avoid making application-specific conclusions.

---

## 7. Evidence boundaries

NativeRelay distinguishes between three levels of information.

### Observed

Information directly provided by the underlying telemetry source.

```text
process 4821 opened /workspace/.env
```

### Derived

Information calculated from observed events.

```text
process 4821 is a child of process 4102
```

### Interpretation

A conclusion made by a consuming application.

```text
Agent X accessed credentials.
```

NativeRelay should primarily provide **observed evidence** and, where appropriate, well-defined derived information.

Interpretation belongs to the consumer.

This makes the system more useful for debugging, security, and forensic applications where incorrect assumptions can be more harmful than missing conclusions.

---

## 8. Process attribution

Process attribution is an important part of NativeRelay.

A useful event should provide enough process context for consumers to correlate activity.

For example:

```text
ProcessStarted
      │
      ▼
PID 4821
      │
      ├── FileOpened
      ├── FileWritten
      └── ProcessExited
```

Where the underlying platform supports it, NativeRelay should preserve information such as:

* process ID
* parent process ID
* process name
* executable
* process start time
* event timestamp

The exact process metadata exposed will depend on the event model and platform capabilities.

---

## 9. File events

Filesystem change notifications and process-attributed file access are different problems.

For example:

```text
FileChanged
```

does not necessarily tell a consumer:

```text
which process caused the change?
```

Likewise:

```text
FileOpened
```

does not automatically mean:

```text
file contents were read
```

NativeRelay should preserve these distinctions.

Possible file event categories include:

```text
FileOpened
FileRead
FileWritten
FileCreated
FileDeleted
FileRenamed
```

The actual availability of each event depends on the platform collector.

NativeRelay should not manufacture a stronger event from a weaker observation.

---

## 10. Network events

Network telemetry is intentionally outside the initial implementation.

The architecture should nevertheless allow future event families such as:

```text
NetworkConnectionStarted
NetworkConnectionClosed
```

without requiring changes to the fundamental collector architecture.

Network events should only be added once their platform-specific semantics and capability requirements are properly understood.

---

## 11. Local-first architecture

NativeRelay does not require a remote service.

The intended architecture is:

```text
Operating System
       │
       ▼
   NativeRelay
       │
       ▼
Local Application
```

No cloud component is required for collection or normalization.

A consuming application may choose to transmit events elsewhere, but that decision belongs to the application.

This separation keeps NativeRelay useful for:

* local developer tools
* debugging
* security tooling
* offline environments
* privacy-sensitive applications

---

## 12. Privacy boundaries

NativeRelay should collect the minimum information necessary for the requested event.

For example:

```text
FileOpened
path=/workspace/.env
pid=4821
```

does not require:

```text
contents of /workspace/.env
```

Likewise, observing a process does not automatically require permanently storing every command argument or environment variable associated with it.

Sensitive information should only be collected when explicitly required by a supported feature and should have clear configuration and documentation.

---

## 13. Consumer model

NativeRelay is intended to be useful both as a library and as a standalone developer tool.

Conceptually:

```text
                 NativeRelay
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
     Library                  CLI
        │                       │
        ▼                       ▼
Developer application      Human inspection
```

The library is the primary architectural boundary.

The CLI should consume the same core interfaces exposed to other applications rather than becoming a separate implementation.

---

## 14. AgentTrace integration

AgentTrace is one of the motivating use cases for NativeRelay.

Today, AgentTrace has to reason about:

```text
AI agent
   ↓
process tree
   ↓
workspace activity
```

NativeRelay can eventually provide:

```text
NativeRelay
   ↓
native process/file events
   ↓
AgentTrace
   ↓
agent attribution
```

AgentTrace can then focus on its actual domain:

* identifying AI coding agents
* maintaining agent sessions
* correlating process trees
* associating activity with workspaces
* building evidence timelines

NativeRelay remains responsible for host-level observation.

This separation allows both projects to evolve independently.

---

## 15. What the architecture deliberately avoids

NativeRelay should avoid becoming a large abstraction layer that attempts to expose every operating-system feature.

The project should not initially attempt to normalize:

* every filesystem operation
* every process attribute
* every network protocol
* kernel metrics
* hardware sensors
* GPU telemetry
* system performance counters
* application logs

The common event model should grow only when there is a clear use case and a defensible cross-platform representation.

---

## 16. Architectural goals

The architecture should eventually provide:

```text
              Native OS Telemetry
                       │
                       ▼
               ┌──────────────┐
               │   NativeRelay   │
               │              │
               │ Common Model │
               └──────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       AgentTrace   Debugger   Security Tool
```

The success criterion is not:

> "NativeRelay supports every operating system feature."

The success criterion is:

> **A developer tool can consume useful host-level evidence without implementing an independent telemetry stack for every operating system.**

---

## Open design questions

The following decisions remain intentionally open:

* What should the minimum event schema contain?
* How should event loss be represented?
* How should collector confidence be represented?
* How should permissions be exposed to consumers?
* Which events should be guaranteed across platforms?
* Which events should remain platform-specific?
* How should backpressure be handled?
* Should NativeRelay provide persistence or only streaming?
* How should collectors be loaded and selected?
* What should the stable public API look like?

These questions should be resolved through implementation experience and discussion rather than prematurely fixed.

---

## Current implementation strategy

The initial implementation will use **Linux as the reference platform**.

The first goal is to prove that the following pipeline works reliably:

```text
Linux native telemetry
        ↓
NativeRelay collector
        ↓
normalized events
        ↓
NativeRelay API
        ↓
consumer
```

Once the event model and core interfaces have been tested against a real collector, the project can evaluate how the same abstractions map to Windows and macOS.

This prevents the project from designing a theoretical cross-platform API before understanding what real native telemetry looks like.

---

## Related documentation

* [Event Model](event-model.md)
* [Platform Support](platform-support.md)
* [Design Principles](design-principles.md)
* [Roadmap](../ROADMAP.md)
* [Contributing](../CONTRIBUTING.md)
