# HostLens Design Principles

HostLens exists to make native host telemetry easier for developer tools to consume without hiding the differences between operating systems.

These principles guide the event model, collectors, APIs, and future platform implementations.

## 1. Normalize the Interface, Not the Reality

HostLens should provide a common interface across platforms, but it must not pretend that every operating system provides the same observability capabilities.

A normalized event should preserve:

* what was observed
* where it was observed
* which process was involved
* which native collector produced it
* what the platform can guarantee
* what the platform cannot guarantee

Cross-platform compatibility means consumers can work with a consistent model, not that every platform produces identical evidence.

---

## 2. Observations Come Before Conclusions

HostLens records system events.

It should not automatically turn those events into claims about intent.

For example:

```text
Observed:
process 4821 opened /project/.env

Not automatically:
"the AI agent read the .env file"

```

A consumer may derive a conclusion from several observations, but that conclusion belongs to the consumer or a higher-level analysis layer.

This distinction is particularly important for security, auditing, and AI-agent tooling.

---

## 3. Never Manufacture Capabilities

If a platform cannot reliably provide a particular event, HostLens must not simulate it and present the result as equivalent evidence.

For example:

```text
Linux:
process-attributed file access available
```

does not mean:

```text
Windows:
process-attributed file access available in exactly the same way
```

Platform limitations should be exposed through capability information and documentation.

---

## 4. Native Collectors Own Platform Complexity

Platform-specific implementation details belong inside collectors.

The core should not contain large amounts of:

```text
if Linux
if Windows
if macOS
```

logic.

Instead:

```text
                 HostLens Core
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       Linux       Windows      macOS
      Collector   Collector    Collector
```

Each collector translates native telemetry into HostLens events.

This keeps the common layer stable while allowing platform implementations to evolve independently.

---

## 5. Preserve Native Evidence

Normalization must not destroy information that may be useful to consumers.

If the native platform provides information that does not map cleanly into the common event model, HostLens should have a mechanism for preserving relevant source-specific metadata.

The goal is:

```text
common fields
+
platform-specific evidence when available
```

rather than:

```text
common fields only
```

This allows higher-level tools to remain portable without making advanced platform-specific use cases impossible.

---

## 6. Capability Differences Are First-Class

Consumers should be able to determine what the current collector supports.

For example:

```json
{
  "platform": "linux",
  "capabilities": {
    "process_events": true,
    "file_events": true,
    "file_process_attribution": true,
    "network_events": false
  }
}
```

A consumer should not have to guess whether an event type is supported.

Capabilities may differ because of:

* operating system
* OS version
* collector implementation
* permissions
* runtime environment
* containerization
* unavailable native facilities

---

## 7. Loss and Uncertainty Must Be Visible

System telemetry is not guaranteed to be perfect.

Events may be lost because of:

* kernel or operating-system queue limits
* collector failures
* permission restrictions
* process lifetime
* unsupported environments
* resource pressure
* virtualization or container boundaries

HostLens should expose relevant loss or uncertainty rather than silently presenting incomplete telemetry as complete.

For example:

```text
event_loss_detected
collector_unavailable
permission_denied
capability_unavailable
```

The exact representation may evolve with the event model.

---

## 8. Local-First by Default

HostLens is intended to operate on the machine being observed.

The core design should not require:

* a cloud service
* an external database
* an account
* a hosted dashboard
* sending telemetry to a third party

A developer should be able to use HostLens locally and decide what happens to the resulting events.

Remote collection, forwarding, or storage may be built by consumers later.

---

## 9. Privacy Is a Design Constraint

Host-level events can expose sensitive information.

Depending on the collector and configuration, telemetry may contain:

* file paths
* process names
* command information
* network endpoints
* usernames
* application metadata

HostLens should therefore avoid collecting more information than necessary for the requested observation.

In particular, observing that a process interacted with a file does not require capturing the file's contents.

Consumers should also be able to control what event information is retained or forwarded.

---

## 10. Embeddable Before Dashboard-Oriented

HostLens is infrastructure.

The primary interface should be useful to software that wants to consume events programmatically.

Potential consumers include:

* developer tools
* security tools
* debugging utilities
* auditing software
* AI-agent tooling
* local observability applications
* testing infrastructure

