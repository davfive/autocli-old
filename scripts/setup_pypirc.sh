#!/bin/bash

# --- Script to Configure ~/.pypirc for GitHub Packages ---
# This script uses the GitHub CLI (gh) to authenticate for fetching packages.
# It requires the user to be authenticated with 'gh auth login'.

REPO_OWNER="davfive" # The GitHub user/organization that owns the repository (crucial for the index URL structure)
DEFAULT_PYPIRC="$HOME/.pypirc"
PROJECT_PYPIRC="$HOME/.pypirc.autocli.rc"

# Determine the target file path
if [ -f "$DEFAULT_PYPIRC" ]; then
    PYPIRC_FILE="$PROJECT_PYPIRC"
    WRITE_MODE="SAFE"
else
    PYPIRC_FILE="$DEFAULT_PYPIRC"
    WRITE_MODE="DEFAULT"
fi


echo "================================================="
echo "  GitHub Packages (.pypirc) Configuration Script"
echo "================================================="

# 1. Check for GitHub CLI installation
if ! command -v gh &> /dev/null
then
    echo "ERROR: GitHub CLI (gh) is not installed."
    echo "Please install it (e.g., 'brew install gh') and run 'gh auth login'."
    exit 1
fi

# 2. Ensure user is authenticated
if ! gh auth status &> /dev/null
then
    echo "ERROR: You are not logged in with the GitHub CLI."
    echo "Please run 'gh auth login' first."
    exit 1
fi

# 3. Refresh token scope to include 'read:packages'
echo "Checking/refreshing GitHub CLI token scope (requires 'read:packages')..."
gh auth refresh -h github.com -s read:packages

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to refresh authentication scope."
    echo "Please ensure you approved the 'read:packages' permission in the browser."
    exit 1
fi

# 4. Retrieve necessary credentials
GH_USERNAME=$(gh api user -q .login)
GH_PACKAGE_TOKEN=$(gh auth token)

if [ -z "$GH_USERNAME" ] || [ -z "$GH_PACKAGE_TOKEN" ]; then
    echo "ERROR: Could not retrieve GitHub username or token."
    exit 1
fi

echo "Successfully retrieved credentials for user: $GH_USERNAME"
echo "Target configuration file: $PYPIRC_FILE"
echo " "

# 5. Define the configuration block
CONFIG_BLOCK="
[distutils]
index-servers = 
    github

[github]
repository: https://pypi.pkg.github.com/$REPO_OWNER/
username: $GH_USERNAME
password: $GH_PACKAGE_TOKEN
"

# 6. Append the new configuration to the determined file
echo "$CONFIG_BLOCK" > "$PYPIRC_FILE" # Use > to overwrite/create the new file, ensuring it's clean.

# 7. CRITICAL SECURITY STEP: Set permissions to 600 (read/write by owner only)
echo "Setting file permissions to 600..."
chmod 600 "$PYPIRC_FILE"

echo "-------------------------------------------------"
if [ "$WRITE_MODE" == "SAFE" ]; then
    echo "SUCCESS: Configuration saved to project-specific file: $PYPIRC_FILE"
    echo ""
    echo "ACTION REQUIRED: Since you already have a $DEFAULT_PYPIRC file,"
    echo "you must manually copy the [github] block from $PYPIRC_FILE"
    echo "and append it to your primary $DEFAULT_PYPIRC file."
else
    echo "SUCCESS: Your primary configuration file $PYPIRC_FILE has been created."
fi
echo ""
echo "You can now install the package using:"
echo "pip install autocli --index-url https://pypi.pkg.github.com/$REPO_OWNER/simple/"
echo "-------------------------------------------------"

# Ensure the script is executable
chmod +x scripts/setup_pypirc.sh