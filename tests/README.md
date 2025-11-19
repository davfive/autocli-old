# Running Tests Locally

This document outlines the standard procedure for executing the project's test suite locally using **Python's built-in `unittest` framework**.

---

## Prerequisites

Before running the tests, ensure you have:

1.  **Python Environment:** Python 3.8+ installed.
2.  **Dependencies**: All project dependencies, including testing dependencies, installed in an editable environment:
    ```bash
    python3 -m pip install -e .[tests]
    ```
3.  **Project Structure:** The test files are located under the `tests/` directory, and example files are correctly organized under `examples/`.

---

## Execution Methods

### 1. Running All Tests (Recommended)

The most common way to run the entire suite is by using the `unittest` discovery mechanism from the project root. This command automatically finds all files named `test_*.py` within the `tests/` directory and executes them.

```bash
python3 -m unittest discover tests
```

### 2. Running a Single Test File

To focus on a specific area, such as the new example tests, you can target the individual file.

```bash
python3 -m unittest tests.test_examples
```

### 3. Running a Specific Test Method

If you are debugging a single failure, you can target a specific method within a test class.

```bash
python3 -m unittest tests.test_examples.TestExampleApp.test_greet_command_with_name
```

---

## Testing Examples (`test_examples.py`)

The `test_examples.py` file uses **`subprocess.run()`** to execute the example CLI applications (e.g., `examples/my_app/scripts/example_run.py`) as if they were being run from the command line.

This approach guarantees that:
* The tests are executing the actual application entry points.
* The entire dependency resolution and `autocli` parsing process is tested end-to-end.
* The output (stdout/stderr) and exit codes are correctly verified against expected behavior.

### Command Line Arguments for Verbosity

To see detailed information about which tests are running (helpful for CI pipelines or large suites), you can increase the verbosity level:

| Option | Verbosity | Description |
| :--- | :--- | :--- |
| **`-v`** | Level 1 | Shows the name of each test method before execution. |
| **`-vv`** | Level 2 | Shows the method name and docstring for each test. |

**Example:**

```bash
python3 -m unittest discover -v
```

---

## Troubleshooting

* **Import Errors:** If tests fail with `ModuleNotFoundError`, ensure you are executing the command from the **project root** and that all dependencies are installed.
* **Permissions:** If you encounter errors related to running scripts, ensure the example runner files have execute permissions (though they are typically run directly by the Python interpreter).
* **Path Issues:** The tests rely on `pathlib` to correctly locate files inside the `examples/` directory. If you move the project structure, these path assumptions may need adjustment.