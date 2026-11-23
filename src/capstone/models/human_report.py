from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .bin import Bin
from .enums import OperatorRole, ReportType


@dataclass(eq=False)
class HumanReport:
    """A message from a person: bin loaded, bin emptied, or material requested."""
    report_type: ReportType
    bin: Optional[Bin] = None
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = ""
    role: Optional[OperatorRole] = None  # who is reporting; None means not checked (older callers)
    material_type: str = ""              # MATERIAL_REQUESTED only
    tool_id: str = ""                    # MATERIAL_REQUESTED only
