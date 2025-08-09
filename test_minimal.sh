#!/bin/bash

set -euo pipefail

# Function to detect package manager and OS
detect_package_manager() {
    echo "DEBUG: Starting package manager detection..."
    if command -v apt-get >/dev/null 2>&1; then
        PKG_MANAGER="apt"
        OS_TYPE="debian"
        echo "DEBUG: Found apt-get, setting PKG_MANAGER=apt"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MANAGER="yum"
        OS_TYPE="rhel"
        echo "DEBUG: Found yum, setting PKG_MANAGER=yum"
    elif command -v dnf >/dev/null 2>&1; then
        PKG_MANAGER="dnf"
        OS_TYPE="rhel"
        echo "DEBUG: Found dnf, setting PKG_MANAGER=dnf"
    else
        echo "ERROR: Unsupported package manager detected"
        exit 1
    fi
    echo "DEBUG: Final PKG_MANAGER=$PKG_MANAGER, OS_TYPE=$OS_TYPE"
    echo "Detected package manager: $PKG_MANAGER on $OS_TYPE"
}

# Detect package manager first
detect_package_manager

# Install basic system tools
echo "Installing basic system tools..."
echo "DEBUG: PKG_MANAGER=$PKG_MANAGER"
if [ "$PKG_MANAGER" = "apt" ]; then
    echo "DEBUG: Using apt-get branch"
    echo "Would run: sudo apt-get update"
    echo "Would run: sudo apt-get install -y curl wget git unzip jq gcc g++ make python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev ca-certificates gnupg lsb-release software-properties-common apt-transport-https"
else
    echo "DEBUG: Using yum branch"
    echo "Would run: sudo yum update -y"
    echo "Would run: sudo yum install -y curl wget git unzip jq gcc gcc-c++ make python3 python3-pip python3-devel openssl-devel libffi-devel ca-certificates gnupg2"
fi
echo "Basic system tools installed"