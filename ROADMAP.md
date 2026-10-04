# HostLens Roadmap

HostLens is being developed incrementally.

The first goal is not to support every operating system or every type of host telemetry. The goal is to establish a reliable event model and a working native collector that can prove the architecture.

## Phase 0 — Foundation

**Status: Current**

Establish the project structure and define the contracts that future implementations will follow.

### Goals

* [x] Define project scope
* [x] Define architectural boundaries
* [x] Define the common event model
* [x] Document platform differences
* [x] Define design principles
* [ ] Establish core API
* [ ] Establish event serialization format
* [ ] Define collector interface
* [ ] Define capability representation
* [ ] Add initial automated tests

### Outcome

HostLens has a stable enough foundation for implementation to begin without prematurely locking the project into one operating system's design.

---

## Phase 1 — Linux Reference Collector

**Status: Planned**

Build the first real collector using Linux native telemetry.

### Initial scope

Process and file activity.

The collector should be capable of producing normalized events for supported operations such as:

* process activity
* file access
* file creation
* file modification
* file deletion
* file movement
* file close events
* process attribution where available

### Goals

* [ ] Implement Linux collector
* [ ] Connect collector to the common event model
* [ ] Implement process attribution
* [ ] Implement file events
* [ ] Implement capability reporting
* [ ] Handle collector permissions
* [ ] Detect and represent event loss
* [ ] Add collector-level tests
* [ ] Add integration tests
* [ ] Document required permissions
* [ ] Document known limitations

### Outcome

A real Linux system can produce HostLens events that applications can consume without directly interacting with Linux-specific telemetry APIs.

---

## Phase 2 — Developer API

**Status: Planned**

Make HostLens practical for other software to consume.

### Goals

* [ ] Define stable programmatic API
* [ ] Support event subscriptions
* [ ] Support filtering
* [ ] Support capability discovery
* [ ] Support graceful collector shutdown
* [ ] Define error handling
* [ ] Define lifecycle behavior
* [ ] Provide examples for embedding HostLens
* [ ] Add API documentation

### Outcome

A developer can integrate HostLens into another application without needing to understand the underlying operating-system collector.

---

## Phase 3 — CLI

**Status: Planned**

Provide a small command-line interface for inspecting HostLens directly.

Possible usage:

```text
hostlens run
hostlens events
hostlens capabilities
hostlens doctor
```

The exact command structure is intentionally not locked yet.

### Goals

* [ ] Add CLI
* [ ] Display normalized events
* [ ] Display active capabilities
* [ ] Display collector status
* [ ] Provide machine-readable output
* [ ] Provide useful diagnostics
* [ ] Document CLI usage

The CLI should be useful for development and debugging without turning HostLens into a full system-monitoring dashboard.

---

## Phase 4 — Windows Collector

**Status: Research**

Investigate Windows-native telemetry before committing to an implementation.

### Research areas

* ETW providers
* file I/O events
* process attribution
* event correlation
* permissions
* event ordering
* event loss
* supported Windows versions
* deployment requirements

### Goals

* [ ] Document viable Windows telemetry sources
* [ ] Define collector architecture
* [ ] Implement initial process events
* [ ] Implement initial file events
* [ ] Map native events into HostLens events
* [ ] Document capability differences
* [ ] Add Windows integration tests

### Outcome

Windows applications can consume HostLens events through a native collector while retaining the limitations and semantics of Windows telemetry.

---

## Phase 5 — macOS Collector

**Status: Research**

Investigate Apple's Endpoint Security framework and the requirements for distributing and operating a native collector.

### Research areas

* Endpoint Security events
* process events
* file events
* permissions
* entitlements
* deployment restrictions
* event ordering
* event-loss behavior
* supported macOS versions

### Goals

* [ ] Document Endpoint Security requirements
* [ ] Define collector architecture
* [ ] Implement initial process events
* [ ] Implement initial file events
* [ ] Map native events into HostLens events
* [ ] Document capability differences
* [ ] Add macOS integration tests

### Outcome

macOS applications can consume HostLens events through a native collector where the required system permissions and deployment conditions are satisfied.

---

## Phase 6 — Cross-Platform Stabilization

**Status: Future**

Once multiple collectors exist, test whether the common event model is actually holding up.

### Goals

* [ ] Compare equivalent events across platforms
* [ ] Identify gaps in the common model
* [ ] Refine capability reporting
* [ ] Improve event normalization
* [ ] Document semantic differences
* [ ] Test event ordering
* [ ] Test event-loss behavior
* [ ] Test permission failures
* [ ] Test restricted environments
* [ ] Establish compatibility policy

The objective is not identical output.

The objective is predictable behavior with clearly documented differences.

---

## Phase 7 — Additional Event Families

**Status: Future**

Only after process and file telemetry are reliable should HostLens expand into additional system events.

Potential areas include:

* network connections
* command execution
* sockets
* process resource information
* other host-level telemetry

Each event family should go through the same process:

```text
Native capability
      ↓
Research
      ↓
Event-model design
      ↓
Collector implementation
      ↓
Capability mapping
      ↓
Integration tests
      ↓
Documentation
```

New event families should not be added simply to increase the feature list.

---

## Phase 8 — Consumer Ecosystem

**Status: Future**

HostLens becomes more valuable as other tools begin consuming it.

Potential consumers include:

* AgentTrace
* security tools
* developer debugging tools
* local auditing utilities
* AI-agent monitoring
* testing tools
* developer environment tooling

### Goals

* [ ] Publish integration examples
* [ ] Document consumer patterns
* [ ] Support third-party collectors where appropriate
* [ ] Encourage external integrations
* [ ] Collect feedback from real consumers

AgentTrace is expected to be one of the first serious consumers, but HostLens should remain independent of it.

---

# What We Are Not Building Yet

HostLens is intentionally not starting as:

* a full system-monitoring dashboard
* a cloud observability platform
* a SIEM
* an endpoint security product
* an AI-agent tracker
* a hosted telemetry service
* a replacement for OS-native observability tools

These may be built by other projects using HostLens.

---

# Milestone Philosophy

A phase is not complete because the code compiles.

A meaningful milestone should have:

1. A working implementation.
2. Tests covering the important behavior.
3. Documented platform requirements.
4. Documented limitations.
5. A clear event contract.
6. Evidence that the implementation matches the documented behavior.

For platform collectors specifically:

> **Supported means observable, tested, documented, and honest about limitations.**

---

# Current Priority

The immediate sequence is:

```text
Foundation
    ↓
Linux collector
    ↓
Developer API
    ↓
CLI
    ↓
Windows research
    ↓
macOS research
    ↓
Cross-platform stabilization
    ↓
Additional event families
    ↓
Consumer ecosystem
```

The roadmap is deliberately conservative.

HostLens should earn broader platform and event coverage through working implementations rather than promising parity in advance.
