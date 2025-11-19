import argparse

# --- Required Functions for autocli ---


def autocli_setup_parser(subparsers: argparse._SubParsersAction, command_name: str):
    """
    Sets up the argument parser for this command.
    """
    # NOTE: We keep the help text minimal for these mock examples.
    parser = subparsers.add_parser(command_name, help=f"The {command_name} command.")

    # Add a required argument for testing execution proof
    parser.add_argument(
        "--test-value",
        type=str,
        required=True,
        help="A value required to confirm the command ran.",
    )

    # Crucial: Link the execution function to the parser
    parser.set_defaults(func=run_command)


def run_command(args: argparse.Namespace):
    """
    The function executed when the command is run.
    """
    print(f"SUCCESS: ran with value: {args.test_value}")  # for testing purposes
