from dataclasses import dataclass, field
from datetime import datetime

from .enums import SignalType


@dataclass(eq=False)
class ProcessTool:
    tool_id: str
    delivery_point: object  # Point


@dataclass(eq=False)
class ToolHandshake:
    """A signal from a process tool (material needed / delivery received)."""
    signal_type: SignalType
    tool: ProcessTool
    timestamp: datetime = field(default_factory=datetime.now)
