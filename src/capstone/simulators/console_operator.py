"""Console prototype of the operator interface (SCRUM-84, role-aware version).

Without a role it behaves like the first version: one person, one 'done' command.
With a role, the person only gets the commands for their job:

  BIN_FILLER       list, loaded [bin]                    -> operator.bin_loaded
  TOOL_TECHNICIAN  list, empty <bin>                     -> operator.bin_emptied
                   request <material> <tool>             -> operator.material_requested
                   refill <bin>                          -> bin_emptied + material_requested together

In a real system the role would come from the person's login or tablet. Here it is a constructor
argument, so no accounts are needed to show the idea.
"""
from ..interfaces.operator_interface import OperatorInterface
from ..middleware.operator_messages import make_message
from ..models.enums import BinState, OperatorRole, ReportType
from ..models.human_report import HumanReport


class ConsoleOperatorInterface(OperatorInterface):
    def __init__(self, output=print, role=None, source="OPERATOR_CONSOLE"):
        self.output = output
        self.role = role
        self.source = source
        self.pending = {}  # bin_id -> (material_type, tool_id), still waiting to be loaded

    # Called by the middleware when a new delivery request arrives.
    def prompt_fill(self, bin_id, material_type, tool_id):
        self.pending[bin_id] = (material_type, tool_id)
        self.output(f"[REQUEST] Load bin {bin_id} with '{material_type}' for tool {tool_id}.")

    # ---- operator loop ----
    def run(self, middleware, input_fn=input):
        self.output(self._help())
        while True:
            parts = input_fn("operator> ").split()
            if not parts:
                continue
            cmd, args = parts[0].lower(), parts[1:]
            if cmd == "quit":
                return
            handler = self._commands().get(cmd)
            if handler is None:
                self.output(f"Unknown command for this role: {cmd}. " + self._help())
            else:
                handler(middleware, args)

    def _commands(self):
        commands = {"list": self._list}
        if self.role in (None, OperatorRole.BIN_FILLER):
            commands["done" if self.role is None else "loaded"] = self._loaded
        if self.role == OperatorRole.TOOL_TECHNICIAN:
            commands.update({"empty": self._empty, "request": self._request, "refill": self._refill})
        return commands

    def _help(self):
        names = ", ".join(sorted(self._commands()) + ["quit"])
        who = self.role.name if self.role else "no role (original single-operator mode)"
        return f"Role: {who}. Commands: {names}"

    # ---- commands ----
    def _list(self, middleware, args):
        if self.role == OperatorRole.TOOL_TECHNICIAN:
            waiting = [r for r in middleware.requests.values() if r.bin.state == BinState.DELIVERED]
            if not waiting:
                self.output("No delivered bins waiting to be emptied.")
            for r in waiting:
                self.output(f"  {r.bin.bin_id}: {r.material_type} at {r.delivery_point.point_id}")
            return
        if not self.pending:
            self.output("No bins waiting to be filled.")
        for bin_id, (material, tool) in self.pending.items():
            self.output(f"  {bin_id}: {material} -> {tool}")

    def _loaded(self, middleware, args):
        bin_id = self._pick_pending_bin(args)
        if bin_id is None:
            return
        request = self._request_for_bin(middleware, bin_id)
        del self.pending[bin_id]
        if self.role is None:  # original mode: send the report object directly
            middleware.receive_report(HumanReport(ReportType.BIN_LOADED, request.bin))
        else:
            self._send(middleware, ReportType.BIN_LOADED, request.request_id, bin_id=bin_id)
        self.output(f"[REPORT] Bin {bin_id} loaded. Request {request.request_id} is now "
                    f"{middleware.track_state(request.request_id).name}.")

    def _empty(self, middleware, args):
        request = self._delivered_request(middleware, args)
        if request is not None and self._send(middleware, ReportType.BIN_EMPTIED, request.request_id,
                                              bin_id=request.bin.bin_id):
            self.output(f"[REPORT] Bin {request.bin.bin_id} marked empty.")

    def _request(self, middleware, args):
        if len(args) != 2:
            self.output("Usage: request <material> <tool_id>")
            return
        if self._send(middleware, ReportType.MATERIAL_REQUESTED, "", material_type=args[0], tool_id=args[1]):
            self.output(f"[REPORT] Material requested: {args[0]} for {args[1]}.")

    def _refill(self, middleware, args):
        """One action for the common case: the bin is used up and more material is wanted."""
        request = self._delivered_request(middleware, args)
        if request is None:
            return
        if self._send(middleware, ReportType.BIN_EMPTIED, request.request_id, bin_id=request.bin.bin_id):
            self._send(middleware, ReportType.MATERIAL_REQUESTED, request.request_id,
                       material_type=request.material_type, tool_id=request.delivery_point.point_id)
            self.output(f"[REPORT] Bin {request.bin.bin_id} empty; more {request.material_type} requested "
                        f"for {request.delivery_point.point_id}.")

    # ---- helpers ----
    def _send(self, middleware, report_type, request_id, **fields):
        """Send one operator message and say so if the middleware refused it."""
        message = make_message(report_type, self.source, self.role, request_id, **fields)
        before = len(middleware.rejected)
        middleware.receive_operator_message(message)
        if len(middleware.rejected) > before:
            self.output(f"[REFUSED] {middleware.rejected[-1][1]}")
            return False
        return True

    def _pick_pending_bin(self, args):
        bin_id = args[0] if args else (next(iter(self.pending)) if len(self.pending) == 1 else None)
        if bin_id not in self.pending:
            self.output("Say which bin (type 'list' to see them).")
            return None
        return bin_id

    def _delivered_request(self, middleware, args):
        if not args:
            self.output("Say which bin (type 'list' to see them).")
            return None
        request = self._request_for_bin(middleware, args[0])
        if request is None:
            self.output(f"No request for bin {args[0]}.")
        return request

    @staticmethod
    def _request_for_bin(middleware, bin_id):
        # The middleware matches bins by object, so find the real Bin from its requests.
        return next((r for r in middleware.requests.values() if r.bin.bin_id == bin_id), None)
