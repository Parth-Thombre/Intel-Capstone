"""Smoke tests for the installed package and its nonblocking startup contract."""

import os
import subprocess
import sys

import pytest

from capstone.config import AppConfig
from capstone.main import build_application, main
from capstone.middleware.middleware import Middleware
from capstone.models.enums import AMRStatus
from capstone.simulators.simulated import (
    SimulatedFleetManager,
    SimulatedGantry,
    SimulatedMCS,
    SimulatedOperatorInterface,
)


@pytest.fixture
def process_environment():
    """Do not let a developer's local startup settings alter smoke-test results."""
    environment = os.environ.copy()
    environment.pop("CAPSTONE_MODE", None)
    environment.pop("CAPSTONE_LOG_LEVEL", None)
    return environment


@pytest.fixture
def run_cli(tmp_path, process_environment):
    def run(*arguments, overrides=None):
        environment = dict(process_environment)
        environment.update(overrides or {})
        return subprocess.run(
            [sys.executable, "-I", "-B", "-m", "capstone", *arguments],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
        )

    return run


def test_installed_startup_check_exits_successfully(run_cli, tmp_path):
    result = run_cli("--check")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "Startup check passed (mode=simulation). No delivery tasks were started."
    )
    assert "startup check complete" in result.stderr
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "setting,value",
    [
        ("CAPSTONE_MODE", "hardware"),
        ("CAPSTONE_LOG_LEVEL", "invalid"),
        ("CAPSTONE_LOG_LEVEL", ""),
    ],
)
def test_invalid_configuration_exits_with_actionable_error(run_cli, setting, value):
    result = run_cli("--check", overrides={setting: value})
    assert result.returncode == 2
    assert "Configuration error:" in result.stderr and setting in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("arguments", [(), ("--help",)])
def test_help_exits_without_starting_application(run_cli, arguments):
    result = run_cli(*arguments)
    assert result.returncode == 0
    assert "--check" in result.stdout
    assert "Startup check passed" not in result.stdout
    assert result.stderr == ""


def test_unknown_option_is_rejected(run_cli):
    result = run_cli("--unknown")
    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr
    assert "Startup check passed" not in result.stdout


def test_logging_override_does_not_hide_success_result(run_cli):
    result = run_cli("--check", overrides={"CAPSTONE_LOG_LEVEL": "ERROR"})
    assert result.returncode == 0
    assert "Startup check passed" in result.stdout
    assert result.stderr == ""


def test_entry_points_and_package_boundaries_import_without_starting(tmp_path, process_environment):
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            "import capstone.main, capstone.__main__; "
            "import capstone.adapters, capstone.messaging, capstone.persistence; "
            "from capstone.interfaces.process_tool import ProcessToolInterface",
        ],
        cwd=tmp_path,
        env=process_environment,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == result.stderr == ""
    assert list(tmp_path.iterdir()) == []


def test_application_construction_issues_no_delivery_actions(monkeypatch):
    def unexpected_action(*args, **kwargs):
        pytest.fail("Application construction must not issue delivery actions.")

    for component, operation in [
        (Middleware, "receive_delivery_request"),
        (SimulatedFleetManager, "assign_task"),
        (SimulatedGantry, "place_bin_at_handoff"),
        (SimulatedOperatorInterface, "prompt_fill"),
        (SimulatedMCS, "receive_status"),
    ]:
        monkeypatch.setattr(component, operation, unexpected_action)

    config = AppConfig()
    application = build_application(config)
    middleware = application.middleware
    assert application.config == config
    assert middleware.requests == {}
    assert middleware.mcs.statuses == []
    assert middleware.gantry.placed == []
    assert middleware.operator_interface.prompts == []
    assert middleware.fleet_managers[0].amrs[0].status == AMRStatus.AVAILABLE


def test_invalid_configuration_prevents_dependency_construction(monkeypatch, capsys):
    def unexpected_construction(config):
        pytest.fail("Invalid configuration must stop dependency construction.")

    monkeypatch.setenv("CAPSTONE_MODE", "hardware")
    monkeypatch.setenv("CAPSTONE_LOG_LEVEL", "INFO")
    monkeypatch.setattr("capstone.main.build_application", unexpected_construction)
    assert main(["--check"]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "CAPSTONE_MODE" in output.err
