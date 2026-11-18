from capstone.middleware.middleware import Middleware
from capstone.models.amr import AMR
from capstone.models.bin import Bin
from capstone.models.delivery_request import DeliveryRequest
from capstone.models.enums import BinState, PointType, RequestStatus as S
from capstone.models.point import Point
from capstone.simulators.console_operator import ConsoleOperatorInterface
from capstone.simulators.simulated import SimulatedFleetManager, SimulatedGantry, SimulatedMCS


def setup():
    lines = []
    operator = ConsoleOperatorInterface(output=lines.append)
    mw = Middleware(SimulatedMCS(), [SimulatedFleetManager([AMR("AMR_1")])], SimulatedGantry(), operator)
    request = DeliveryRequest("R1", "wafer", Bin("B1"), Point("H1", PointType.STORAGE_HANDOFF),
                              Point("T1", PointType.TOOL_POINT))
    return mw, operator, request, lines


def run_commands(operator, mw, *commands):
    feed = iter(commands)
    operator.run(mw, input_fn=lambda _prompt: next(feed))


def test_request_shows_a_fill_prompt():
    mw, operator, request, lines = setup()
    mw.receive_delivery_request(request)
    assert any("B1" in line and "wafer" in line and "T1" in line for line in lines)
    assert "B1" in operator.pending


def test_done_reports_bin_loaded_and_request_is_assigned():
    mw, operator, request, lines = setup()
    mw.receive_delivery_request(request)
    assert request.status == S.PENDING                 # still waiting for the operator
    run_commands(operator, mw, "done", "quit")
    assert request.bin.state == BinState.LOADED
    assert request.status == S.ASSIGNED
    assert operator.pending == {}


def test_done_with_explicit_bin_id():
    mw, operator, request, lines = setup()
    mw.receive_delivery_request(request)
    run_commands(operator, mw, "done B1", "quit")
    assert request.status == S.ASSIGNED


def test_done_for_unknown_bin_changes_nothing():
    mw, operator, request, lines = setup()
    mw.receive_delivery_request(request)
    run_commands(operator, mw, "done B99", "quit")
    assert request.status == S.PENDING
    assert "B1" in operator.pending


def test_second_done_is_ignored():
    mw, operator, request, lines = setup()
    mw.receive_delivery_request(request)
    run_commands(operator, mw, "done B1", "done B1", "quit")
    assert request.status == S.ASSIGNED
    assert [s for _, s in mw.mcs.statuses] == [S.ASSIGNED]   # reported to the MCS once
