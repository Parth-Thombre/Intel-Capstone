"""Configuration behavior required before wiring application startup."""

from dataclasses import FrozenInstanceError

import pytest

from capstone.config import AppConfig, ConfigurationError, load_config


def test_missing_settings_use_simulation_defaults():
    assert load_config({}) == AppConfig(mode="simulation", log_level="INFO")


def test_loads_process_environment(monkeypatch):
    monkeypatch.setenv("CAPSTONE_MODE", "simulation")
    monkeypatch.setenv("CAPSTONE_LOG_LEVEL", "DEBUG")
    assert load_config().log_level == "DEBUG"


def test_explicit_mapping_is_isolated_from_process_environment(monkeypatch):
    monkeypatch.setenv("CAPSTONE_MODE", "hardware")
    monkeypatch.setenv("CAPSTONE_LOG_LEVEL", "invalid")
    assert load_config({}) == AppConfig()


def test_environment_is_normalized_without_being_modified():
    values = {"CAPSTONE_MODE": " Simulation ", "CAPSTONE_LOG_LEVEL": " debug "}
    original = dict(values)
    assert load_config(values) == AppConfig(mode="simulation", log_level="DEBUG")
    assert values == original


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_supported_logging_levels(level):
    assert load_config({"CAPSTONE_LOG_LEVEL": level}).log_level == level


@pytest.mark.parametrize("mode", ["hardware", "production", "", " "])
def test_unsupported_or_empty_mode_is_rejected(mode):
    with pytest.raises(ConfigurationError, match="CAPSTONE_MODE"):
        load_config({"CAPSTONE_MODE": mode})


@pytest.mark.parametrize("level", ["TRACE", "verbose", "", " "])
def test_invalid_or_empty_logging_level_is_rejected(level):
    with pytest.raises(ConfigurationError, match="CAPSTONE_LOG_LEVEL"):
        load_config({"CAPSTONE_LOG_LEVEL": level})


def test_direct_construction_cannot_bypass_mode_validation():
    with pytest.raises(ConfigurationError, match="CAPSTONE_MODE"):
        AppConfig(mode="hardware")


def test_direct_construction_cannot_bypass_logging_validation():
    with pytest.raises(ConfigurationError, match="CAPSTONE_LOG_LEVEL"):
        AppConfig(log_level="VERBOSE")


def test_configuration_is_immutable():
    config = load_config({})
    with pytest.raises(FrozenInstanceError):
        config.log_level = "DEBUG"
