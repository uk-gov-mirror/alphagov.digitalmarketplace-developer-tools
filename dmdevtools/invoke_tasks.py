import os
import venv
from pathlib import Path
from typing import List

from invoke import Collection, task


os.environ.setdefault("DM_ENVIRONMENT", "development")


@task
def show_environment(c):
    """Show Digital Marketplace environment variables in use"""
    print("Environment variables in use:")
    for envvar in os.environ:
        if envvar.startswith("DM_"):
            print(f"{envvar}={os.environ[envvar]}")


@task
def virtualenv(c):
    if not os.getenv("VIRTUAL_ENV") and not Path("venv").exists():
        print("\033[1;37mcreating virtualenv at `venv`\033[0m")
        venv.create("venv", with_pip=True)

    c.virtual_env = Path(os.getenv("VIRTUAL_ENV", "venv"))

    venv_path = c.virtual_env.resolve() / "bin"
    print(f"\033[1;37mentering virtualenv at `{c.virtual_env}`\033[0m")
    os.environ["PATH"] = f"{venv_path}"


@task(virtualenv, aliases=["upgrade-pip"])
def install_pip_tools(c):
    c.run("pip install --upgrade pip wheel")

    pip_sync_installed = c.run("pip show pip-tools", warn=True, hide=True).ok
    if not pip_sync_installed:
        c.run("pip install pip-tools")


def install_python_requirements(c, dev: bool = True):
    requirements_files: List[Path]
    if dev:
        requirements_files = list(Path().glob("requirements*.txt"))
    else:
        requirements_files = [Path("requirements.txt")]

    c.run(f"pip-sync {' '.join(map(str, requirements_files))}")


@task(virtualenv, install_pip_tools)
def requirements(c):
    """Install python requirements"""
    install_python_requirements(c, dev=False)


@task(virtualenv, install_pip_tools)
def requirements_dev(c):
    """Install python app development requirements"""
    install_python_requirements(c, dev=True)


@task(virtualenv, requirements_dev)
def freeze_requirements(c):
    """Save python dependency tree in requirements files"""
    if Path("requirements.in").exists():
        c.run("pip-compile requirements.in")
    if Path("requirements-dev.in").exists():
        c.run("pip-compile requirements-dev.in")


@task
def npm_install(c):
    """Install node.js dependencies"""
    if os.getenv("CI") == "true":
        # On CI/GitHub Actions, install with a clean slate
        # (https://docs.npmjs.com/cli/ci.html)
        #
        # If dependencies in the package lock do not match those in package.json,
        # npm ci will exit with an error, instead of updating the package lockfile.
        #
        # If node_modules already exists, it will be removed.
        c.run("npm ci")
    else:
        # On developer machine, install without updating package.json or
        # package-lock.json.
        #
        # We want to save our disk drives and avoid reinstalling everything everytime,
        # but we also want to avoid updating package lock files without realising it,
        # so we add the `--no-save` option.
        c.run("npm install --no-save")


@task(npm_install)
def frontend_build(c, gulp_environment=""):
    """Build frontend assets using node.js"""
    if not Path("gulpfile.js").exists:
        c.run("npm run build")
        return

    if not gulp_environment:
        gulp_environment = (
            "development"
            if os.environ["DM_ENVIRONMENT"] == "development"
            else "production"
        )

    c.run(f"npm run --silent frontend-build:{gulp_environment}")


@task(virtualenv, requirements_dev)
def test_flake8(c):
    """Run python code linter"""
    c.run("flake8 .")


@task(virtualenv, requirements_dev)
def test_mypy(c):
    """Run python code linter"""
    c.run("mypy")  # requires mypy.ini


@task(virtualenv, requirements_dev, aliases=["test-unit"])
def test_python(c, pytest_args=""):
    """Run python unit tests"""
    c.run(f"pytest {pytest_args}")


@task(frontend_build)
def test_javascript(c):
    """Run node.js tests"""
    c.run("npm test")


@task
def docker_build(c, release_name=""):
    """Build docker image for app"""
    if not release_name:
        release_name = c.run("git describe", hide=True).stdout.strip()

    repo_name = Path.cwd().name.replace("-", "/", 1)

    print(f"Building a docker image for {repo_name}:{release_name}...")

    c.run(f"docker build -t {repo_name} --build-arg release_name={release_name} .")
    c.run(f"docker tag {repo_name} {repo_name}:{release_name}")


@task
def docker_push(c, release_name=""):
    """Push docker image for app to Docker Hub"""
    if not release_name:
        release_name = c.run("git describe", hide=True).stdout.strip()

    repo_name = Path.cwd().name.replace("-", "/", 1)

    c.run(f"docker push {repo_name}:{release_name}")


@task(show_environment, virtualenv)
def run_app(c):
    """Run app"""
    c.run("flask run")


# Create collections for each kind of repo
# This probably isn't the best way to do this,
# but it seems to work.
_common_tasks = [
    virtualenv,
    install_pip_tools,
    requirements,
    requirements_dev,
    freeze_requirements,
    test_flake8,
    test_mypy,
    test_python,
    show_environment,
]
_common_app_tasks = [
    *_common_tasks,
    run_app,
    docker_build,
    docker_push,
]
_common_configuration = {
    "run": {"echo": True, "pty": True}  # set commands to echo like in Make by default
}


def _Collection(*args, **kwargs):
    c = Collection(*args, **kwargs)
    c.configure(_common_configuration)
    return c


def _empty_task(*args, name, doc=None, **kwargs):
    """Create a task that just calls other tasks"""
    f = lambda c: None  # noqa: E731
    f.__name__ = name
    if doc:
        f.__doc__ = doc
    return task(pre=list(args), **kwargs)(f)


library_tasks = _Collection(
    *_common_tasks,
    _empty_task(test_flake8, test_python, name="test", doc="Run all tests"),
)

api_app_tasks = _Collection(
    *_common_app_tasks,
    _empty_task(requirements, run_app, name="run-all", doc="Build and run app"),
    _empty_task(test_flake8, test_python, name="test", doc="Run all tests"),
)

frontend_app_tasks = _Collection(
    *_common_app_tasks,
    npm_install,
    frontend_build,
    _empty_task(
        requirements,
        npm_install,
        frontend_build,
        run_app,
        name="run-all",
        doc="Build and run app",
    ),
    _empty_task(
        show_environment,
        frontend_build,
        test_flake8,
        test_python,
        test_javascript,
        name="test",
    ),
)
