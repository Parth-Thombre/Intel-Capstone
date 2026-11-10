from ..interfaces.access_door import AccessDoor
from ..interfaces.fleet_manager import FleetManager
from ..interfaces.mcs import MCS
from ..interfaces.operator_interface import OperatorInterface
from ..interfaces.storage_gantry import StorageGantry
from ..models.enums import AccessResult, AMRStatus


class SimulatedMCS(MCS):
    def __init__(self):
        self.statuses = []  # (request_id, status) in the order received

    def receive_status(self, request_id, status):
        self.statuses.append((request_id, status))


class SimulatedFleetManager(FleetManager):
    def __init__(self, amrs):
        self.amrs = amrs

    def assign_task(self, request, amr):
        amr.status = AMRStatus.MOVING
        return True

    def report_amr_status(self, amr):
        return amr.status

    def receive_amr_update(self, amr, status):
        amr.status = status


class SimulatedAccessDoor(AccessDoor):
    def __init__(self, result=AccessResult.GRANTED):
        self.result = result

    def request_access(self, amr):
        return self.result

    def is_open(self):
        return self.result == AccessResult.GRANTED


class SimulatedGantry(StorageGantry):
    def __init__(self):
        self.placed = []

    def place_bin_at_handoff(self, bin):
        self.placed.append(bin)


class SimulatedOperatorInterface(OperatorInterface):
    def __init__(self):
        self.prompts = []

    def prompt_fill(self, bin_id, material_type, tool_id):
        self.prompts.append((bin_id, material_type, tool_id))
