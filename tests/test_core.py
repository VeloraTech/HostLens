import json
import unittest
from nativerelay.model import Event, EventType, Process, Resource, decode_event
from nativerelay.stream import EventStream
from nativerelay.collector import Collector
from nativerelay.model import Capability, CollectorStatus

class CoreTests(unittest.TestCase):
    def make_event(self):
        return Event(EventType.FILE_OPENED, "linux", "test", Process(10, 1, "/bin/demo", ("demo",)),
                     Resource("file", "/tmp/a"), timestamp="2026-01-01T00:00:00+00:00", id="stable")
    def test_round_trip_stable_serialization(self):
        event = self.make_event()
        self.assertEqual(decode_event(event.to_json()), event)
        self.assertEqual(event.to_json(), event.to_json())
    def test_stable_id(self):
        self.assertEqual(Event.stable_id("c", "b", 2), Event.stable_id("c", "b", 2))
        self.assertNotEqual(Event.stable_id("c", "b", 2), Event.stable_id("c", "b", 3))
    def test_validation_and_malformed_input(self):
        with self.assertRaises(ValueError): Process(0)
        with self.assertRaises(ValueError): Event(EventType.PROCESS_STARTED, "linux", "test", "not-a-process")
        with self.assertRaises(ValueError): Event(EventType.PROCESS_STARTED, "linux", "test", Process(1), metadata={"bad": object()})
        with self.assertRaises(ValueError): decode_event("{}")
        obj = json.loads(self.make_event().to_json()); obj["type"] = "process.telepathy"
        with self.assertRaises(ValueError): decode_event(json.dumps(obj))
    def test_bounded_stream_and_timeout(self):
        stream = EventStream(1); event = self.make_event()
        self.assertTrue(stream.publish(event)); self.assertFalse(stream.publish(event))
        self.assertEqual(stream.dropped, 1); self.assertEqual(stream.receive(), event)
        with self.assertRaises(TimeoutError): stream.receive(timeout=0)
    def test_capability_and_collector_lifecycle(self):
        capability = Capability(EventType.PROCESS_STARTED, CollectorStatus.AVAILABLE, "test", "host", "kernel")
        self.assertEqual(capability.status, CollectorStatus.AVAILABLE)
        class FakeCollector(Collector):
            running = False
            @property
            def capabilities(self): return (capability,)
            def start(self, stream): self.running = True
            def stop(self): self.running = False
        collector = FakeCollector(); collector.start(EventStream())
        self.assertTrue(collector.running); collector.stop(); self.assertFalse(collector.running)

if __name__ == "__main__": unittest.main()
