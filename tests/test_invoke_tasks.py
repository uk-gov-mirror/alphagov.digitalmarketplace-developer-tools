from invoke import MockContext, Result

from dmdevtools.invoke_tasks import install_python_requirements


class TestInstallPythonRequirements:
    def test_it_installs_requirements_from_requirements_txt_if_present(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context)
        context.run.assert_called_with("pip-sync requirements.txt")

    def test_it_installs_requirements_from_requirements_dev_txt_if_present(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements-dev.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context)
        context.run.assert_called_with("pip-sync requirements-dev.txt")

    def test_it_installs_requirements_from_both_requirements_txt_requirements_dev_txt_if_present(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements.txt").touch()
        (tmp_path / "requirements-dev.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context)
        context.run.assert_called_with("pip-sync requirements.txt requirements-dev.txt")

    def test_it_does_not_install_from_requirements_dev_txt_if_dev_is_false(
        self, monkeypatch, tmp_path
    ):
        (tmp_path / "requirements.txt").touch()
        (tmp_path / "requirements-dev.txt").touch()
        monkeypatch.chdir(tmp_path)

        context = MockContext(run=Result())
        install_python_requirements(context, dev=False)
        context.run.assert_called_with("pip-sync requirements.txt")
