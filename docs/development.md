# Development and testing

NativeRelay uses Python 3.11+ and has no runtime dependencies. Run from the repository root:

```sh
python -m unittest discover -s tests -v
python -m nativerelay.cli capabilities --scope /tmp
python -m nativerelay.cli observe --scope /tmp --json
```

Core tests are platform-independent. Process decoder tests use constructed connector messages and do not require kernel privileges. Live integration checks for CN_PROC and fanotify must be performed on Linux; process connector subscription generally requires root or `CAP_NET_ADMIN`, and fanotify mount notification requires root or `CAP_SYS_ADMIN`. Use a fresh temporary directory and helper process for integration tests. Do not rely on the developer's home directory or internet access.

The live Linux checks are opt-in so ordinary unit runs remain unprivileged and deterministic:

```sh
NATIVERELAY_LINUX_INTEGRATION=1 python3 -m unittest discover -s tests -p test_linux_integration.py -v
```

The tests launch a short-lived controlled child and create/write a file under a temporary directory. They verify fork/exit delivery, parent PID, file open/modify delivery, and PID attribution. A test skips when its kernel facility or required privilege is unavailable. A passing skip is not evidence of live telemetry support; record whether each test ran or skipped on the target kernel.

Set `NATIVERELAY_LINUX_INTEGRATION_REQUIRED=1` in privileged CI to fail instead of skip when either kernel mechanism is unavailable. The Linux workflow runs this strict mode as root so missing CN_PROC or fanotify coverage makes the job fail visibly.

Validation on the current WSL2 Linux 6.6.87 kernel: fanotify passed as root and correctly failed without privilege. CN_PROC subscription timed out for both the normal distro user and root because this distro is in a non-initial PID namespace. Its live process test remains unverified until run on a normal Linux host/VM.

The CLI emits one compact JSON event per line with `--json`. Human-readable output is the default. Ctrl-C shuts down both collector threads. The internal stream has a configurable bounded queue; overflow drops new events and increments a counter.
