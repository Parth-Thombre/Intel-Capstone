from enum import Enum, auto


class RequestStatus(Enum):
    PENDING = auto()          # created, no AMR yet
    ASSIGNED = auto()         # an AMR is chosen
    AWAITING_ACCESS = auto()  # waiting for a door to open
    IN_TRANSIT = auto()       # bin is on its way
    DELIVERED = auto()        # AMR dropped it off
    CONFIRMED = auto()        # tool confirmed receipt
    FAILED = auto()           # delivery did not complete


class AMRStatus(Enum):
    MOVING = auto()
    ARRIVED = auto()
    BLOCKED = auto()
    ERROR = auto()
    AVAILABLE = auto()
    CHARGING = auto()


class BinState(Enum):
    EMPTY = auto()
    LOADED = auto()
    IN_TRANSIT = auto()
    DELIVERED = auto()
    EMPTIED = auto()


class PointType(Enum):
    TOOL_POINT = auto()
    STORAGE_HANDOFF = auto()
    CHARGING_STATION = auto()


class SignalType(Enum):
    MATERIAL_NEEDED = auto()
    DELIVERY_RECEIVED = auto()


class ReportType(Enum):
    BIN_LOADED = auto()
    JOB_DONE = auto()
    SEND_AMR = auto()


class DoorState(Enum):
    CLOSED = auto()
    OPEN = auto()
    FAULT = auto()


class AccessResult(Enum):
    GRANTED = auto()
    DENIED = auto()
    TIMEOUT = auto()
