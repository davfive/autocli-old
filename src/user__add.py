import argparse
import sys

# --- Required Functions for autocli ---


def autocli_setup_parser(subparsers: argparse._SubParsersAction, command_name: str):
    """
    Sets up the argument parser for the specific command (user add).

    Args:
        subparsers: The object to which this command's parser should be added.
        command_name: The name of the command (e.g., 'add').
    """
    parser = subparsers.add_parser(command_name, help="Adds a new user to the system.")

    # Define arguments for the 'user add' command
    parser.add_argument(
        "username", type=str, help="The unique identifier for the new user."
    )
    parser.add_argument(
        "-e", "--email", type=str, required=True, help="The user's email address."
    )
    parser.add_argument(
        "--admin", action="store_true", help="Grant administrator privileges."
    )

    # Crucial: Link the execution function to the parser
    parser.set_defaults(func=run_command)


def run_command(args: argparse.Namespace):
    """
    The function executed when the 'user add' command is run.

    Args:
        args: The parsed arguments from the command line.
    """
    print(f"--- Running Command: user {args.cmd} ---")

    # Command Logic starts here
    status = "Admin" if args.admin else "Standard"

    print(f"Processing new user: {args.username}")
    print(f"Email: {args.email}")
    print(f"Status: {status}")

    if args.username == "erroruser":
        sys.exit("Error: Username reserved or invalid.")

    print(f"Success: User '{args.username}' has been successfully created.")


# --- Example Runner (Optional, for local testing) ---

# Note: In a real app, you would have a main script that uses create_command_parser.
# This section is just for demonstrating the file's content.
if __name__ == "__main__":
    # This is not how autocli runs it, but shows what func=run_command does.
    print("This module is designed to be run via the main autocli parser.")
