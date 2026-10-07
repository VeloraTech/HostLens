# Architecture

NativeRelay separates the event contract from OS-specific collection.

```text
Operating system
        ↓
Platform collector (Linux reference; macOS and Windows future)
        ↓
NativeRelay normalized Event / bounded EventStream
        ↓
Consumer
```

Linux uses CN_PROC and fanotify; the core event, capability, and stream contract has no Linux-specific imports. macOS and Windows collectors remain future implementations.

The `nativerelay` package owns event types, validation/serialization, capability states, a collector contract, and a bounded in-process stream. It imports no Linux APIs. `collectors/linux` owns the kernel mechanisms, `/proc` metadata lookup, path scoping, and Linux health reporting. macOS and Windows can implement the same collector contract later without making the core depend on platform APIs.

This architecture normalizes the interface, not the underlying guarantees. A consumer inspects capabilities and collector status; unsupported telemetry is never represented as an empty stream. Linux event semantics and limitations are recorded in [Linux support](linux-support.md).

The current scope is a directory selected by the caller. Process lifecycle events are host-visible kernel notifications, subject to kernel policy and event loss. File events use a mount mark filtered to that directory. The local event stream is bounded and does not persist events. JSON is a serialization/debug format, not a trusted or tamper-proof ledger.

NativeRelay reports observations only. Process IDs are not application identities; file opens are not proof that file data was read. Higher-level identity or interpretation remains the responsibility of a consumer. NativeRelay has no AgentTrace dependency or integration logic.
