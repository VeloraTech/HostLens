"""Bounded synchronous event stream shared by collectors."""
from queue import Queue, Full, Empty
from .model import Event

class EventStream:
    def __init__(self, capacity=1024):
        if capacity <= 0: raise ValueError("capacity must be positive")
        self._queue = Queue(maxsize=capacity)
        self.dropped = 0
    def publish(self, event: Event):
        if not isinstance(event, Event): raise TypeError("event must be a NativeRelay Event")
        try: self._queue.put_nowait(event); return True
        except Full: self.dropped += 1; return False
    def receive(self, timeout=None):
        try: return self._queue.get(timeout=timeout)
        except Empty as exc: raise TimeoutError("no NativeRelay event available") from exc
    def __iter__(self):
        while True: yield self.receive()
