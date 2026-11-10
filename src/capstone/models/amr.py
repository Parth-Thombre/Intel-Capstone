from dataclasses import dataclass

from .enums import AMRStatus


@dataclass(eq=False)
class AMR:
    """An autonomous mobile robot (commanded through its fleet manager)."""
    amr_id: str
    battery_level: int = 100  # 0..100
    status: AMRStatus = AMRStatus.AVAILABLE
    access_card_id: str = ""

    def drive_to(self, point) -> None:
        """Move to the given point (real movement is the vendor's job; simulated here)."""
        self.status = AMRStatus.MOVING
