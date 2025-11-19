from pathlib import Path
from autocli import create_command_parser
import commands

SCRIPT_NAME = Path(__file__).stem


def main():
    parser = create_command_parser(commands, description=f"{SCRIPT_NAME}")
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()  # no subcommand provided


if __name__ == "__main__":
    main()
