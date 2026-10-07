# NativeRelay

NativeRelay is a local-first, embeddable operating-system observability layer for developer tools. It normalizes the event interface across platforms, while platform-specific collectors expose different capabilities and coverage.

**System telemetry is currently Linux-supported.** macOS and Windows collectors are future work. NativeRelay reports native observations; it does not identify AI agents, infer file contents, or depend on AgentTrace.

## Phase 1 status

The Linux collector uses the kernel process connector (`NETLINK_CONNECTOR/CN_PROC`) for process fork/exit events and `fanotify` for process-attributed file open/write-close notifications. Filesystem observation requires elevated privileges, is scoped to a user-selected directory (kernel monitoring is mounted-filesystem-wide, then filtered), and is best effort. Process events are independently available only when the kernel permits connector subscription.

| Event | Linux status | Notes |
|---|---|---|
| `process.started`, `process.exited` | Best effort | Kernel fork/leader-exit notifications; short-lived forked processes are included when notifications arrive. A leader exit does not guarantee all threads in its group have stopped. |
| `file.opened` | Best effort | `fanotify` open event with PID and path for the selected scope. |
| `file.modified` | Best effort | `fanotify` modification notification; does not report changed bytes or guarantee durable storage. |
| `file.created`, `file.deleted`, `file.renamed` | Unsupported | Not emitted; no inference from directory watchers. |

Unsupported, permission-denied, and unavailable capabilities are visible through the capability API/CLI. Queue loss and collector errors are available through collector health. No file contents or environment values are read. Process argv collection is opt-in because arguments can contain secrets.

## Run locally

Python 3.11 or newer, Linux, and no third-party runtime dependencies are required. From a checkout:

```sh
python -m nativerelay.cli capabilities --scope /path/to/workspace
python -m nativerelay.cli observe --scope /path/to/workspace
python -m nativerelay.cli observe --scope /path/to/workspace --json
```

The process connector may be unavailable depending on kernel configuration and privilege; subscribing to its netlink multicast group generally requires root or `CAP_NET_ADMIN`. `fanotify` mount monitoring requires `CAP_SYS_ADMIN`; the CLI reports each degraded state. Use least privilege that satisfies the kernel on the target system. `--include-command` opts into process argument collection and should be used with care.

## Embed

The platform-neutral event model, bounded stream, and collector contract live in `nativerelay`. A consumer can receive events from `EventStream.receive(timeout=...)`; events serialize through `Event.to_json()`. Linux-specific collection is isolated in `collectors.linux`.

## Documentation

- [Architecture](docs/architecture.md)
- [Event model](docs/event-model.md)
- [Linux support and limits](docs/linux-support.md)
- [Platform support](docs/platform-support.md)
- [Privacy](docs/privacy.md)
- [Development and testing](docs/development.md)
- [Roadmap](ROADMAP.md)
- [Design principles](docs/design-principles.md)

## Project status

Phase 1 is complete for the documented event set and remains pre-release. Controlled CN_PROC process-lifecycle and fanotify file-event integration tests passed in the privileged GitHub Actions Linux workflow; the workflow targets Ubuntu 22.04 and 24.04. The fanotify smoke test also passed under root in WSL2 on Linux 6.6.87. WSL could not validate CN_PROC because the distro uses a non-initial PID namespace. Process connector loss accounting is a known follow-up, and NativeRelay does not provide complete audit coverage. See the capability and limitations documentation before use.

MIT licensed. No cloud service, account, network connection, or remote telemetry is required.
