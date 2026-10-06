import struct
import unittest
import errno
from pathlib import Path
from collectors.linux.collector import LinuxCollector, CN_IDX_PROC, CN_VAL_PROC, PROC_EVENT_FORK
from nativerelay.model import EventType, CollectorStatus

class LinuxParserTests(unittest.TestCase):
    def test_malformed_packet_rejected_without_crashing_collector(self):
        collector = LinuxCollector.__new__(LinuxCollector)
        with self.assertRaises(ValueError): collector._parse_proc_packet(struct.pack("=IHHII", 100, 0, 0, 0, 0))
    def test_fork_packet_preserves_parent_child_ids(self):
        collector = LinuxCollector.__new__(LinuxCollector)
        seen = []
        collector._emit_process = lambda typ, pid, ppid, metadata=None: seen.append((typ.value, pid, ppid))
        proc_event = struct.pack("=IIQ", PROC_EVENT_FORK, 0, 123456) + struct.pack("=IIII", 101, 101, 202, 202)
        cn = struct.pack("=IIIIHH", CN_IDX_PROC, CN_VAL_PROC, 7, 0, len(proc_event), 0) + proc_event
        nl = struct.pack("=IHHII", 16 + len(cn), 0x10, 0, 9, 0)
        collector._parse_proc_packet(nl + cn)
        self.assertEqual(seen, [("process.started", 202, 101)])
    def test_thread_clone_is_not_reported_as_new_process(self):
        collector = LinuxCollector.__new__(LinuxCollector)
        seen = []
        collector._emit_process = lambda *args, **kwargs: seen.append(args)
        proc_event = struct.pack("=IIQ", PROC_EVENT_FORK, 0, 123456) + struct.pack("=IIII", 101, 101, 303, 202)
        cn = struct.pack("=IIIIHH", CN_IDX_PROC, CN_VAL_PROC, 7, 0, len(proc_event), 0) + proc_event
        nl = struct.pack("=IHHII", 16 + len(cn), 0x10, 0, 9, 0)
        collector._parse_proc_packet(nl + cn)
        self.assertEqual(seen, [])
    def test_unsupported_and_permission_denied_capabilities(self):
        collector = LinuxCollector.__new__(LinuxCollector)
        collector.scope = Path("/controlled/scope")
        collector._caps = collector._initial_capabilities()
        collector.health = {"errors": []}
        self.assertEqual(next(c for c in collector.capabilities if c.event_type == EventType.FILE_CREATED).status, CollectorStatus.UNSUPPORTED)
    def test_connector_ack_controls_capability_state(self):
        collector = LinuxCollector.__new__(LinuxCollector)
        collector.scope = Path("/controlled/scope")
        collector._caps = collector._initial_capabilities()
        collector.health = {"process": "starting", "errors": []}
        body = struct.pack("=IIQi", 0, 0, 1, 0)
        cn = struct.pack("=IIIIHH", CN_IDX_PROC, CN_VAL_PROC, 1, 0, len(body), 0) + body
        nl = struct.pack("=IHHII", 16 + len(cn), 3, 0, 1, 0)
        collector._parse_proc_packet(nl + cn)
        self.assertEqual(collector.health["process"], "available")
        self.assertEqual(next(c for c in collector.capabilities if c.event_type == EventType.PROCESS_STARTED).status, CollectorStatus.AVAILABLE)
        body = struct.pack("=IIQi", 0, 0, 2, errno.EPERM)
        cn = struct.pack("=IIIIHH", CN_IDX_PROC, CN_VAL_PROC, 2, 0, len(body), 0) + body
        nl = struct.pack("=IHHII", 16 + len(cn), 3, 0, 2, 0)
        collector._parse_proc_packet(nl + cn)
        self.assertEqual(next(c for c in collector.capabilities if c.event_type == EventType.PROCESS_STARTED).status, CollectorStatus.PERMISSION_DENIED)
        collector._failure("filesystem", PermissionError("denied"))
        self.assertEqual(next(c for c in collector.capabilities if c.event_type == EventType.FILE_OPENED).status, CollectorStatus.PERMISSION_DENIED)
        self.assertEqual(next(c for c in collector.capabilities if c.event_type == EventType.FILE_CREATED).status, CollectorStatus.UNSUPPORTED)

if __name__ == "__main__": unittest.main()
