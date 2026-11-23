from ..models.enums import AccessResult, AMRStatus, BinState, ReportType, RequestStatus, SignalType
from ..models.operator_roles import is_allowed
from . import request_state
from .message_translator import translate_messages
from .operator_messages import parse_message


class Middleware:
    """Central control layer: receives news from every party, drives requests through the state machine,
    and reports status to the MCS."""

    def __init__(self, mcs, fleet_managers, gantry=None, operator_interface=None):
        self.mcs = mcs
        self.fleet_managers = fleet_managers
        self.gantry = gantry
        self.operator_interface = operator_interface
        self.requests = {}  # request_id -> DeliveryRequest
        self.rejected = []           # (message or report, reason) for anything refused
        self.material_requests = []  # MATERIAL_REQUESTED reports; who turns these into deliveries is open (SCRUM-65)
        self._seen_message_ids = set()

    # ---- raw messages -> receive_* (see sequence diagram) ----
    def translate_messages(self, raw_message: str) -> dict:
        return translate_messages(raw_message)

    # ---- entry points (all one-way notifications) ----
    def receive_delivery_request(self, request) -> None:
        self.requests[request.request_id] = request
        if self.operator_interface:
            self.operator_interface.prompt_fill(
                request.bin.bin_id, request.material_type, request.delivery_point.point_id)
        self._try_assign(request)

    def receive_operator_message(self, raw) -> None:
        """Operator message as a dict (or JSON text) in the INTERFACES.md envelope.
        Validates it, turns it into a HumanReport and hands it to receive_report."""
        message = self.translate_messages(raw) if isinstance(raw, str) else raw
        if message.get("message_id") in self._seen_message_ids:
            return  # same event delivered twice: no second effect
        try:
            report = parse_message(message, self.requests)
        except ValueError as error:
            self.rejected.append((message, str(error)))
            return
        self._seen_message_ids.add(message["message_id"])
        self.receive_report(report)

    def receive_report(self, report) -> None:
        if report.role is not None and not is_allowed(report.role, report.report_type):
            self.rejected.append((report, f"{report.role.name} may not send {report.report_type.name}"))
            return
        if report.report_type == ReportType.BIN_LOADED:
            report.bin.state = BinState.LOADED
            for request in list(self.requests.values()):
                if request.bin is report.bin:
                    self._try_assign(request)
        elif report.report_type == ReportType.BIN_EMPTIED:
            if report.bin.state != BinState.DELIVERED:
                self.rejected.append((report, f"bin {report.bin.bin_id} is {report.bin.state.name}, not DELIVERED"))
                return
            report.bin.state = BinState.EMPTIED  # the empty-bin return is a separate, still undefined flow
        elif report.report_type == ReportType.MATERIAL_REQUESTED:
            self.material_requests.append(report)  # recorded only

    def receive_amr_status(self, amr, status) -> None:
        request = self._request_for(amr)
        if request is None:
            return
        if status == AMRStatus.MOVING and request.status == RequestStatus.ASSIGNED:
            request.bin.state = BinState.IN_TRANSIT
            self._set(request, RequestStatus.IN_TRANSIT)
            self._check_doors(request, amr)
        elif status == AMRStatus.ARRIVED and request.status == RequestStatus.IN_TRANSIT:
            request.bin.state = BinState.DELIVERED
            self._set(request, RequestStatus.DELIVERED)
        elif status == AMRStatus.ERROR:
            self._set(request, RequestStatus.FAILED)

    def receive_handshake(self, handshake) -> None:
        if handshake.signal_type != SignalType.DELIVERY_RECEIVED:
            return
        for request in self.requests.values():
            if (request.delivery_point is handshake.tool.delivery_point
                    and request.status == RequestStatus.DELIVERED):
                self._set(request, RequestStatus.CONFIRMED)

    # ---- decision logic ----
    def run_decision_algorithm(self, request):
        """Placeholder: first available AMR. Replace with the real algorithm (and who decides is still open)."""
        for fm in self.fleet_managers:
            for amr in fm.amrs:
                if fm.report_amr_status(amr) == AMRStatus.AVAILABLE:
                    return amr
        return None

    def track_state(self, request_id: str) -> RequestStatus:
        return self.requests[request_id].status

    # ---- helpers ----
    def _try_assign(self, request) -> None:
        if request.status != RequestStatus.PENDING or request.bin.state != BinState.LOADED:
            return
        if request.delivery_point.occupied:  # never assume the destination is empty
            return
        amr = self.run_decision_algorithm(request)
        if amr is None:
            return
        fm = next(f for f in self.fleet_managers if amr in f.amrs)
        if self.gantry:
            self.gantry.place_bin_at_handoff(request.bin)
        if fm.assign_task(request, amr):
            request.assigned_amr = amr
            self._set(request, RequestStatus.ASSIGNED)

    def _check_doors(self, request, amr) -> None:
        for door in request.delivery_point.doors:
            if door.request_access(amr) != AccessResult.GRANTED:
                self._set(request, RequestStatus.AWAITING_ACCESS)  # retries / timeouts: TBD
                return

    def _request_for(self, amr):
        for request in self.requests.values():
            if request.assigned_amr is amr and request.status not in (
                    RequestStatus.CONFIRMED, RequestStatus.FAILED):
                return request
        return None

    def _set(self, request, status) -> None:
        request_state.transition(request, status)
        self.mcs.receive_status(request.request_id, status)
