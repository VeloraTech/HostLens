"""Platform-neutral collector contract."""
from abc import ABC, abstractmethod
from .model import Capability
from .stream import EventStream

class Collector(ABC):
    @property
    @abstractmethod
    def capabilities(self) -> tuple[Capability, ...]: ...
    @abstractmethod
    def start(self, stream: EventStream) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
