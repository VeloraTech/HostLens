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
        self._loss_generation = 0
        self._losses = {}

    @property
    def closed(self):
        with self._lock: return self._closed

    @property
    def error(self):
        with self._lock: return self._close_error

    @property
    def loss_generation(self):
        """Monotonic counter; changes whenever a producer reports detected loss."""
        with self._lock: return self._loss_generation

    @property
    def losses(self):
        """Copy of loss totals grouped by source and reason."""
        with self._lock:
            return {source: {reason: dict(totals) for reason, totals in reasons.items()}
                    for source, reasons in self._losses.items()}

    def _record_loss_locked(self, source, reason, count, sequence):
        totals = self._losses.setdefault(source, {}).setdefault(reason, {
            "occurrences": 0, "known_dropped": 0, "unknown_count": False,
            "last_sequence": None,
        })
        totals["occurrences"] += 1
        if count is None:
            totals["unknown_count"] = True
        else:
            totals["known_dropped"] += count
        if sequence is not None: totals["last_sequence"] = sequence
        self._loss_generation += 1

    def report_loss(self, source, reason, *, count=None, sequence=None):
        """Report an observed loss; count=None means the lost-event count is unknown."""
        if not isinstance(source, str) or not source: raise ValueError("loss source is required")
        if not isinstance(reason, str) or not reason: raise ValueError("loss reason is required")
        if count is not None and (not isinstance(count, int) or count < 0):
            raise ValueError("loss count must be a non-negative integer or None")
        if sequence is not None and (not isinstance(sequence, int) or sequence < 0):
            raise ValueError("loss sequence must be a non-negative integer or None")
        with self._lock:
            self._record_loss_locked(source, reason, count, sequence)

    def publish(self, event: Event):
        if not isinstance(event, Event): raise TypeError("event must be a NativeRelay Event")
        with self._lock:
            if self._closed:
                self.dropped += 1
                self._record_loss_locked(event.collector, "event_stream_closed", 1, event.sequence)
                return False
            try: self._queue.put_nowait(event); return True
            except Full:
                self.dropped += 1
                self._record_loss_locked(event.collector, "event_stream_full", 1, event.sequence)
                return False

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
