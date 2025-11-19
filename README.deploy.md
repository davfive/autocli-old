# Deployment Workflow Explained (GitHub Actions)

This document explains the Continuous Integration/Continuous Delivery (CI/CD) pipeline defined in `.github/workflows/deploy.yml`. This workflow is triggered automatically upon pushing a new tag starting with `v` (e.g., `git push v0.1.0`).

Our deployment strategy is highly controlled, utilizing two manual approval gates to ensure rigorous testing before any public release.

> ⚠️ **CRITICAL SETUP REQUIRED: MANUAL GATES**
> 
> The manual approval steps for deployment (TestPyPI and DeployGate_PyPiProd) will **NOT** pause and wait for approval (i.e., they will run automatically) unless you complete the setup detailed in the **[Required Environment Setup for Gating](#required-environment-setup-for-gating)** section below. This is a one-time configuration in GitHub Repository Settings.

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
  * **Gate 1 (`DeployGate_PyPiTest`):** This job is protected by the **`DeployGate_PyPiTest` environment** It will pause and require manual approval before execution.
  * **Action:** Once approved, the package is deployed to **TestPyPI** (`test.pypi.org`).
  * **Testing Mandate:** After deployment, the developer **must** manually install and test the package using:
    ```bash
    pip install --index-url [https://test.pypi.org/simple/](https://test.pypi.org/simple/) autocli
    ```

### 4. `deploy_pypi_prod` (Gated)

  * **Dependency:** Requires successful completion of `deploy_pypi_test`.
  * **Gate 2 (`DeployGate_PyPiProd`):** This job is protected by the **`DeployGate_PyPiProd` environment** It will pause and require a second manual approval before execution.
  * **Action:** Once approved, the package is deployed to **PyPI** (`pypi.org`), securing the name and making the package publicly available.
  * **Note:** This two-gate process ensures that only packages successfully validated on TestPyPI reach the DeployGate_PyPiProd index.

-----

## The Workflow Flow Summary

This table outlines the execution sequence, dependencies, and required manual gates:

| # | Job Name | Runs After | Gate / Approval | Result |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `build` | N/A | Automatic | Creates distribution artifacts. |
| 2 | `deploy_github_packages` | `build` | Automatic | Package published to GitHub Packages. |
| 3 | `deploy_pypi_test` | `deploy_github_packages` | **DeployGate_PyPiTest** | Package published to TestPyPI. |
| 4 | `deploy_pypi_prod` | `deploy_pypi_test` | **DeployGate_PyPiProd** | Package published to PyPI DeployGate_PyPiProd. |

**Workflow Summary Steps:**

1. `git push --tags`
2. `build` (Runs)
3. `deploy_github_packages` (Runs)
4. `deploy_pypi_test` (Pauses at `DeployGate_PyPiTest`)
5. **Approve DeployGate_PyPiTest** → `deploy_pypi_test` (Runs)
6. `deploy_pypi_prod` (Pauses at `DeployGate_PyPiProd`)
7. **Approve DeployGate_PyPiProd** → `deploy_pypi_prod` (Runs)

-----

## Required Environment Setup for Gating

For the workflow to **pause** and wait for a manual approval click (the "play button"), you must configure the corresponding **GitHub Environments** in your repository settings. The `deploy.yml` file references `DeployGate_PyPiTest` and `DeployGate_PyPiProd`, and they must be set up to require reviewers.

To enable the manual pausing behavior for these jobs, perform the following one-time setup:

1. **Navigate to Settings:** Go to your repository on GitHub and select **Settings**
2. **Find Environments:** In the left sidebar, click **Environments**
3. **Create/Configure `DeployGate_PyPiTest`:**
      * Click **New environment** and name it `DeployGate_PyPiTest` (or click on `DeployGate_PyPiTest` if it already exists).
      * Under **Deployment protection rules**, check the box for **Required reviewers**
      * Add yourself or the relevant team/user who should approve the TestPyPI deployment.
      * Click **Save protection rules**
4. **Create/Configure `DeployGate_PyPiProd`:**
      * Repeat the process for a new environment named **`DeployGate_PyPiProd`**
      * Under **Deployment protection rules**, check **Required reviewers**
      * Add the necessary approver(s).
      * Click **Save protection rules**

Once these environments are configured, the workflow jobs referencing them will automatically pause and require your manual approval before proceeding.
