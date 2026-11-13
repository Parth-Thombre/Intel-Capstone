# Capstone Middleware (skeleton)

Software-only simulation of the middleware between the MCS, fleet managers, door, gantry, operators and process tools.
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

## Architecture and coding plan

The repository currently contains a middleware skeleton. The documents below describe the target implementation and distinguish working prototype choices from unresolved physical interfaces.

- [Architecture and ownership](docs/ARCHITECTURE.md)
- [Message and interface contracts](docs/INTERFACES.md)
- [Implementation tasks and acceptance scenarios](docs/IMPLEMENTATION_PLAN.md)

Start with A1 (shared models/contracts), then implement the UML state machine and simulators. Preserve the existing UML-facing interfaces while adding transport, persistence and recovery behind them.

For a virtual environment named `.venv`, activate it with `source .venv/bin/activate` before running the existing tests.
