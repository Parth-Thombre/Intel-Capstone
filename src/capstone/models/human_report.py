from dataclasses import dataclass, field
from datetime import datetime

from .bin import Bin
from .enums import ReportType


@dataclass(eq=False)
class HumanReport:
    """A message from a bin handler, e.g. 'bin loaded'."""
    report_type: ReportType
    bin: Bin
    timestamp: datetime = field(default_factory=datetime.now)
