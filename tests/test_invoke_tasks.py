from invoke import MockContext, Result

import pytest

from dmdevtools.invoke_tasks import install_python_requirements


@pytest.fixture(autouse=True, params=[True, False])
def ci(request, monkeypatch):
    """Parametrize all tests for CI

    Tasks may behave differently depending on whether they are running on a
    Continuous Integration (CI) server (where the environment variable `CI`
    will be set).

    This fixture makes sure all tests exercise tasks in both scenarios.
    """
    if request.param is True:
        monkeypatch.setenv("CI", "true")
    elif request.param is False:
        monkeypatch.delenv("CI", raising=False)
    return request.param


class TestInstallPythonRequirements:
    def test_it_runs_pip_sync_if_local_pip_install_if_on_ci(self, ci):
        context = MockContext(run=Result())
        install_python_requirements(context)

        command = context.run.call_args[0][0]
        assert command.startswith("pip install" if ci else "pip-sync")

    def test_it_installs_requirements_from_requirements_txt_if_present(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context)

        command = context.run.call_args[0][0]
        assert "requirements.txt" in command

    def test_it_installs_requirements_from_requirements_dev_txt_if_present(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements-dev.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context)

        command = context.run.call_args[0][0]
        assert "requirements-dev.txt" in command

    def test_it_installs_requirements_from_both_requirements_txt_requirements_dev_txt_if_present(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements.txt").touch()
        (tmp_path / "requirements-dev.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context)

        command = context.run.call_args[0][0]
        assert "requirements.txt" in command
        assert "requirements-dev.txt" in command

    def test_it_does_not_install_from_requirements_dev_txt_if_dev_is_false(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements.txt").touch()
        (tmp_path / "requirements-dev.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context, dev=False)

        command = context.run.call_args[0][0]
        assert "requirements-dev.txt" not in command
