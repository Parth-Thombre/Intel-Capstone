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
    BIN_LOADED = auto()           # a bin filler says: this bin is filled with the requested material
    BIN_EMPTIED = auto()          # a tool technician says: this delivered bin has been used up
    MATERIAL_REQUESTED = auto()   # a tool technician asks for more material for a tool
    # Older names, not handled by the middleware. Proposed to be replaced by BIN_EMPTIED and
    # MATERIAL_REQUESTED; renaming enums touches the UML, so the team decides.
    JOB_DONE = auto()
    SEND_AMR = auto()


class OperatorRole(Enum):
    BIN_FILLER = auto()       # fills bins in the gantry / storage area
    TOOL_TECHNICIAN = auto()  # works at a process tool


class DoorState(Enum):
    CLOSED = auto()
    OPEN = auto()
    FAULT = auto()


class AccessResult(Enum):
    GRANTED = auto()
    DENIED = auto()
    TIMEOUT = auto()
