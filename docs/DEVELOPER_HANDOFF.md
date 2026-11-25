# Implementation Skeleton Developer Handoff

## Start development

Check out the branch containing the skeleton changes and follow the [README development setup](../README.md#development-setup) to create a fresh Python 3.12 environment and install the editable development package. The environment is local to each developer; never commit it.

From the repository root with that environment activated:

```bash
python --version
python -m pip check
python -m capstone --check
python -m pytest
```

Python should report 3.12.x for the team baseline. The startup command should print `Startup check passed (mode=simulation). No delivery tasks were started.` and exit with code 0. INFO logging on stderr is normal. The tests should pass; the check constructs in-memory dependencies and exits rather than running a delivery service.

To run only the startup smoke tests:

```bash
python -m pytest tests/test_startup.py -q
```

The subprocess tests run outside the repository and use isolated Python mode, so they require the package to be installed in the interpreter running pytest. They intentionally do not rely on a source-directory PYTHONPATH override. Each subprocess has a timeout to detect a startup command that fails to exit.

## Available foundation

| Area | Available now | Next implementation work |
| --- | --- | --- |
| Packaging | Editable installation, Python requirement and development dependencies | Keep dependencies in pyproject.toml as modules are added |
| Configuration | Immutable simulation/log-level settings and validation | Add settings only when a component uses them |
| Startup | Module entry point, simulation composition, logging, success/error exit behavior | Service lifecycle and additional dependency wiring |
| Interfaces | Existing UML contracts and abstract tool pickup/delivery requests | Concrete adapters and shared event schemas |
| Package boundaries | Importable adapters, messaging and persistence packages | Protocol translations, queued transport and transactional repositories |
| Operator prototype | Filler/technician console commands and basic operator message validation | Integration with refined workflow and authenticated identities if required |
| Transport scope | Documented storage-to-tool, tool-to-storage and tool-to-tool contracts | End-to-end route execution and physical evidence |

The existing middleware still uses simplified movement/arrival signals, object-identity matching and in-memory request storage. The startup check does not establish UML workflow conformance, hardware readiness or a successful physical transfer. The [implementation plan](IMPLEMENTATION_PLAN.md) records the remaining work and acceptance scenarios.

## Choose a module

- Shared contracts: implement typed commands/events and stable IDs under `models` (A1).
- Workflow: implement guarded transitions, correlation and duplicate-request handling under `middleware` (A2/A3).
- Simulation: extend `simulators` with source readiness/release, destination acceptance and fault events (B1/B2).
- Integrations: translate external protocols in `adapters`; keep network transport and routing in `messaging`.
- Storage: implement transaction-backed repositories and custody tracking in `persistence` (C2/C3).

The IDs above are documentation work packages, not automatically created Jira or GitHub issues. Coordinate ownership before changing shared models or `middleware.py`. Read [interface contracts](INTERFACES.md) before implementing a sender or receiver.

## Before submitting a change

Run the startup check and the relevant tests, then the complete suite when shared behavior changes. Include changed behavior and validation in the pull request. Update contracts and examples when interfaces change. Keep unimplemented operations explicit and do not start connections, background workers or file creation from package imports.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Python 3.6 or `datetime.fromisoformat` failure | Recreate the environment with Python 3.12 and select it in VS Code |
| `No module named capstone` | Use the intended environment and run `python -m pip install -e ".[dev]"` from the repository root |
| pytest cannot import the package | Use `python -m pytest` from the same environment used for installation |
| Startup exits with code 2 and a setting name | Correct or unset that CAPSTONE environment variable; empty values are invalid |
| Startup prints help | Pass `--check`; a persistent service command is not implemented |
| MQTT/database functionality is unavailable | Those packages are placeholders awaiting implementation; startup does not connect them |
