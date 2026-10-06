# Contributing to NativeRelay

Thanks for your interest in NativeRelay.

NativeRelay is an open-source project exploring a common event layer over native operating-system telemetry for developer tools.

The project is still early, so contributions that improve the design, research, documentation, and platform understanding are just as valuable as implementation work.

## What We Need Help With

NativeRelay has an initial Linux implementation. Linux integration verification and collector reliability are current priorities; macOS and Windows remain future collectors.

### Linux

* CN_PROC and fanotify live integration testing
* Kernel permission and coverage research
* Process connector loss reporting
* fanotify path and event handling review
* Reliable create/delete/rename telemetry research

### Windows

* ETW research
* File I/O providers
* Process attribution
* Event correlation
* Permission requirements
* Collector design
* Testing across Windows versions

### macOS

* Endpoint Security research
* Process events
* File events
* Entitlements and permissions
* Deployment requirements
* Collector design
* Testing across supported macOS versions

### Core

* Event-model design
* Capability representation
* Collector interfaces
* Serialization
* Event streaming
* API design
* Cross-platform normalization

### Tooling

* CLI development
* Testing infrastructure
* Examples
* Documentation
* Developer experience

---

## Research Contributions Are Welcome

You do not need to implement a collector to contribute.

If you know a platform's native telemetry system, a useful contribution might simply answer:

* What events can it actually observe?
* Can events be attributed to a process?
* What permissions are required?
* What information is available?
* What information is unavailable?
* Can events be lost?
* How are events correlated?
* What operating-system versions are supported?
* What deployment restrictions exist?

Please include links to authoritative documentation or reproducible experiments where possible.

Research should distinguish between:

```text
Documented capability
Observed behavior
Inference
```

This is important because NativeRelay is intended to represent actual evidence rather than assumptions.

---

## Before Starting a Large Change

For significant architectural or platform changes, open a discussion or issue first.

This is especially useful for:

* new event families
* changes to the common event model
* new platform collectors
* breaking API changes
* new dependencies
* changes to privacy behavior
* changes that affect multiple collectors

Small fixes and documentation improvements generally do not need prior discussion.

---

## Development Principles

Contributions should follow the project's design principles.

In particular:

### Do not hide platform differences

If a platform cannot provide equivalent telemetry, expose that limitation.

### Do not turn observations into conclusions

A collector should report what the operating system tells us.

Higher-level interpretation belongs to consuming applications.

### Keep platform-specific code isolated

Native APIs and platform-specific behavior should remain inside the relevant collector whenever practical.

### Avoid unnecessary collection

Do not collect file contents or other sensitive information when the observation does not require it.

### Prefer tested behavior

A collector should not claim support for an event simply because the underlying API appears capable of producing it.

---

## Project Structure

The repository is organized around these implementation areas:

```text
NativeRelay/
├── docs/
│   ├── architecture.md
│   ├── event-model.md
│   ├── platform-support.md
│   └── design-principles.md
├── nativerelay/
│   ├── model.py
│   ├── collector.py
│   ├── stream.py
│   └── cli.py
├── collectors/
│   └── linux/
├── tests/
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── CONTRIBUTING.md
└── LICENSE
```

The implementation structure may change as the project develops.

---

## Pull Requests

A good pull request should explain:

1. What changed.
2. Why it changed.
3. Which platform or component it affects.
4. How it was tested.
5. Any limitations that remain.

For platform-specific changes, include the relevant OS version and environment where practical.

For example:

```text
Platform: Linux
Kernel: 6.x
Collector: fanotify
Test environment: local development machine
```

---

## Tests

Changes should include appropriate tests where practical.

At minimum, contributors should test:

* event construction
* normalization
* capability reporting
* error handling
* collector behavior
* platform-specific edge cases

Platform collectors should also include integration tests where the environment allows them.

---

## Documentation

Documentation is part of the implementation.

If a change introduces:

* a new event
* a new capability
* a new platform behavior
* a permission requirement
* a limitation
* a new API

update the relevant documentation with the change.

Do not rely on the implementation alone to communicate platform behavior.

---

## Commit Messages

Use clear commit messages that describe the change.

Examples:

```text
feat: add linux file collector
fix: preserve process attribution
docs: clarify fanotify limitations
test: add file event normalization tests
refactor: isolate collector interface
```

The exact convention may evolve as the project grows.

---

## Opening an Issue

When reporting a bug, include:

* operating system
* OS version
* NativeRelay version or commit
* collector being used
* reproduction steps
* expected behavior
* actual behavior
* relevant logs or events

Avoid including sensitive file paths, credentials, tokens, or private system information.

---

## Security Issues

Do not publicly disclose a suspected security vulnerability before it has been reviewed.

See `SECURITY.md` for the project's security-reporting process.

---

## Good First Contributions

If you are new to the project, useful starting points include:

* improving documentation
* testing existing behavior
* researching a platform API
* adding examples
* improving error messages
* adding event-model tests
* reproducing platform-specific behavior
* improving the CLI

You do not need to understand the entire codebase before contributing.

---

## Platform Experts

NativeRelay particularly welcomes contributors familiar with:

* Linux kernel interfaces
* eBPF
* `fanotify`
* Windows ETW
* Windows internals
* macOS Endpoint Security
* Rust systems programming
* security telemetry
* observability infrastructure

If you understand one of these areas deeply, your platform knowledge may be more valuable than a large code contribution.

---

## Questions and Discussions

Use GitHub Discussions for questions, architectural proposals, platform research, and ideas that would benefit from community input.

Issues should generally be used for concrete bugs and actionable implementation work.

---

## License

By contributing to NativeRelay, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).
