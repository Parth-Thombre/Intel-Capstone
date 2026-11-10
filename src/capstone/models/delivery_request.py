from dataclasses import dataclass
from typing import Optional

from .amr import AMR
from .bin import Bin
from .enums import RequestStatus
from .point import Point


@dataclass(eq=False)
class DeliveryRequest:
    """One bin moved from a pickup point to a delivery point."""
    request_id: str
    material_type: str
    bin: Bin
    pickup_point: Point
    delivery_point: Point
    priority: int = 0  # >= 0
    source: str = ""
    status: RequestStatus = RequestStatus.PENDING
    assigned_amr: Optional[AMR] = None
