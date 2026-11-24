# Middleware Implementation Plan

Use [the architecture](ARCHITECTURE.md) and [interface contracts](INTERFACES.md) as the shared coding baseline. Task labels below are documentation identifiers, not existing GitHub issues. Contributors can claim tasks in the pull request or team tracker.

## Work packages

| ID | Work | Dependencies | Completion evidence |
| --- | --- | --- | --- |
| A1 | Extend models with IDs, typed commands/events, execution phase and observation freshness | None | Valid/invalid schema examples and round-trip serialization |
| A2 | Implement UML state transitions and guards | A1 | Each specified transition and illegal-event case tested |
| A3 | Replace object-identity matching and add request deduplication | A1 | Reconstructed objects correlate by IDs; conflicting duplicate rejected |
| B1 | Implement mock MCS, tool pickup/release and destination readiness/receipt simulators | A1 | Explicit route endpoints; one tool need creates one request; stale source/destination readiness blocks transfer |
| B2 | Implement fleet, dock and door simulators | A1 | Delayed results, faults and duplicate commands can be injected |
| C1 | Implement assignment policy and atomic reservations | A1 | Two requests cannot acquire the same AMR/bin/destination |
| C2 | Implement SQLite repositories and pending-command publishing | A1 | State/event/command atomicity; pending commands survive restart |
| C3 | Implement custody and location tracking | A1, C2 | Bin location, contents and stale/unknown observations queryable |
| D1 | Connect orchestrator through UML interfaces and agreed endpoint extensions | A2, A3, B1, B2, C1, C2, C3 | Storage-to-tool, tool-to-storage and tool-to-tool each complete simulated pickup, destination transfer and receipt |
| D2 | Implement deadlines, retries and incident recovery | D1 | Denied access, pickup timeout, confirmation timeout and uncertain transfer tested |
| D3 | Add MQTT transport behind adapters | A1, B1, B2 | Separate simulator processes use the same contracts |
| D4 | Add CLI for submission, status, history and recovery inspection | D1 | A teammate can run the documented demonstration |
| E1 | Restart reconciliation and fault demonstrations | D2, D3 | No blind repeated transfer; occupied resources remain reserved |
| E2 | Integrate EE/ME hardware one adapter at a time | E1 and agreed physical contracts | Measured signals, handoff evidence and physical demonstration |

Initial independent work can proceed on models/contracts, adapter design, simulator design and persistence design. Merge A1 early so contributors share the same types. Avoid concurrent incompatible edits to `middleware.py` by giving orchestration integration one owner per change.

## Required regression scenarios

- Successful storage-to-tool request through contents preparation, identification, assignment, collection, applicable door passage, destination transfer and receipt.
- Successful tool-to-storage request with source release and configured storage receipt; empty-bin readiness is checked only for a request explicitly requiring an empty bin.
- Successful tool-to-tool request with distinct tool IDs, source release and receiving-tool receipt; no implicit gantry command or storage fill prompt.
- Same-point transport requests and missing/stale source readiness cannot authorize collection.
- Moving before collection does not imply IN_TRANSIT; arrival alone does not imply DELIVERED.
- Wrong bin, tool, request, command or location cannot advance a request.
- Unknown, occupied or stale destination blocks authorization, including a readiness change after assignment.
- Door denied then granted resumes the correct pre/post-collection phase; exhausted retries fail.
- AMR blocked with reroute stays IN_TRANSIT; unmodeled blockage holds progression and raises an incident.
- Duplicate requests/events/commands do not repeat assignment, transfer or receipt effects.
- Two competing requests cannot reserve the same physical resource.
- Disconnect, delayed completion and application/controller restart preserve uncertainty and custody.
- A failed request does not release a physically occupied AMR or dock.
- Missing tool receipt causes the specified confirmation timeout.

## Existing skeleton gaps

The current middleware treats MOVING as collection, matches bin/tool objects by identity, overwrites duplicate request IDs, and lacks complete door recovery, timeout, persistent tracking and resource-release behavior. Its existing tests cover only a small subset of the target behavior. Update tests deliberately when introducing the more precise collection and destination-transfer events.

## Demonstration milestones

1. In-process simulated transport with complete event history for storage-to-tool, tool-to-storage and tool-to-tool scenarios.
2. Persistent delivery, inventory and reservation state with failure handling.
3. Separate MQTT-connected simulators, fault injection and restart reconciliation.
4. Physical signal and transfer demonstration with EE/ME, including measured timing.

Keep hardware timing values in named configuration settings. Document which are simulation defaults and which were measured or supplied by the sponsor. Empty-bin return requires a separate agreed scenario before it counts as complete.

## Contribution workflow

Use a branch per task and small pull requests. Include the task ID, changed behavior, interface/schema changes and relevant validation. Changes to UML state meaning or external message contracts must update the documentation and examples in the same pull request. Never present simulated results as physical acceptance evidence.
