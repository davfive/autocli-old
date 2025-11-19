import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from abc import ABC, abstractmethod


# --- GLOBAL PATHS ---

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"


def get_runner_script_path(app_name: str) -> Path:
    runner = EXAMPLES_DIR / app_name / "run.py"
    if not runner.exists():
        raise FileNotFoundError(f"Missing run.py for example app: {app_name}")
    return runner


# --- COMMAND DISCOVERY (commands/** only) ---


def discover_commands_for_app(app_root: Path) -> list[tuple[list[str], str]]:
    """
    Returns a list of tuples:
      (cli_args_list, test_method_suffix)

    cli_args_list: e.g. ["user", "reset_password"]
    test_method_suffix: e.g. "user__reset_password"
    """

    commands_dir = app_root / "commands"
    if not commands_dir.exists():
        return []

    discovered = []

    for path in commands_dir.rglob("*.py"):
        if path.name == "__init__.py":
            continue

        # Get the module name parts based on path and filename
        # Example 1: user/db/connect.py -> parts from dir ('user', 'db') + filename base ('connect')
        # Example 2: user__add.py -> no dir parts + filename base ('user', 'add')

        relative_path = path.relative_to(commands_dir)
        cmd_path_str = relative_path.with_suffix("").as_posix()
        test_suffix = cmd_path_str.replace(os.sep, "__")
        cli_args = test_suffix.split("__")

        discovered.append((cli_args, test_suffix))

    return discovered


# --- BASE CLASS ---


class BaseAppTest(ABC):
    APP_NAME = ""
    COMMANDS: list[tuple[list[str], str]] = []

    def setUp(self):
        super().setUp()
        self.app_root = EXAMPLES_DIR / self.APP_NAME
        self.runner = get_runner_script_path(self.APP_NAME)

        self._tempdir = TemporaryDirectory()
        self.tempdir = self._tempdir.name

    def tearDown(self):
        self._tempdir.cleanup()
        super().tearDown()

    def run_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(self.runner)] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.app_root),
            check=False,
        )


# --- DYNAMIC TEST GENERATION ---


def generate_tests():
    module = sys.modules[__name__]

    # Discover example apps
    apps = [
        d.name for d in EXAMPLES_DIR.iterdir() if d.is_dir() and (d / "run.py").exists()
    ]

    for app_name in apps:
        app_root = EXAMPLES_DIR / app_name
        commands = discover_commands_for_app(app_root)

        class_name = f"Test{app_name.replace('__', ' ').title().replace('_', '')}"

        attrs = {
            "APP_NAME": app_name,
            "COMMANDS": commands,
            "__module__": __name__,
        }

        # Create class first
        TestClass = type(class_name, (BaseAppTest, unittest.TestCase), attrs)

        # Dynamically generate one test per command
        for cli_args, suffix in commands:

            def make_test(cli_args, suffix):
                def test_method(self):
                    test_val = f"SUCCESS_TOKEN_FOR_{'_'.join(cli_args).upper()}"
                    full_args = cli_args + ["--test-value", test_val]
                    expected_fragment = f"ran with value: {test_val}"

                    result = self.run_cli(full_args)

                    if result.returncode != 0:
                        self.fail(
                            f"\n❌ Command returned nonzero exit code\n"
                            f"Command: {' '.join(full_args)}\n"
                            f"Return code: {result.returncode}\n\n"
                            f"STDERR:\n{result.stderr}\n"
                            f"STDOUT:\n{result.stdout}\n"
                        )

                    if expected_fragment not in result.stdout:
                        self.fail(
                            f"\n❌ Output mismatch\n"
                            f"Command: {' '.join(full_args)}\n\n"
                            f"Expected to contain:\n"
                            f"    {expected_fragment}\n\n"
                            f"Actual STDOUT:\n"
                            f"{result.stdout}\n"
                            f"Actual STDERR:\n"
                            f"{result.stderr}\n"
                        )

                return test_method

            test_name = f"test_{suffix}"
            setattr(TestClass, test_name, make_test(cli_args, suffix))

        setattr(module, class_name, TestClass)


generate_tests()
