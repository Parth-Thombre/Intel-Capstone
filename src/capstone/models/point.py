from dataclasses import dataclass, field

from .enums import PointType


@dataclass(eq=False)
class Point:
    """A location: tool point, storage handoff or charging station."""
    point_id: str
    point_type: PointType
    occupied: bool = False
    doors: list = field(default_factory=list)  # AccessDoor objects between an AMR and this point
