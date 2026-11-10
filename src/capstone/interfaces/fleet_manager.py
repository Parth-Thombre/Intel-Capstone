from abc import ABC, abstractmethod


class FleetManager(ABC):
    """Vendor software that commands a group of AMRs."""

    amrs: list

    @abstractmethod
    def assign_task(self, request, amr) -> bool: ...

    @abstractmethod
    def report_amr_status(self, amr):
        """Pull: return the AMR's current status."""

    @abstractmethod
    def receive_amr_update(self, amr, status) -> None:
        """Push from an AMR (bin collected, arrived)."""
