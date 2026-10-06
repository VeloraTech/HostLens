# Development and testing

NativeRelay uses Python 3.11+ and has no runtime dependencies. Run from the repository root:

```sh
python -m unittest discover -s tests -v
python -m nativerelay.cli capabilities --scope /tmp
python -m nativerelay.cli observe --scope /tmp --json
```

Core tests are platform-independent. Process decoder tests use constructed connector messages and do not require kernel privileges. Live integration checks for CN_PROC and fanotify must be performed on Linux; process connector subscription generally requires root or `CAP_NET_ADMIN`, and fanotify mount notification requires root or `CAP_SYS_ADMIN`. Use a fresh temporary directory and helper process for integration tests. Do not rely on the developer's home directory or internet access.

The CLI emits one compact JSON event per line with `--json`. Human-readable output is the default. Ctrl-C shuts down both collector threads. The internal stream has a configurable bounded queue; overflow drops new events and increments a counter.
