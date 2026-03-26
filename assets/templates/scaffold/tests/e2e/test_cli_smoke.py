from __future__ import annotations

import pytest
from typer.testing import CliRunner

from {{PYTHON_PACKAGE_NAME}}.cli.app import app


runner = CliRunner()


@pytest.mark.e2e
def test_cli_doctor_and_task_seed(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("{{ENV_PREFIX}}_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("{{ENV_PREFIX}}_LOGS_DIR", str(tmp_path / "logs"))

    seed_result = runner.invoke(app, ["task", "seed-demo"])
    assert seed_result.exit_code == 0
    assert "demo-bootstrap-task" in seed_result.stdout

    doctor_result = runner.invoke(app, ["doctor"])
    assert doctor_result.exit_code == 0
    assert "Harness status" in doctor_result.stdout
