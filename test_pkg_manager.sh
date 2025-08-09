#!/bin/bash

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

# Test the detection
detect_package_manager
echo "PKG_MANAGER=$PKG_MANAGER"
echo "OS_TYPE=$OS_TYPE"

# Test the conditional
if [ "$PKG_MANAGER" = "apt" ]; then
    echo "Would use apt-get"
else
    echo "Would use yum/dnf"
fi