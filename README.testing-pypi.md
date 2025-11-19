# Package Validation on TestPyPI

This guide outlines the procedure for manually verifying the package distribution after a successful deployment to the TestPyPI registry (`test.pypi.org`). This verification is mandatory before approving the final production deployment.

-----

## 1. Prerequisites

This validation step is executed only after the `deploy_pypi_test` job in the `deploy.yml` workflow has successfully completed its run, following manual approval of the `TestGate` environment.

### Authentication Note

To fetch packages from TestPyPI, you generally require either a valid `~/.pypirc` file configured with TestPyPI credentials or manual authentication via environment variables. Assuming you have the `TEST_PYPI_API_TOKEN` available, the `pip install` command handles authentication via the index URL implicitly.

-----

## 2. Installation and Verification

Use the following command to explicitly pull and install the `autocli` package from the TestPyPI index.

```bash
# Command to install the latest version from TestPyPI
pip install autocli --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/
```

> **Note:** The `--extra-index-url https://pypi.org/simple/` is included as a best practice to ensure `pip` can resolve any third-party dependencies (`requirements`) that `autocli` may rely on, which are likely hosted only on the main PyPI index.

-----

## 3. Post-Installation Checks

After a successful installation, execute the following to verify the integrity and functionality of the deployed package:

### A. Version Check

Verify that the installed version matches the version tag pushed to the repository (e.g., `0.0.1` from `pyproject.toml`).

```bash
pip show autocli
# Expected output should show the correct Version:
# ...
# Version: 0.0.1
# ...
```

### B. Command Execution Test

Run an expected command to ensure the entry points and dynamic loading mechanism are functional.

```bash
autocli user add testuser --email test@example.com
# Expected: Success message confirming user creation.
```

### C. Error Path Test

Validate that error handling within a command module (e.g., `user__add.py`) functions as intended.

```bash
autocli user add erroruser --email invalid@example.com
# Expected: The error message defined in the run_command function.
```

## 4. Final Approval

If all installation and functional tests pass, the TestPyPI deployment is considered validated. Proceed to the GitHub Actions workflow, review the artifacts, and manually approve the **Production Gate** to initiate deployment to the main PyPI index.