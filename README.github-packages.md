# Installing from GitHub Packages

The `autocli` package is published to the **GitHub Packages** registry for immediate access to development, patch, or pre-release versions. Installing from this private/authenticated registry requires a Personal Access Token (PAT).

---

## Prerequisites

### 1. Generate a Personal Access Token (PAT)

You must create a PAT with the following scope:

  * `read:packages`

You can create this token in your GitHub Settings: **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**.

**Note:** Treat your **PAT** like a password; do not share it or commit it to your repository.

### 2. Configure `pip`

There are two common ways to provide your credentials to `pip`:

#### Option A: Using Environment Variables (Recommended)

Set your GitHub Username and PAT as environment variables. `pip` will automatically pick these up when trying to access the GitHub registry.

```bash
# Replace 'YOUR_USERNAME' with your GitHub username
export GITHUB_USER="YOUR_USERNAME"

# Replace 'YOUR_PAT' with the PAT you generated with the 'read:packages' scope
export GITHUB_TOKEN="YOUR_PAT"