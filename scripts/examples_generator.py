import os
import sys
from typing import Dict, Any

# --- Constants for Content Tags ---
EMPTY_CONTENT = 0
RUNPY_TEMPLATE = "examples_run.py"
CMDPY_TEMPLATE = "examples_cmd.py"

# Find the directory of the script being executed.
# This ensures that relative paths for templates are correctly resolved
# regardless of the current working directory (e.g., when run as ./scripts/examples_generator.py).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# --- File Structure Definition ---
# The value dictates the content source: 0 for empty, or the template filename string.
EXAMPLES_STRUCTURE: Dict[str, Any] = {
    # single_app
    "single_app/commands/__init__.py": EMPTY_CONTENT,
    "single_app/commands/report.py": CMDPY_TEMPLATE,
    "single_app/run.py": RUNPY_TEMPLATE,
    # dunder_app (Flat commands directory with dunder-separated files)
    "dunder_app/commands/__init__.py": EMPTY_CONTENT,
    "dunder_app/commands/service__db__connect.py": CMDPY_TEMPLATE,
    "dunder_app/commands/user__delete.py": CMDPY_TEMPLATE,
    "dunder_app/run.py": RUNPY_TEMPLATE,
    # dirs_app (Deeply nested commands directories)
    "dirs_app/commands/__init__.py": EMPTY_CONTENT,
    "dirs_app/commands/admin/__init__.py": EMPTY_CONTENT,
    "dirs_app/commands/admin/user/__init__.py": EMPTY_CONTENT,
    "dirs_app/commands/admin/user/list.py": CMDPY_TEMPLATE,
    "dirs_app/commands/data/__init__.py": EMPTY_CONTENT,
    "dirs_app/commands/data/get.py": CMDPY_TEMPLATE,
    "dirs_app/run.py": RUNPY_TEMPLATE,
    # mixed_app (Combination of nested directories and dunder-separated files)
    "mixed_app/commands/__init__.py": EMPTY_CONTENT,  # Root package __init__
    "mixed_app/commands/admin__db/__init__.py": EMPTY_CONTENT,
    "mixed_app/commands/admin__db/connect.py": CMDPY_TEMPLATE,
    "mixed_app/commands/settings/__init__.py": EMPTY_CONTENT,
    "mixed_app/commands/settings/config__get.py": CMDPY_TEMPLATE,
    "mixed_app/commands/user/__init__.py": EMPTY_CONTENT,
    "mixed_app/commands/user/add.py": CMDPY_TEMPLATE,
    "mixed_app/run.py": RUNPY_TEMPLATE,
}

# --- File Utility Functions ---


def read_template(template_name: str) -> str:
    """Reads the content of a template file, resolving the path relative to the script's directory."""

    # Construct the full path using the script's directory and the template filename
    filepath = os.path.join(SCRIPT_DIR, template_name)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Improved error message to help the user debug
        print(
            f"Error: Template file '{template_name}' not found at path: {filepath}",
            file=sys.stderr,
        )
        print(
            "Ensure 'examples_cmd.py' and 'examples_run.py' are in the same directory as the generator script.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def generate_structure(
    root_dir: str, templates: Dict[str, str], structure: Dict[str, Any]
):
    """
    Creates the application directory and populates it with nested files
    based on the provided structure dictionary and pre-read templates.
    """
    if os.path.exists(root_dir):
        print(
            f"Target directory '{root_dir}' exists. Creating/Overwriting files inside it."
        )
    else:
        try:
            os.makedirs(root_dir)
            print(f"Created root directory: '{root_dir}/'")
        except OSError as e:
            print(f"Error creating root directory {root_dir}: {e}", file=sys.stderr)
            sys.exit(1)

    for relative_path, content_tag in structure.items():
        filepath = os.path.join(root_dir, relative_path)
        dirpath = os.path.dirname(filepath)

        # 1. Ensure all parent directories exist
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        # 2. Determine content
        content = ""
        if content_tag == EMPTY_CONTENT:
            content = ""
        elif content_tag in templates:
            # content_tag is the string (e.g., 'examples_cmd.py'), used as the key for the templates dict
            content = templates[content_tag]
        else:
            print(
                f"Warning: Unknown content tag {content_tag} for {relative_path}. Writing empty file.",
                file=sys.stderr,
            )

        # 3. Write file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  - Created {filepath}")
        except Exception as e:
            print(f"Error writing file {filepath}: {e}", file=sys.stderr)
            sys.exit(1)

    print("\nGeneration complete! The 'examples/' directory is ready.")


if __name__ == "__main__":
    # 1. Read the content from the template files in the same directory as this script
    try:
        # We read the content using the string constant as the filename
        cmd_content = read_template(CMDPY_TEMPLATE)
        run_content = read_template(RUNPY_TEMPLATE)
    except Exception:
        # read_template handles the exit on error
        sys.exit(1)

    # 2. Map the content to the string template file names
    # The key is the template filename string, the value is the content string
    TEMPLATES: Dict[str, str] = {
        RUNPY_TEMPLATE: run_content,
        CMDPY_TEMPLATE: cmd_content,
    }

    # 3. Generate the application structure inside the 'examples' root directory
    generate_structure("examples", TEMPLATES, EXAMPLES_STRUCTURE)