A graphical interface may be useful later, but it is not the core product.

---

## 11. Streaming Is a First-Class Use Case

System events naturally occur over time.

HostLens should support consumers that want to process events as they happen rather than requiring periodic snapshots.

Conceptually:

```text
Native OS telemetry
        ↓
     Collector
        ↓
   HostLens Event
        ↓
   Event Stream
        ↓
      Consumer
```

This makes the same infrastructure useful for both interactive tools and long-running monitoring systems.

---

## 12. Keep Consumers Independent

HostLens should not be designed specifically around AgentTrace.

AgentTrace is an important early consumer, but the underlying system should remain useful without it.

The dependency should be:

```text
HostLens
   ↓
normalized host events
   ↓
AgentTrace
```

not:

```text
AgentTrace requirements
   ↓
HostLens architecture
```

This distinction is important if HostLens is going to become a reusable open-source project.

---

## 13. Agent Identity Belongs Above the Host Layer

HostLens should observe the host.

It should not be responsible for deciding whether a process belongs to:

* Claude Code
* Codex
* Gemini CLI
* another AI agent
* a developer's terminal
* an IDE

That attribution belongs to higher-level tools such as AgentTrace.

HostLens provides evidence such as:

```text
PID 4821
opened /project/.env
```

AgentTrace can then determine:

```text
PID 4821
↓
process tree
↓
Codex session
```

This keeps HostLens general-purpose.

---

## 14. APIs Should Prefer Explicitness

HostLens APIs should make important behavior visible.

Avoid APIs where consumers have to guess:

* what is being monitored
* which capabilities are active
* what permissions are required
* whether events can be lost
* whether an event is native or derived
* what platform-specific limitations exist

Configuration should favor explicit behavior over hidden magic.

---

## 15. The Core Should Stay Small

The common layer should contain only functionality that genuinely belongs across platforms.

Good candidates include:

* event types
* event structures
* timestamps
* process/resource identity
* capability representation
* event metadata
* collector interfaces
* event streaming
* serialization

Platform-specific implementation should remain outside the core whenever practical.

A small core makes it easier for contributors to implement new collectors without understanding the entire project.

---

## 16. Version the Event Model Carefully

The event model is effectively a contract between HostLens and its consumers.

Changes should therefore consider:

* backwards compatibility
* new event types
* new fields
* renamed fields
* removed fields
* platform-specific extensions
* serialization formats

A consumer should be able to determine which event-model version produced an event.

Breaking changes should be deliberate and documented.

---

## 17. Platform Support Means More Than Compilation

A collector should not be considered supported simply because the project compiles on an operating system.

Meaningful platform support requires understanding:

* what native telemetry is available
* what permissions are required
* what events can be observed
* what events cannot be observed
* attribution reliability
* event ordering
* event-loss behavior
* deployment restrictions
* environmental limitations

HostLens should document these boundaries explicitly.

---

## 18. Build the Reference Implementation Before Chasing Parity

HostLens should initially prioritize a platform where the required low-level telemetry can be implemented and tested properly.

Linux is the initial reference implementation because it provides strong low-level observability primitives suitable for developing and validating the event model.

The goal is not to declare Linux the "best" platform.

The goal is to establish a concrete implementation against which the common model can be tested before expanding to other operating systems.

---

## 19. Research Is Part of the Project

Some platform capabilities cannot be responsibly implemented from assumptions or high-level documentation alone.

For each collector, HostLens should document:

* native API being used
* permissions required
* supported event types
* known limitations
* event-loss behavior
* attribution behavior
* deployment constraints
* relevant OS versions

Platform research should therefore be treated as a first-class contribution.

---

## 20. Prefer Evidence Over Convenience

When there is a choice between:

```text
easy but ambiguous
```

and:

```text
more difficult but demonstrably correct
```

HostLens should prefer the latter for its core observation layer.

The project is intended to become infrastructure for tools that may make security, debugging, or auditing decisions from its events.

Trust in the underlying evidence matters more than having the largest feature list.

---

## Guiding Principle

The central rule for HostLens is:

> **Give developers a consistent interface to native host events without pretending the underlying operating systems are identical.**

Everything else should follow from that principle.
