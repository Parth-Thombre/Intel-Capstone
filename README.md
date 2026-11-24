# Capstone Middleware (skeleton)

Software-only simulation of the middleware between the MCS, fleet managers, door, gantry, operators and process tools.

The target transport scope includes storage handoff to process tool, process tool to storage handoff, and process tool to another process tool. All three use a delivery request with pickup and destination points. The current skeleton and operator demo do not yet implement complete workflows for all three routes.

Design docs (UML class, state machine, sequence diagram) go in `docs/`.

## Layout
- `src/capstone/models/`      data classes, one file per class, plus `enums.py`
- `src/capstone/middleware/`  `middleware.py` (receive_* operations), `request_state.py` (state machine), `message_translator.py`
- `src/capstone/interfaces/`  the outside parties as abstract classes the middleware calls
- `src/capstone/simulators/`  fake versions of those parties, for testing without the fab
- `tests/`                    pytest tests (state machine, translator, end-to-end delivery)

## Run the tests
    cd Intel-Capstone
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pytest


## Status
Skeleton only. The decision algorithm is a placeholder (first available AMR). Retry limits, timeouts,
message formats and the return trip for empty bins are TBD (see open questions in the design doc).

## Operator console demo
A console version of the operator interface (shows the fill prompt, accepts `done`). Run from the repo root:

    python3 demo_operator.py

Commands: `list`, `done [bin_id]`, `quit`. Code: `src/capstone/simulators/console_operator.py`.

### Roles (optional)
    python3 demo_operator.py filler        # bin filler: list, loaded
    python3 demo_operator.py technician    # tool technician: list, empty, request, refill

Operator messages follow the dictionary envelope in `docs/INTERFACES.md` (`operator.bin_loaded`,
`operator.bin_emptied`, `operator.material_requested`). Roles are a prototype setting, not real accounts.
## Architecture and coding plan

The repository currently contains a middleware skeleton. The documents below describe the target implementation and distinguish working prototype choices from unresolved physical interfaces.

- [Architecture and ownership](docs/ARCHITECTURE.md)
- [Message and interface contracts](docs/INTERFACES.md)
- [Implementation tasks and acceptance scenarios](docs/IMPLEMENTATION_PLAN.md)

Start with A1 (shared models/contracts), then implement the UML state machine and simulators. Preserve the existing UML-facing interfaces while adding transport, persistence and recovery behind them.

For a virtual environment named `.venv`, activate it with `source .venv/bin/activate` before running the existing tests.
