#!/bin/bash

# NativeSeries - Netlify Environment Setup Script
# Version: 1.0.0
# This script helps set up environment variables for Netlify deployment

set -euo pipefail

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_section() {
    echo -e "${PURPLE}📋 $1${NC}"
    echo "=================================="
}

# Banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    NativeSeries                              ║"
echo "║              Netlify Environment Setup                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_section "Netlify Environment Variables Setup"

print_info "This script will help you set up environment variables for your Netlify deployment."
print_info "You'll need to provide your Vault credentials and database connection details."

echo

# Check if netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    print_warning "Netlify CLI not found. Installing..."
    npm install -g netlify-cli
    print_success "Netlify CLI installed"
fi

# Get user input
echo -e "${YELLOW}Please provide the following information:${NC}"
echo

# Vault Configuration
print_section "Vault Configuration"
read -p "Vault Address (default: http://44.204.193.107:8200): " VAULT_ADDR
VAULT_ADDR=${VAULT_ADDR:-"http://44.204.193.107:8200"}

read -p "Vault Role ID: " VAULT_ROLE_ID
if [ -z "$VAULT_ROLE_ID" ]; then
    print_warning "Vault Role ID is required for vault access"
    read -p "Vault Role ID: " VAULT_ROLE_ID
fi

read -p "Vault Secret ID: " VAULT_SECRET_ID
if [ -z "$VAULT_SECRET_ID" ]; then
    print_warning "Vault Secret ID is required for vault access"
    read -p "Vault Secret ID: " VAULT_SECRET_ID
fi

echo

# Database Configuration
print_section "Database Configuration"
read -p "MongoDB URI (default: mongodb://localhost:27017): " MONGO_URI
MONGO_URI=${MONGO_URI:-"mongodb://localhost:27017"}

read -p "Database Name (default: nativeseries): " DATABASE_NAME
DATABASE_NAME=${DATABASE_NAME:-"nativeseries"}

read -p "Collection Name (default: students): " COLLECTION_NAME
COLLECTION_NAME=${COLLECTION_NAME:-"students"}

echo

# Application Configuration
print_section "Application Configuration"
read -p "Secret Key (default: your-secret-key-here): " SECRET_KEY
SECRET_KEY=${SECRET_KEY:-"your-secret-key-here"}

read -p "Environment (default: production): " APP_ENV
APP_ENV=${APP_ENV:-"production"}

read -p "Debug Mode (true/false, default: false): " DEBUG
DEBUG=${DEBUG:-"false"}

echo

# Confirm settings
print_section "Configuration Summary"
echo "Vault Address: $VAULT_ADDR"
echo "Vault Role ID: ${VAULT_ROLE_ID:0:8}..."
echo "Vault Secret ID: ${VAULT_SECRET_ID:0:8}..."
echo "MongoDB URI: $MONGO_URI"
echo "Database Name: $DATABASE_NAME"
echo "Collection Name: $COLLECTION_NAME"
echo "Environment: $APP_ENV"
echo "Debug Mode: $DEBUG"
echo

read -p "Do you want to proceed with these settings? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    print_info "Setup cancelled"
    exit 0
fi

echo

# Set environment variables
print_section "Setting Netlify Environment Variables"

# Check if we're in a Netlify site
if [ ! -f "netlify.toml" ]; then
    print_error "netlify.toml not found. Please run this script from your project root."
    exit 1
fi

# Set environment variables using netlify CLI
print_info "Setting environment variables..."

netlify env:set VAULT_ADDR "$VAULT_ADDR"
netlify env:set VAULT_ROLE_ID "$VAULT_ROLE_ID"
netlify env:set VAULT_SECRET_ID "$VAULT_SECRET_ID"
netlify env:set MONGO_URI "$MONGO_URI"
netlify env:set DATABASE_NAME "$DATABASE_NAME"
netlify env:set COLLECTION_NAME "$COLLECTION_NAME"
netlify env:set SECRET_KEY "$SECRET_KEY"
netlify env:set APP_ENV "$APP_ENV"
netlify env:set DEBUG "$DEBUG"

print_success "Environment variables set successfully!"

echo

# Test vault connection
print_section "Testing Vault Connection"
print_info "Testing connection to Vault at $VAULT_ADDR..."

if curl -s "$VAULT_ADDR/v1/sys/health" > /dev/null; then
    print_success "Vault is accessible"
else
    print_warning "Could not connect to Vault. Please check your Vault address."
fi

echo

# Create .env file for local development
print_section "Creating Local Environment File"
cat > .env.local << EOF
# NativeSeries Local Environment Variables
# Copy these to your Netlify environment variables

# Vault Configuration
VAULT_ADDR=$VAULT_ADDR
VAULT_ROLE_ID=$VAULT_ROLE_ID
VAULT_SECRET_ID=$VAULT_SECRET_ID

# Database Configuration
MONGO_URI=$MONGO_URI
DATABASE_NAME=$DATABASE_NAME
COLLECTION_NAME=$COLLECTION_NAME

# Application Configuration
SECRET_KEY=$SECRET_KEY
APP_ENV=$APP_ENV
DEBUG=$DEBUG
EOF

print_success "Local environment file created: .env.local"
print_info "You can use this file for local development"

echo

# Final instructions
print_section "Next Steps"
print_info "1. Deploy your application to Netlify:"
echo "   netlify deploy --prod"
echo
print_info "2. Test your endpoints:"
echo "   - /api/database - Check database connection"
echo "   - /api/vault - Check vault status"
echo "   - /api/stats - Get database statistics"
echo
print_info "3. Monitor your deployment:"
echo "   netlify status"
echo

print_success "Netlify environment setup completed!"
print_info "Your application should now be able to access your database and vault."