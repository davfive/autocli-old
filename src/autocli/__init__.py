import pkgutil
import sys
import argparse
import typing as t
import importlib
import types

# Define the expected types for command modules
CommandModule = types.ModuleType


def create_command_parser(
    package_module: CommandModule, *args, **kwargs
) -> argparse.ArgumentParser:
    """
    Creates the main ArgumentParser, dynamically discovers and registers all
    subcommands from the specified command package module.

    Subcommands are discovered recursively based on file names separated by '__'.
    Example: 'user__add.py' becomes 'user add'.

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

    pkg = package_module
    pkg_name = pkg.__name__

    # Basic check to ensure it is a package we can scan
    if not hasattr(pkg, "__path__"):
        sys.exit(
            f"Error: Provided object '{pkg_name}' is not a valid package/namespace to scan."
        )

    # 2. Scan the package for modules
    for _, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        # We only care about file modules, not nested subpackages or __init__
        if ispkg or name == "__init__":
            continue

        # Split the filename (e.g., 'user__add' -> ['user', 'add'])
        parts = name.split("__")

        try:
            # 3. Import the module dynamically
            module = importlib.import_module(f"{pkg_name}.{name}")

            # 4. Enforce required functions
            if not hasattr(module, "autocli_setup_parser") or not hasattr(
                module, "run_command"
            ):
                print(
                    f"Warning: Module {name} skipped (missing autocli_setup_parser or run_command).",
                    file=sys.stderr,
                )
                continue

            # 5. Build the command group hierarchy (e.g., creating 'user' group before 'add' command)
            parent_key = ""
            for part in parts[:-1]:
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

            # 6. Register the final command (the last part of the filename)
            final_target = targets[parent_key]

            # The command module must call final_target.add_parser() and attach
            # the run_command function as a default.
            module.autocli_setup_parser(final_target, parts[-1])

        except Exception as e:
            print(f"Error processing module {name}: {e}", file=sys.stderr)

    return parser
