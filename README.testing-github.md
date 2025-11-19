# Testing GitHub Packages Installation

The `autocli` package is published to the GitHub Packages registry (`pypi.pkg.github.com/davfive/`) for access to development and pre-release distributions. Installation requires authenticated access via a Personal Access Token (PAT).

We utilize the **GitHub CLI (`gh`)** for secure, temporary credential management, avoiding the need for manual PAT generation.

-----

## 1. Prerequisites and Authentication

Ensure the GitHub CLI (`gh`) is installed and authenticated:

```bash
# Install (e.g., via Homebrew on macOS)
brew install gh

# Authenticate and set up the session
# Follow the browser prompts to log in.
gh auth login
```

## 2. Configure Local Environment (`~/.pypirc`)

The `setup_pypirc.sh` script handles token generation, scope validation, and configuration of Python's registry file (`.pypirc`).

This script ensures your active `gh` token has the necessary `read:packages` scope and securely inserts your credentials.

```bash
# Set executable permission and run
chmod +x scripts/setup_pypirc.sh
./scripts/setup_pypirc.sh
```

### Script Output Handling

The script manages existing configuration files non-destructively:

  * **No existing `~/.pypirc`:** Configuration is written directly to `~/.pypirc`.
  * **Existing `~/.pypirc`:** Configuration is written to a dedicated file, `~/.pypirc.autocli.rc`. If this occurs, you must **manually merge** the generated `[github]` block into your primary `~/.pypirc` file to enable the simple `pip install` command.

-----

## 3. Installation

Once the configuration is in place, install the package using the registered index URL:

```bash
pip install autocli --index-url https://pypi.pkg.github.com/davfive/simple/
```