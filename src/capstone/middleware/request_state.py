from ..models.enums import RequestStatus as S

# From the request state machine diagram. A state maps to the states it may move to.
ALLOWED = {
    S.PENDING: {S.ASSIGNED},
    S.ASSIGNED: {S.IN_TRANSIT, S.AWAITING_ACCESS, S.FAILED},
    S.IN_TRANSIT: {S.IN_TRANSIT, S.AWAITING_ACCESS, S.DELIVERED, S.FAILED},
    S.AWAITING_ACCESS: {S.AWAITING_ACCESS, S.ASSIGNED, S.IN_TRANSIT, S.FAILED},
    S.DELIVERED: {S.CONFIRMED, S.FAILED},
    S.CONFIRMED: set(),
    S.FAILED: set(),
}


class IllegalTransition(Exception):
    pass


def transition(request, new_status: S) -> None:
    """Move a request to a new state, or raise if the diagram does not allow it."""
    if new_status not in ALLOWED[request.status]:
        raise IllegalTransition(f"{request.status.name} -> {new_status.name}")
    request.status = new_status
