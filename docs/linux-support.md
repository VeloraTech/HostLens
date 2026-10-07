# Linux collector: support, capabilities, and limits

The Phase 1 collector is implemented in `collectors/linux`. It has two independent kernel sources and filters file events to one configured directory.

## Mechanisms

### Process lifecycle: `NETLINK_CONNECTOR/CN_PROC`

The process connector delivers kernel fork and exit notifications through netlink. Fork notifications supply parent and child PIDs directly, so short-lived children do not need to survive a process-table scan. The collector ignores thread clones and reports the thread-group leader's exit with `leaderThreadExit: true`; a multithreaded process may still have other threads running when that leader exits. This is therefore a kernel task lifecycle signal, not a guarantee that the thread group has fully disappeared. The collector reads `/proc/<pid>/stat` and `/proc/<pid>/exe` opportunistically for parent/executable metadata; these may already be unavailable by the time userspace handles an event. Arguments are omitted by default and read from `/proc/<pid>/cmdline` only with `--include-command`; command-line values can contain secrets. Event timestamps are userspace receipt/normalization times, not the connector's kernel monotonic timestamps.

Connector availability depends on the kernel build (`CONFIG_CONNECTOR` and process events), namespaces, security policy, and privileges. Netlink multicast subscription generally requires root or `CAP_NET_ADMIN`. Subscription failures are reported as `permission_denied` or `unavailable`. Events can be lost if the kernel or netlink receive queue overflows; this initial implementation does not yet decode connector loss diagnostics, so it must not be treated as a complete audit log.

### File activity: `fanotify`

The collector requests notification-class fanotify and marks the filesystem mount containing the requested scope for `FAN_OPEN` and `FAN_MODIFY`. Mount-wide notifications are filtered in userspace to the resolved scope directory. Events include the kernel-supplied PID and an event file descriptor, whose path is resolved through `/proc/self/fd`.

This is process-attributed kernel file notification, not a generic directory watcher. The mount mark may observe many unrelated operations inside that mount before filtering. Mount marking requires `CAP_SYS_ADMIN`; the full mount may span far more than the selected directory. A file reached through a different bind mount may not match the mark and can be missed. Container, PID, and mount namespace boundaries affect what is visible.

| Event type | Status | Meaning |
|---|---|---|
| `file.opened` | Best effort | Kernel reported open; does not establish a successful read or content access. |
| `file.modified` | Best effort | Kernel reported a modification; does not identify changed bytes or guarantee durable storage. |
| `file.created` | Unsupported | Not generated. |
| `file.deleted` | Unsupported | Not generated. |
| `file.renamed` | Unsupported | Not generated. |

Creation, deletion, and rename require reliable name/event correlation beyond this initial descriptor-based implementation. They are not inferred from close or open events.

`FAN_Q_OVERFLOW` is counted in collector health. Unresolvable paths, event parse errors, permission failures, and bounded stream drops are surfaced in health/status. The implementation does not read file contents, hash files, read environment variables, or send telemetry remotely.

## Capability and permission behavior

Process and file collectors start independently. One may work when the other fails. The `capabilities --scope` command briefly initializes both sources and reports their observed startup states, then shuts them down. Consumers can inspect the collector capability property and status after startup. `available` indicates a source initialized, not complete system coverage. `unsupported` means this implementation intentionally does not produce that event. Elevated privileges are not requested automatically.

```sh
python -m nativerelay.cli capabilities --scope /workspace
python -m nativerelay.cli observe --scope /workspace --json
```

## Validation status

Deterministic tests exercise normalized models, stream limits, connector packet parsing, acknowledgement handling, and permission/unsupported capability states. The opt-in integration tests use a temporary child process and temporary file.

The current development host's WSL2 kernel (`6.6.87.2-microsoft-standard-WSL2`) passed the root fanotify open/modify attribution test; the unprivileged fanotify test correctly reported `EPERM`. CN_PROC did not acknowledge a subscription in either the ordinary distro user or its root user namespace, so the process integration test skipped. The WSL distro runs in a non-initial PID namespace; the kernel's CN_PROC handler returns without acknowledging requests outside the initial PID/user namespaces ([kernel handler](https://github.com/torvalds/linux/blob/master/drivers/connector/cn_proc.c#L1815-L1829)). This is an environment limitation, not evidence of CN_PROC behavior on a normal Linux VM or host. Run the process test on a Linux host in the initial PID namespace before claiming process lifecycle support has passed live validation.

The repository's [Linux collector workflow](../.github/workflows/linux-collector.yml) runs the required live checks as root on Ubuntu 22.04 and 24.04. A collector unavailable in that environment fails CI rather than silently skipping validation.
