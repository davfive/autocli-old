import os
import sys
import argparse
import typing as t
import importlib
import types
from pathlib import Path

# Define the expected types for command modules
CommandModule = types.ModuleType


def create_command_parser(
    package_module: CommandModule, *args, **kwargs
) -> argparse.ArgumentParser:
    """
    Creates the main ArgumentParser, dynamically discovers and registers all
    subcommands from the specified command package module.

    Subcommands are discovered recursively based on:
    1. Directory structure (e.g., 'user/add.py' becomes 'user add').
    2. File names separated by '__' (e.g., 'user__add.py' becomes 'user add').
    3. Both mixed (e.g., 'user/db__connect.py' becomes 'user db connect').

    Args:
        package_module: The package object (e.g., importlib.import_module('autocli.commands')).
        *args, **kwargs: Passed directly to argparse.ArgumentParser.

    Returns:
        A configured argparse.ArgumentParser instance.
    """

    # 1. Initialize the root parser
    parser = argparse.ArgumentParser(*args, **kwargs)

    # targets will map command group keys (e.g., '', 'user', 'user__db') to
    # their respective subparsers action objects.
    # '' is the root key.
    targets: t.Dict[str, argparse._SubParsersAction] = {}
    targets[""] = parser.add_subparsers(title="Commands", dest="cmd", required=True)

    pkg_name = package_module.__name__

    # Determine the physical directory path of the package
    if not hasattr(package_module, "__file__") or not package_module.__file__:
        sys.exit(
            f"Error: Could not determine physical path for package '{pkg_name}' to scan recursively."
        )

    pkg_dir = Path(package_module.__file__).parent
    if not pkg_dir.is_dir():
        sys.exit(f"Error: Package path '{pkg_dir}' is not a directory.")

    found_modules = []

    # 2. Recursively scan the package directory for command modules (*.py)
    for file_path in pkg_dir.rglob("*.py"):
        relative_path = file_path.relative_to(pkg_dir)
        if relative_path.name == "__init__.py":
            continue

        # Get the module name parts based on path and filename
        # Example 1: user/db/connect.py -> parts from dir ('user', 'db') + filename base ('connect')
        # Example 2: user__add.py -> no dir parts + filename base ('user', 'add')

        cmd_path_str = relative_path.with_suffix("").as_posix()
        cmd_parts = cmd_path_str.replace(os.sep, "__").split("__")
        import_name = cmd_path_str.replace(os.sep, ".")

        found_modules.append(
            {
                "command_parts": cmd_parts,
                "import_name": f"{pkg_name}.{import_name}",
            }
        )

    # 3. Import and Register all found modules
    for mod_info in found_modules:
        parts = mod_info["command_parts"]
        import_name = mod_info["import_name"]

        try:
            module = importlib.import_module(import_name)

            # Enforce required functions
            if not hasattr(module, "autocli_setup_parser") or not hasattr(
                module, "run_command"
            ):
                print(
                    f"Warning: Module {import_name} skipped (missing setup or run function).",
                    file=sys.stderr,
                )
                continue

            # Build the command group hierarchy dynamically
            parent_key = ""
            for part in parts[:-1]:
                # The key uses the original __ delimiter format for consistency in the targets dict
                current_key = f"{parent_key}{'__' if parent_key else ''}{part}"

                # If this group doesn't exist yet, create its subparser
                if current_key not in targets:
                    parent_parser = targets[parent_key].add_parser(
                        part, help=f"Subcommands for the '{part}' group"
                    )
                    targets[current_key] = parent_parser.add_subparsers(
                        dest=current_key, required=True
                    )
                parent_key = current_key

            # Register the final command (the last part of the parts list)
            final_target = targets[parent_key]

            # The command module must call final_target.add_parser() and attach
            # the run_command function as a default.
            module.autocli_setup_parser(final_target, parts[-1])

        except Exception as e:
            print(f"Error processing module {import_name}: {e}", file=sys.stderr)

    return parser
