"""Operator messages as dictionaries, following the envelope in docs/INTERFACES.md."""
import uuid
from datetime import datetime, timezone

from ..models.enums import OperatorRole, ReportType
from ..models.human_report import HumanReport

SCHEMA_VERSION = 1
TYPE_FOR_REPORT = {
    ReportType.BIN_LOADED: "operator.bin_loaded",
    ReportType.BIN_EMPTIED: "operator.bin_emptied",
    ReportType.MATERIAL_REQUESTED: "operator.material_requested",
}
REPORT_FOR_TYPE = {name: report_type for report_type, name in TYPE_FOR_REPORT.items()}


def make_message(report_type, source, role, request_id="", bin_id="", material_type="", tool_id="") -> dict:
    """Build the message dict an operator interface sends.
    In a real system the role would come from the person's account, not from the message."""
    payload = {"role": role.name if role else None}
    if bin_id:
        payload["bin_id"] = bin_id
    if report_type == ReportType.MATERIAL_REQUESTED:
        payload["material_type"] = material_type
        payload["tool_id"] = tool_id
    return {
        "schema_version": SCHEMA_VERSION,
        "message_id": f"evt-{uuid.uuid4().hex[:8]}",
        "message_type": TYPE_FOR_REPORT[report_type],
        "request_id": request_id,
        "source": source,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload,
    }


def parse_message(message: dict, requests: dict) -> HumanReport:
    """Check an operator message and turn it into a HumanReport. Raises ValueError if it is not valid."""
    if message.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version {message.get('schema_version')!r}")
    report_type = REPORT_FOR_TYPE.get(message.get("message_type"))
    if report_type is None:
        raise ValueError(f"unknown message_type {message.get('message_type')!r}")
    if not message.get("message_id") or not message.get("source"):
        raise ValueError("message needs a message_id and a source")
    payload = message.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("message needs a payload")
    try:
        timestamp = datetime.fromisoformat(str(message.get("timestamp")).replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("timestamp is not a valid date and time") from None

    role = None
    if payload.get("role") is not None:
        if payload["role"] not in OperatorRole.__members__:
            raise ValueError(f"unknown role {payload['role']!r}")
        role = OperatorRole[payload["role"]]

    if report_type == ReportType.MATERIAL_REQUESTED:
        if not payload.get("material_type") or not payload.get("tool_id"):
            raise ValueError("material request needs a material_type and a tool_id")
        return HumanReport(report_type, None, timestamp, message.get("request_id", ""), role,
                           payload["material_type"], payload["tool_id"])

    request = requests.get(message.get("request_id"))
    if request is None:
        raise ValueError(f"unknown request_id {message.get('request_id')!r}")
    if payload.get("bin_id") != request.bin.bin_id:
        raise ValueError(f"bin {payload.get('bin_id')!r} does not belong to request {request.request_id}")
    return HumanReport(report_type, request.bin, timestamp, request.request_id, role)
