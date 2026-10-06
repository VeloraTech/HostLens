# Platform support

NativeRelay normalizes the event interface across platforms, while platform-specific collectors expose different capabilities and coverage.

| Platform | System telemetry status | Implementation |
|---|---|---|
| Linux | Linux-supported, initial implementation | `NETLINK_CONNECTOR/CN_PROC`; `fanotify` |
| macOS | Future | No collector implemented |
| Windows | Future | No collector implemented |

Do not infer that an unimplemented platform supports a common event merely because it appears in `EventType`. Query each active collector's `capabilities`. Read [Linux support](linux-support.md) for Linux behavior, requirements, and limitations.
