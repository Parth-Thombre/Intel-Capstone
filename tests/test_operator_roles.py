import pytest

from capstone.middleware.middleware import Middleware
from capstone.middleware.operator_messages import make_message
from capstone.models.amr import AMR
from capstone.models.bin import Bin
from capstone.models.delivery_request import DeliveryRequest
from capstone.models.enums import (AMRStatus, BinState, OperatorRole as R, PointType, ReportType as T,
                                   RequestStatus as S)
from capstone.models.human_report import HumanReport
from capstone.models.point import Point
from capstone.simulators.console_operator import ConsoleOperatorInterface
from capstone.simulators.simulated import SimulatedFleetManager, SimulatedGantry, SimulatedMCS


def setup(role):
    lines = []
    operator = ConsoleOperatorInterface(output=lines.append, role=role)
    amr = AMR("AMR_1")
    mw = Middleware(SimulatedMCS(), [SimulatedFleetManager([amr])], SimulatedGantry(), operator)
    request = DeliveryRequest("R1", "wafer", Bin("B1"), Point("H1", PointType.STORAGE_HANDOFF),
                              Point("T1", PointType.TOOL_POINT))
    mw.receive_delivery_request(request)
    return mw, operator, request, amr, lines


def deliver(mw, request, amr):
    mw.receive_report(HumanReport(T.BIN_LOADED, request.bin))
    mw.receive_amr_status(amr, AMRStatus.MOVING)
    mw.receive_amr_status(amr, AMRStatus.ARRIVED)


def run(operator, mw, *commands):
    feed = iter(commands)
    operator.run(mw, input_fn=lambda _p: next(feed))


def msg(report_type, role, **kw):
    return make_message(report_type, "TEST", role, **kw)


# ---- roles decide what a person can do ----
def test_filler_only_gets_filler_commands():
    mw, operator, request, amr, lines = setup(R.BIN_FILLER)
    run(operator, mw, "empty B1", "quit")
    assert any("Unknown command" in line for line in lines)


def test_filler_loaded_assigns_request():
    mw, operator, request, amr, lines = setup(R.BIN_FILLER)
    run(operator, mw, "loaded", "quit")
    assert request.bin.state == BinState.LOADED and request.status == S.ASSIGNED


def test_technician_cannot_send_bin_loaded():
    mw, operator, request, amr, lines = setup(R.TOOL_TECHNICIAN)
    mw.receive_operator_message(msg(T.BIN_LOADED, R.TOOL_TECHNICIAN, request_id="R1", bin_id="B1"))
    assert request.status == S.PENDING and mw.rejected


def test_filler_cannot_send_bin_emptied():
    mw, operator, request, amr, lines = setup(R.BIN_FILLER)
    deliver(mw, request, amr)
    mw.receive_operator_message(msg(T.BIN_EMPTIED, R.BIN_FILLER, request_id="R1", bin_id="B1"))
    assert request.bin.state == BinState.DELIVERED and mw.rejected


# ---- the three events are separate facts ----
def test_empty_marks_bin_emptied_without_requesting_material():
    mw, operator, request, amr, lines = setup(R.TOOL_TECHNICIAN)
    deliver(mw, request, amr)
    run(operator, mw, "empty B1", "quit")
    assert request.bin.state == BinState.EMPTIED and mw.material_requests == []


def test_request_alone_records_material_request_and_leaves_bin_alone():
    mw, operator, request, amr, lines = setup(R.TOOL_TECHNICIAN)
    deliver(mw, request, amr)
    run(operator, mw, "request wafer T1", "quit")
    assert len(mw.material_requests) == 1 and request.bin.state == BinState.DELIVERED


def test_refill_does_both():
    mw, operator, request, amr, lines = setup(R.TOOL_TECHNICIAN)
    deliver(mw, request, amr)
    run(operator, mw, "refill B1", "quit")
    assert request.bin.state == BinState.EMPTIED
    assert [(m.material_type, m.tool_id) for m in mw.material_requests] == [("wafer", "T1")]


def test_cannot_empty_a_bin_that_was_never_delivered():
    mw, operator, request, amr, lines = setup(R.TOOL_TECHNICIAN)
    run(operator, mw, "empty B1", "quit")
    assert request.bin.state == BinState.EMPTY and any("REFUSED" in line for line in lines)


# ---- dictionary messages (INTERFACES.md envelope) ----
def test_message_has_the_documented_fields():
    m = msg(T.BIN_LOADED, R.BIN_FILLER, request_id="R1", bin_id="B1")
    assert {"schema_version", "message_id", "message_type", "request_id", "source", "timestamp",
            "payload"} <= m.keys()
    assert m["message_type"] == "operator.bin_loaded" and m["payload"]["bin_id"] == "B1"


def test_duplicate_message_id_has_no_second_effect():
    mw, operator, request, amr, lines = setup(R.BIN_FILLER)
    m = msg(T.BIN_LOADED, R.BIN_FILLER, request_id="R1", bin_id="B1")
    mw.receive_operator_message(m)
    mw.receive_operator_message(m)
    assert [s for _, s in mw.mcs.statuses] == [S.ASSIGNED]


@pytest.mark.parametrize("change", [
    {"schema_version": 2},
    {"message_type": "operator.nonsense"},
    {"request_id": "R99"},
    {"timestamp": "yesterday"},
    {"payload": {"role": "BIN_FILLER", "bin_id": "WRONG"}},
    {"payload": {"role": "JANITOR", "bin_id": "B1"}},
])
def test_invalid_messages_are_rejected_and_change_nothing(change):
    mw, operator, request, amr, lines = setup(R.BIN_FILLER)
    m = msg(T.BIN_LOADED, R.BIN_FILLER, request_id="R1", bin_id="B1")
    m.update(change)
    mw.receive_operator_message(m)
    assert request.status == S.PENDING and len(mw.rejected) == 1


def test_json_text_is_accepted_too():
    import json
    mw, operator, request, amr, lines = setup(R.BIN_FILLER)
    mw.receive_operator_message(json.dumps(msg(T.BIN_LOADED, R.BIN_FILLER, request_id="R1", bin_id="B1")))
    assert request.status == S.ASSIGNED
