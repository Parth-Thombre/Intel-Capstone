"""Validated startup settings; loading configuration performs no device or file I/O."""

from collections.abc import Mapping
from dataclasses import dataclass
import os


LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


class ConfigurationError(ValueError):
    """A startup setting is unsupported or invalid."""


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Settings for the simulation skeleton, independent of application startup."""

    mode: str = "simulation"
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        if self.mode != "simulation":
            raise ConfigurationError(
                "CAPSTONE_MODE must be 'simulation'; physical hardware mode is not implemented."
            )
        if self.log_level not in LOG_LEVELS:
            raise ConfigurationError(
                "CAPSTONE_LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR or CRITICAL."
            )


def load_config(environ: Mapping[str, str] | None = None) -> AppConfig:
    """Read settings from the environment, or exclusively from a supplied mapping.

    Missing settings use defaults. Explicitly empty settings are invalid. Values
    are trimmed and case-normalized without changing the supplied environment.
    """
    values = os.environ if environ is None else environ
    return AppConfig(
        mode=values.get("CAPSTONE_MODE", "simulation").strip().lower(),
        log_level=values.get("CAPSTONE_LOG_LEVEL", "INFO").strip().upper(),
    )
