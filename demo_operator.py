"""Demo of the console operator interface.

Run from the repo root:
    python3 demo_operator.py
    python3 demo_operator.py filler
    python3 demo_operator.py technician
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from capstone.middleware.middleware import Middleware
from capstone.models.amr import AMR
from capstone.models.bin import Bin
from capstone.models.delivery_request import DeliveryRequest
from capstone.models.enums import AMRStatus, OperatorRole, PointType, ReportType
from capstone.models.human_report import HumanReport
from capstone.models.point import Point
from capstone.simulators.console_operator import ConsoleOperatorInterface
from capstone.simulators.simulated import SimulatedFleetManager, SimulatedGantry, SimulatedMCS

ROLES = {
    "filler": OperatorRole.BIN_FILLER,
    "technician": OperatorRole.TOOL_TECHNICIAN,
}

arg = sys.argv[1] if len(sys.argv) > 1 else None

if arg is not None and arg not in ROLES:
    sys.exit(f"Unknown role {arg!r}. Use: filler, technician (or nothing).")

operator = ConsoleOperatorInterface(role=ROLES.get(arg))
amr = AMR("AMR_1")

mw = Middleware(
    SimulatedMCS(),
    [SimulatedFleetManager([amr])],
    SimulatedGantry(),
    operator,
)

request = DeliveryRequest(
    "R1",
    "wafer",
    Bin("B1"),
    Point("H1", PointType.STORAGE_HANDOFF),
    Point("T1", PointType.TOOL_POINT),
)

mw.receive_delivery_request(request)

if arg == "technician":
    # Simulate the bin being filled and delivered to the tool.
    operator.pending.clear()
    mw.receive_report(HumanReport(ReportType.BIN_LOADED, request.bin))
    mw.receive_amr_status(amr, AMRStatus.MOVING)
    mw.receive_amr_status(amr, AMRStatus.ARRIVED)
    print("(simulated: bin B1 was filled and delivered to tool T1)")

operator.run(mw)