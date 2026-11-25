# Middleware Interface Contracts

Status: proposed prototype contract. External vendor and EE protocols are translated to this contract by adapters. No specific SEMI wire protocol is claimed.

## Message envelope

```json
{
  "schema_version": 1,
  "message_id": "evt-1042",
  "message_type": "amr.bin_collected",
  "request_id": "REQ-1001",
  "correlation_id": "cmd-1039",
  "source": "AMR01",
  "timestamp": "2026-11-13T02:30:00Z",
  "payload": {
    "bin_id": "BIN-17",
    "location_id": "PICKUP-A"
  }
}
```

`message_id` uniquely identifies an event. For commands, it is the stable command ID. `correlation_id` identifies the command answered by a response. Sensor events without an active command may omit it. Commands also require `target`, `expires_at` and explicit operation preconditions in their schema. Request and bin fields are required for delivery actions; availability messages need only device identity and observation information.

Adapters must validate field types, supported schema version, known identities and operation-specific required fields. Serialize enum names as strings. Stamp local receipt time independently from device observation time. Use a device boot/session ID and monotonic sequence for ordered status observations; reconcile after a new session rather than trusting old retained state.

## Transport endpoints

Every transport request identifies a `bin_id`, `pickup_point_id` and `delivery_point_id`. Wire IDs resolve to the existing domain `Bin` and `Point` objects. Supported route pairs are storage-to-tool, tool-to-storage and tool-to-tool; source and destination IDs must differ.

Source readiness and destination readiness are separate observations. Tool-source readiness/release and collection evidence replace storage preparation evidence when pickup is at a tool. A material-needed signal does not by itself identify a tool-to-tool source; the request creator must provide both endpoints.

Transfer and receipt events must correlate to the request, matching bin and relevant endpoint. Configure the receipt authority by destination: process tool, storage controller or authorized recipient. Define any new event schemas before implementing them; the current `ToolHandshake` only represents tool signals.

## Commands and events

| Interface | Command or input | Expected evidence |
| --- | --- | --- |
| MCS | Delivery request | Accepted/rejected with reason; request status updates |
| FleetManager | Assign transport task | Accepted/rejected, pickup arrival, collected bin, destination arrival, task clearance, blocked/error |
| Storage | Prepare source bin or observe independent readiness; request destination acceptance when receiving | Identified bin, source/destination readiness, AMR alignment, transfer complete, destination receipt, fault |
| Door | Request access for AMR/request/door | Granted/denied, actual door state, passage complete, fault |
| Tool | Material need, source pickup/release request, inbound notice/authorization request | Source pickup readiness/release, collection, destination readiness/authorization, transfer complete, receipt |
| Operator | Fill prompt and human report | Contents prepared, authorized receipt, recovery confirmation |

Assignment accepted is not collection. Robot arrival is not transfer. Destination transfer is not recipient receipt. Match request, command, source, bin, location and current phase before advancing.

Repeated receipt of the same event has no second effect. A different event ID for an already completed physical action must also be harmless: enforce command and phase guards. Record rejected or contradictory events with a reason; do not overwrite verified custody silently.

## Python implementation boundaries

| Boundary | Current location | Implementation handoff |
| --- | --- | --- |
| MCS | `interfaces/mcs.py` | Preserve `receive_status`; implement incoming request translation in an adapter |
| Fleet | `interfaces/fleet_manager.py` | Preserve assignment and status operations; distinguish acceptance from collection |
| Storage | `interfaces/storage_gantry.py` | Preserve preparation facade; define receiving/readiness/receipt extensions before return execution |
| Door | `interfaces/access_door.py` | Preserve access and open-state operations; correlate passage evidence in future events |
| Operator | `interfaces/operator_interface.py` | Preserve fill prompts and existing reports; route prompts according to transport purpose |
| Tool | `interfaces/process_tool.py` | Implement `ProcessToolInterface.request_pickup(request)` and `request_delivery(request)` in tool adapters |

Paths above are relative to `src/capstone/`. The tool interface is a new outbound extension; `models/tool_handshake.py` still owns the existing `ProcessTool` and `ToolHandshake` data classes. Abstract tool methods raise `NotImplementedError` if invoked through an unimplemented base operation. They are not connected to the current middleware or startup composition.

Tool request methods receive a `DeliveryRequest`, using `pickup_point` for release and `delivery_point` for acceptance. Tool-to-tool transport routes these calls to different endpoint adapters. A normal return from either method does not authorize movement or confirm a transfer. Readiness, acceptance, collection, destination transfer and receipt must arrive as separately correlated evidence; formal event schemas and rejection reporting remain part of the shared-model and adapter work.

The importable `adapters`, `messaging` and `persistence` packages contain responsibility descriptions only. Implement protocol conversion, queued transport/routing and transactional repositories in those respective packages. Do not add side effects to package imports or make a placeholder return a fabricated success result.

## Prototype topics

```text
intel/v1/mcs/requests
intel/v1/mcs/status
intel/v1/fleets/{fleet_id}/commands
intel/v1/fleets/{fleet_id}/events
intel/v1/storage/{storage_id}/commands
intel/v1/storage/{storage_id}/events
intel/v1/doors/{door_id}/commands
intel/v1/doors/{door_id}/events
intel/v1/tools/{tool_id}/commands
intel/v1/tools/{tool_id}/events
intel/v1/devices/{device_id}/availability
```

Use QoS 1 for prototype workflow messages and application deduplication. Commands and action events are non-retained. Retained availability, if used, must include freshness/session information; a retained online message is not sufficient proof of live readiness. Use device-scoped topic permissions when integrating physical clients.

## Measurement

Record event receipt time, processing time, command publish time, acceptance time and completion time. Report missing, incorrect and delayed signals separately. Cross-device timestamps require measured clock synchronization before claiming one-way latency; otherwise measure local round trips and processing intervals.

## Contract examples required before integration

For each adapter, supply validated examples of success, rejection, delayed completion, duplicate delivery, wrong identity, disconnect and restart. Pin the supported schema version and record units, signal meaning, timing parameters and acknowledgement semantics in its configuration/documentation.
