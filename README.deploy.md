# Deployment Workflow Explained (GitHub Actions)

This document explains the Continuous Integration/Continuous Delivery (CI/CD) pipeline defined in `.github/workflows/deploy.yml`. This workflow is triggered automatically upon pushing a new tag starting with `v` (e.g., `git push v0.1.0`).

Our deployment strategy is highly controlled, utilizing two manual approval gates to ensure rigorous testing before any public release.

## 4-Stage Deployment Pipeline

The workflow consists of four sequential jobs, each dependent on the successful completion of the previous job:

### 1. `build`

  * **Purpose:** The initial, automatic step. It installs the Python `build` package and compiles the source code into standard Python distribution formats (`.whl` and `.tar.gz`) based on the `pyproject.toml` configuration.
  * **Output:** The compiled distribution files are saved as a GitHub Artifact named `python-package-distributions` for use by subsequent jobs.

### 2. `deploy_github_packages`

  * **Purpose:** Publishes the built package to the GitHub Packages registry.
  * **Rationale:** This serves as an immediate, versioned backup and allows for quick retrieval and testing of patch releases or pre-release features without hitting public indices. This step is fully automatic.

### 3. `deploy_pypi_test` (Gated)

  * **Dependency:** Requires successful completion of `deploy_github_packages`.
  * **Gate 1 (`TestGate`):** This job is protected by the **`TestGate` environment**. It will pause and require manual approval before execution.
  * **Action:** Once approved, the package is deployed to **TestPyPI** (`test.pypi.org`).
  * **Testing Mandate:** After deployment, the developer **must** manually install and test the package using:
    ```bash
    pip install --index-url [https://test.pypi.org/simple/](https://test.pypi.org/simple/) autocli
    ```

### 4. `deploy_pypi_prod` (Gated)

  * **Dependency:** Requires successful completion of `deploy_pypi_test`.
  * **Gate 2 (`Production`):** This job is protected by the **`Production` environment**. It will pause and require a second manual approval before execution.
  * **Action:** Once approved, the package is deployed to **PyPI** (`pypi.org`), securing the name and making the package publicly available.
  * **Note:** This two-gate process ensures that only packages successfully validated on TestPyPI reach the production index.

-----

## The Workflow Flow Summary

This table outlines the execution sequence, dependencies, and required manual gates:

| # | Job Name | Runs After | Gate / Approval | Result |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `build` | N/A | Automatic | Creates distribution artifacts. |
| 2 | `deploy_github_packages` | `build` | Automatic | Package published to GitHub Packages. |
| 3 | `deploy_pypi_test` | `deploy_github_packages` | **Manual Gate 1 (TestGate)** | Package published to TestPyPI. |
| 4 | `deploy_pypi_prod` | `deploy_pypi_test` | **Manual Gate 2 (Production)** |