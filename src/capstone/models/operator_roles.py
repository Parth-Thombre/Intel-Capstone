from .enums import OperatorRole, ReportType

# What each kind of person may report. A role is about "who", the report type about "what happened".
ALLOWED_REPORTS = {
    OperatorRole.BIN_FILLER: {ReportType.BIN_LOADED},
    OperatorRole.TOOL_TECHNICIAN: {ReportType.BIN_EMPTIED, ReportType.MATERIAL_REQUESTED},
}


def is_allowed(role: OperatorRole, report_type: ReportType) -> bool:
    return report_type in ALLOWED_REPORTS.get(role, set())
