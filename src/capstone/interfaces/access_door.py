from abc import ABC, abstractmethod


class AccessDoor(ABC):
    """Key card controlled door an AMR must pass through (external)."""

    @abstractmethod
    def request_access(self, amr): ...

    @abstractmethod
    def is_open(self) -> bool: ...
