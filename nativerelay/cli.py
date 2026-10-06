"""NativeRelay local development CLI."""
import argparse
import json
import sys
from dataclasses import asdict
from collectors.linux import LinuxCollector
from .stream import EventStream

def main(argv=None):
    parser = argparse.ArgumentParser(prog="nativerelay", description="Observe local Linux kernel events")
    commands = parser.add_subparsers(dest="command", required=True)
    observe = commands.add_parser("observe", help="stream process events and scoped file open/write events")
    observe.add_argument("--scope", required=True, help="existing directory to include in file events")
    observe.add_argument("--json", action="store_true", help="emit one JSON event per line")
    observe.add_argument("--include-command", action="store_true", help="include argv (may contain sensitive data)")
    commands.add_parser("capabilities", help="show collector capabilities for a scope")
    capabilities = commands.choices["capabilities"]
    capabilities.add_argument("--scope", required=True)
    args = parser.parse_args(argv)
    try: collector = LinuxCollector(args.scope, include_command=getattr(args, "include_command", False))
    except (OSError, ValueError) as exc:
        print(f"nativerelay: {exc}", file=sys.stderr); return 2
    if args.command == "capabilities":
        collector.start(EventStream(1))
        try:
            print(json.dumps({"platform": "linux", "collector": collector.name,
                              "scope": str(collector.scope), "health": collector.status,
                              "capabilities": [
                                  {**asdict(c), "event_type": c.event_type.value, "status": c.status.value}
                                  for c in collector.capabilities]}, indent=2))
        finally: collector.stop()
        return 0
    stream = EventStream()
    try:
        collector.start(stream)
        print("NativeRelay Linux observe (Ctrl-C to stop)", file=sys.stderr)
        last_dropped = -1
        while True:
            try: event = stream.receive(timeout=1)
            except TimeoutError:
                status = collector.status
                if status["errors"] or status["dropped"] != last_dropped:
                    print(json.dumps({"collector_status": status}), file=sys.stderr)
                    collector.health["errors"].clear()
                    last_dropped = status["dropped"]
                continue
            print(event.to_json() if args.json else _human(event), flush=True)
    except KeyboardInterrupt:
        return 0
    finally: collector.stop()

def _human(event):
    proc = f"pid={event.process.pid}"
    if event.process.parent_pid is not None: proc += f" ppid={event.process.parent_pid}"
    if event.process.executable: proc += f" exe={event.process.executable}"
    resource = f" {event.resource.path}" if event.resource else ""
    metadata = " " + json.dumps(event.metadata) if event.metadata else ""
    return f"{event.timestamp} {event.type.value} {proc}{resource}{metadata}"

if __name__ == "__main__": raise SystemExit(main())
