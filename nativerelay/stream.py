"""Bounded synchronous event stream shared by collectors."""
from queue import Queue, Full, Empty
from threading import Lock
from .model import Event


class StreamClosed(RuntimeError):
    """Raised after a producer has closed the stream and queued events drain."""


class EventStream:
    def __init__(self, capacity=1024):
        if capacity <= 0: raise ValueError("capacity must be positive")
        self._queue = Queue(maxsize=capacity)
        self.dropped = 0
        self._closed = False
        self._lock = Lock()
        self._close_error = None

    @property
    def closed(self):
        with self._lock: return self._closed

    @property
    def error(self):
        with self._lock: return self._close_error

    def publish(self, event: Event):
        if not isinstance(event, Event): raise TypeError("event must be a NativeRelay Event")
        with self._lock:
            if self._closed: return False
            try: self._queue.put_nowait(event); return True
            except Full: self.dropped += 1; return False

    def close(self, error: BaseException | None = None):
        """Stop accepting events; buffered events remain available to consumers."""
        with self._lock:
            if self._closed: return
            self._closed = True
            self._close_error = error
            # Wake a blocked receiver if the queue is empty. A full queue already
            # guarantees that no receiver can be blocked waiting for an event.
            try: self._queue.put_nowait(_CLOSED)
            except Full: pass

    def receive(self, timeout=None):
        with self._lock:
            if self._closed and self._queue.empty():
                raise StreamClosed("NativeRelay event stream is closed")
        try: item = self._queue.get(timeout=timeout)
        except Empty as exc:
            if self.closed: raise StreamClosed("NativeRelay event stream is closed") from exc
            raise TimeoutError("no NativeRelay event available") from exc
        if item is _CLOSED:
            # Keep closure visible to every later receive call.
            try: self._queue.put_nowait(_CLOSED)
            except Full: pass
            raise StreamClosed("NativeRelay event stream is closed")
        return item

    def __iter__(self):
        while True:
            try: yield self.receive()
            except StreamClosed: return


_CLOSED = object()
