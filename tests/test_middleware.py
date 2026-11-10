from capstone.middleware.middleware import Middleware
from capstone.models.amr import AMR
from capstone.models.bin import Bin
from capstone.models.delivery_request import DeliveryRequest
from capstone.models.enums import (AccessResult, AMRStatus, ReportType, RequestStatus as S,
                                   PointType, SignalType)
from capstone.models.human_report import HumanReport
from capstone.models.point import Point
from capstone.models.tool_handshake import ProcessTool, ToolHandshake
from capstone.simulators.simulated import (SimulatedAccessDoor, SimulatedFleetManager,
                                           SimulatedGantry, SimulatedMCS,
                                           SimulatedOperatorInterface)


def setup(door_result=None):
    mcs, gantry, ops = SimulatedMCS(), SimulatedGantry(), SimulatedOperatorInterface()
    amr = AMR("AMR_1")
    fm = SimulatedFleetManager([amr])
    tool_point = Point("T1", PointType.TOOL_POINT)
    if door_result:
        tool_point.doors.append(SimulatedAccessDoor(door_result))
    request = DeliveryRequest("R1", "wafer", Bin("B1"), Point("H1", PointType.STORAGE_HANDOFF), tool_point)
    mw = Middleware(mcs, [fm], gantry, ops)
    return mw, mcs, amr, request, ProcessTool("TOOL1", tool_point)


def test_normal_delivery():
    mw, mcs, amr, request, tool = setup(AccessResult.GRANTED)
    mw.receive_delivery_request(request)
    assert request.status == S.PENDING                      # waiting for the operator
    mw.receive_report(HumanReport(ReportType.BIN_LOADED, request.bin))
    assert request.status == S.ASSIGNED
    mw.receive_amr_status(amr, AMRStatus.MOVING)
    mw.receive_amr_status(amr, AMRStatus.ARRIVED)
    mw.receive_handshake(ToolHandshake(SignalType.DELIVERY_RECEIVED, tool))
    assert [s for _, s in mcs.statuses] == [S.ASSIGNED, S.IN_TRANSIT, S.DELIVERED, S.CONFIRMED]


def test_door_denied_waits_for_access():
    mw, mcs, amr, request, tool = setup(AccessResult.DENIED)
    mw.receive_delivery_request(request)
    mw.receive_report(HumanReport(ReportType.BIN_LOADED, request.bin))
    mw.receive_amr_status(amr, AMRStatus.MOVING)
    assert request.status == S.AWAITING_ACCESS


def test_occupied_destination_is_not_assigned():
    mw, mcs, amr, request, tool = setup()
    request.delivery_point.occupied = True
    mw.receive_delivery_request(request)
    mw.receive_report(HumanReport(ReportType.BIN_LOADED, request.bin))
    assert request.status == S.PENDING
