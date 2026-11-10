from abc import ABC, abstractmethod


class MCS(ABC):
    """The sponsor's material control system (external)."""

    @abstractmethod
    def receive_status(self, request_id: str, status) -> None: ...
