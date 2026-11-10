import pytest

from capstone.middleware.request_state import IllegalTransition, transition
from capstone.models.amr import AMR
from capstone.models.bin import Bin
from capstone.models.delivery_request import DeliveryRequest
from capstone.models.enums import PointType, RequestStatus as S
from capstone.models.point import Point


def make_request():
    return DeliveryRequest("R1", "wafer", Bin("B1"), Point("H1", PointType.STORAGE_HANDOFF),
                           Point("T1", PointType.TOOL_POINT))


def test_normal_path():
    r = make_request()
    for s in (S.ASSIGNED, S.IN_TRANSIT, S.DELIVERED, S.CONFIRMED):
        transition(r, s)
    assert r.status == S.CONFIRMED


def test_illegal_transition():
    r = make_request()
    with pytest.raises(IllegalTransition):
        transition(r, S.DELIVERED)


def test_terminal_states_have_no_exit():
    r = make_request()
    transition(r, S.ASSIGNED)
    transition(r, S.FAILED)
    with pytest.raises(IllegalTransition):
        transition(r, S.IN_TRANSIT)
