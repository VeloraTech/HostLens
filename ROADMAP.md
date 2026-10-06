# NativeRelay roadmap

## Phase 0 — Repository and design foundation: complete

Project scope, design principles, initial event model, and platform research were documented.

## Phase 1 — Linux reference implementation: initial implementation

- [x] Platform-neutral event model and JSON serialization
- [x] Collector contract, capability states, and bounded in-process stream
- [x] Linux process fork/exit collector using CN_PROC
- [x] Linux file open/write-close collector using fanotify
- [x] Caller-selected directory scope and health reporting
- [x] Developer CLI and local JSON output
- [x] Core/decoder tests and implementation-limit documentation
- [ ] Linux-host integration verification across supported kernels
- [ ] Improve connector overflow/loss detection

This implementation is pre-release and has not yet been validated on a Linux host in the current development environment. It supports process start/exit and best-effort file open/modified events. File create/delete/rename are unsupported.

## Phase 2 — Linux reliability and consumer API

- Exercise process connector and fanotify on real Linux kernels and permission profiles.
- Add live integration tests using controlled temporary processes/files.
- Detect process connector loss where the kernel interface permits it; define a clear gap event/health contract.
- Review fanotify descriptor handling, namespace/filesystem coverage, and shutdown behavior.
- Stabilize event/capability versioning and stream cancellation/subscription ergonomics.
- Add path filtering configuration and examples for embedding.

## Phase 3 — Filesystem event coverage

Research fanotify file-handle event reporting and safe name correlation for create, delete, and rename. Implement only events with verifiable process attribution and documented semantics. Keep unsupported states explicit.

## Phase 4 — Windows research and collector

Evaluate ETW providers, file/process attribution, privileges, supported Windows versions, event loss, and equivalent semantics before implementation.

## Phase 5 — macOS research and collector

Evaluate Endpoint Security permissions, entitlements, event semantics, packaging, and distribution requirements before implementation.

## Later

Cross-platform semantic stabilization and additional event families may follow once multiple working collectors demonstrate a need. No AgentTrace-specific behavior, cloud service, dashboard, file-content capture, or secret collection is planned for this phase.
