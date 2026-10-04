# NativeRelay Platform Support

NativeRelay is designed to provide a common event interface across operating systems while preserving the differences between their native telemetry systems.

Cross-platform support does **not** mean identical capabilities.

A collector is considered supported only when NativeRelay can provide useful, documented, and sufficiently reliable telemetry on that platform.

---

## Platform overview

| Platform | Collector         | Status         | Initial focus           |
| -------- | ----------------- | -------------- | ----------------------- |
| Linux    | Native collector  | In development | Process + file activity |
| Windows  | Native collector  | Research       | Process + file I/O      |
| macOS    | Endpoint Security | Research       | Process + file activity |

The implementation status may change as platform research progresses.

---

# Linux

Linux is the initial reference platform for NativeRelay.

Linux provides several low-level mechanisms for observing system activity. For filesystem activity, NativeRelay is primarily investigating `fanotify` rather than treating ordinary filesystem change watching as sufficient.

`fanotify` can report events such as file access, open, modification, close, and filesystem changes. Events can include the PID of the process that caused the event.

Conceptually:

```text
Linux process
      │
      ▼
  fanotify
      │
      ▼
NativeRelay collector
      │
      ▼
normalized event
```

### Relevant capabilities

The Linux `fanotify` API provides notification events as well as permission events. Relevant event types include:

```text
FAN_ACCESS
FAN_OPEN
FAN_MODIFY
FAN_CLOSE_WRITE
FAN_CLOSE_NOWRITE
FAN_CREATE
FAN_DELETE
FAN_MOVE
```

The exact events available depend on the fanotify configuration and Linux version.

Linux can also expose permission events such as `FAN_OPEN_PERM` and `FAN_ACCESS_PERM`, but these have different semantics from ordinary notification events and require specific fanotify classes. NativeRelay should not treat permission events as interchangeable with ordinary observations.

### Process attribution

A fanotify event can contain the PID of the process that caused the event. With appropriate configuration, thread IDs can also be reported.

This makes Linux a useful reference platform for NativeRelay's process-attributed file-event model.

### Important limitation

Linux telemetry is not automatically complete.

For example, fanotify exposes a queue and defines `FAN_Q_OVERFLOW` when the event queue exceeds its limit. A collector therefore needs an explicit strategy for detecting and communicating lost events.

NativeRelay should never silently present a potentially incomplete event stream as complete.

### Initial Linux target

The first Linux collector will investigate:

```text
Process lifecycle
       +
Process-attributed file activity
       +
Event loss detection
       +
Normalized NativeRelay events
```

The initial implementation should remain focused rather than attempting to expose every Linux kernel event.

---

# Windows

Windows has a mature event-tracing infrastructure through **Event Tracing for Windows (ETW)**.

ETW allows applications to consume events from user-mode and kernel-mode providers, either in real time or from trace data.

Conceptually:

```text
Windows kernel/providers
          │
          ▼
         ETW
          │
          ▼
NativeRelay Windows collector
          │
          ▼
normalized events
```

### File I/O

Windows ETW exposes file I/O event types.

The Windows documentation includes file events such as:

```text
FileCreate
FileIo_ReadWrite
FileIo_SimpleOp
```

and related file-object information that can be correlated across events.

Kernel tracing configuration also exposes file-I/O related flags, including file I/O initialization and disk/file I/O events.

### Why Windows requires separate research

The existence of ETW does not mean NativeRelay can immediately provide an identical event model to Linux.

The Windows collector needs to determine:

* which providers are appropriate
* which events provide process attribution
* how file objects are correlated
* what permissions are required
* how event ordering should be handled
* what telemetry is available consistently across supported Windows versions
* how much information can be obtained without requiring privileged components

The collector should be designed around the actual guarantees of the selected providers.

### Initial Windows status

```text
Research
```

No Windows capability should be marked as supported merely because ETW exposes a related event.

---

# macOS

macOS provides the **Endpoint Security** framework for security-oriented system event monitoring.

Endpoint Security exposes event types covering process and filesystem activity. Apple's documentation includes events for operations such as:

```text
open
create
close
rename
write
access
```

among other filesystem-related events.

Conceptually:

```text
macOS
  │
  ▼
Endpoint Security
  │
  ▼
NativeRelay collector
  │
  ▼
normalized events
```

### File events

Apple's Endpoint Security event model includes a file-open event:

```text
ES_EVENT_TYPE_NOTIFY_OPEN
```

and an associated `es_event_open_t` structure.

The framework also defines event types for operations including file creation, closing, renaming, truncation, writing, lookup, and other filesystem activity.

### Process events

Endpoint Security also provides process-related event types, including process fork events and information about the resulting child process.

This makes Endpoint Security a promising native foundation for process-attributed events on macOS.

### Important consideration

macOS Endpoint Security is not simply a drop-in equivalent of Linux `fanotify`.

The collector must account for:

* Endpoint Security configuration
* required permissions
* deployment requirements
* event semantics
* system security restrictions
* distribution and developer experience
