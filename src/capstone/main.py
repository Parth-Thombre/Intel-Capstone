"""Compose the simulation skeleton and expose a nonblocking startup check."""

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
import logging
import sys

from .config import AppConfig, ConfigurationError, load_config
from .middleware.middleware import Middleware
from .models.amr import AMR
from .simulators.simulated import (
    SimulatedFleetManager,
    SimulatedGantry,
    SimulatedMCS,
    SimulatedOperatorInterface,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Application:
    """Constructed dependencies; creating this object does not run a delivery."""

    config: AppConfig
    middleware: Middleware


def build_application(config: AppConfig) -> Application:
    """Construct in-memory simulation components without submitting any tasks.

    The single AMR is a prototype fixture, not a discovered physical robot.
    Device connections and a service loop belong to later implementation work.
    """
    middleware = Middleware(
        mcs=SimulatedMCS(),
        fleet_managers=[SimulatedFleetManager([AMR("AMR_1")])],
        gantry=SimulatedGantry(),
        operator_interface=SimulatedOperatorInterface(),
    )
    return Application(config=config, middleware=middleware)


def main(argv: Sequence[str] | None = None) -> int:
    """Return zero for a successful check, or two for invalid configuration."""
    parser = argparse.ArgumentParser(
        prog="python -m capstone",
        description="Material delivery middleware simulation skeleton.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate configuration, construct simulated dependencies and exit",
    )
    args = parser.parse_args(argv)
    if not args.check:
        parser.print_help()
        return 0

    try:
        config = load_config()
    except ConfigurationError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    logging.basicConfig(
        level=config.log_level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    application = build_application(config)
    logger.info("Constructed simulation dependencies; startup check complete.")
    print(
        f"Startup check passed (mode={application.config.mode}). "
        "No delivery tasks were started."
    )
    return 0
