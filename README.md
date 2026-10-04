# HostLens

> An open-source host event layer that normalizes native OS telemetry into a common event model for developer tools.

[![Status: Early Development](https://img.shields.io/badge/status-early%20development-orange)](ROADMAP.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

HostLens is an open-source infrastructure project for observing host-level activity and exposing it through a consistent event model.

The goal is to make system-level telemetry reusable instead of forcing every developer tool to build its own platform-specific implementation.

```text
Developer Tool
      │
      ▼
   HostLens
      │
      ▼
Normalized Events
      │
 ┌────┼────┐
 ▼    ▼    ▼
Linux Win  macOS
```

## Why?

A filesystem watcher can tell you:

```text
file changed
```

But many applications need to know:

```text
which process opened the file?
which process created it?
which process modified it?
what happened before and after?
```

Different operating systems expose this information through different native mechanisms.

HostLens explores a common layer for consuming those events without pretending that every platform provides identical capabilities.

## Core idea

HostLens separates **native collection** from a **common event model**.

```json
{
  "type": "file.access",
  "operation": "open",
  "path": "/workspace/.env",
  "pid": 4821,
  "platform": "linux",
  "confidence": "observed"
}
```

The underlying platform remains responsible for what can actually be observed.

HostLens normalizes the result.

**Observed evidence is kept separate from interpretation.**

## Current direction

HostLens is intentionally starting small.

| Capability               | Status       |
| ------------------------ | ------------ |
| Common event model       | Designing |
| Linux process events     | Planned   |
| Linux file-access events | Planned   |
| Process attribution      | Planned   |
| Embeddable API           | Planned   |
| Windows                  | Research     |
| macOS                    | Research     |
| Network events           | Later        |

Linux is the initial reference platform because it provides strong low-level observability primitives for the first implementation.

Cross-platform support will be added without claiming equivalent coverage where the underlying OS cannot provide it.

## AgentTrace

HostLens originated from a problem encountered while building [AgentTrace](https://github.com/VeloraTech/AgentTrace).

AgentTrace needs to understand activity performed by AI coding agents and their processes. Rather than making AgentTrace responsible for implementing native system telemetry for every operating system, HostLens explores whether that capability can become reusable infrastructure.

```text
HostLens
   │
   │ normalized host events
   ▼
AgentTrace
   │
   ├── agent identity
   ├── process trees
   ├── sessions
   └── activity timeline
```

AgentTrace is one potential consumer of HostLens.

It is not the only intended one.

## Design principles

* **Native underneath** — use the capabilities of each operating system.
* **Normalized above** — provide a consistent event model.
* **Evidence first** — distinguish observations from conclusions.
* **Local-first** — no cloud service required.
* **Capability-aware** — unsupported telemetry should be explicit.
* **Embeddable** — useful as a library, not only a CLI.

More detail:

* [Architecture](docs/architecture.md)
* [Event Model](docs/event-model.md)
* [Platform Support](docs/platform-support.md)
* [Design Principles](docs/design-principles.md)
* [Roadmap](ROADMAP.md)
* [Contributing](CONTRIBUTING.md)

## Status

HostLens is **early-stage and open for collaboration**.

The hardest part is not collecting one more system event.

It is designing a useful abstraction across operating systems without hiding the limitations of the underlying platform.

If you work with operating-system internals, observability, security, developer tooling, or native systems programming, contributions and technical feedback are welcome.

## License

MIT
