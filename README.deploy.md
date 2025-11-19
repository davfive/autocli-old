# Deployment Workflow Explained (GitHub Actions)

This document explains the CI/CD pipeline defined in `.github/workflows/deploy.yml`. This workflow is triggered automatically upon pushing a new tag starting with `v` (e.g., `git push v0.1.0`).

-----

## 4-Stage Deployment Pipeline

The workflow consists of four sequential jobs:

### 1. `build`

  * **Purpose:** The initial, automatic step. It installs the Python `build` package and compiles the source code into standard Python distribution formats (`.whl` and `.tar.gz`) based on the `pyproject.toml` configuration.
  * **Output:** The compiled distribution files are saved as a GitHub Artifact named `python-package-distributions` for use by subsequent jobs.

### 2. `deploy_github_packages`

  * **Purpose:** Publishes the built package to the GitHub Packages registry.
  * **Rationale:** This serves as an immediate, versioned backup and allows for quick retrieval and testing of patch releases or pre-release features without hitting public indices. This step is fully automatic.

> **Test Gate 1:** Pause here to manually test the GitHub package (no automation yet). See [README.gitlab-packages.md](./README.gitlab-packages.md).
> 

### 3. `deploy_pypi_test` (Gated)
  * **Dependency:** Requires successful completion of `deploy_github_packages`.    
  * **Purpose:** Deploys package to [test.pypi.or](https://test.pypi.org/simple/autocli/).

> **Test Gate 2:** Pause here to manually test the package from test.pypige (no automation yet). See [README.gitlab-packages.md](./README.gitlab-packages.md).
> 

### 4. `deploy_pypi_prod` (Gated)

  * **Dependency:** Requires successful completion of `deploy_pypi_test`.
  * **Gate 2 (`Production`):** This job is protected by the **`Production` environment** . It will pause and require a second manual approval before execution.
  * **Action:** Once approved, the package is deployed to **PyPI** (`pypi.org`), securing the name and making the package publicly available.
  * **Note:** This