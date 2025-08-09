#!/bin/bash

# NativeSeries - Direct System Cleanup
# Version: 1.0.0 - Direct cleanup without backup
# This script directly cleans the system without creating backups

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
HOSTNAME=$(hostname)

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_status() { echo -e "${GREEN}[✅ SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[⚠️  WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[❌ ERROR]${NC} $1"; }
print_info() { echo -e "${CYAN}[ℹ️  INFO]${NC} $1"; }

# Banner
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          🗑️  NativeSeries - Direct System Cleanup               ║"
echo "║              NO BACKUP - DIRECT ERASE                           ║"
echo "║              Target: ${HOSTNAME}                                 ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Confirmation
echo -e "${RED}⚠️  DANGER: This script will completely clean your system WITHOUT BACKUP! ⚠️${NC}"
echo ""
echo -e "${YELLOW}This script will:${NC}"
echo -e "${WHITE}  • Remove all Kubernetes clusters${NC}"
echo -e "${WHITE}  • Remove all Docker containers, images, and volumes${NC}"
echo -e "${WHITE}  • Remove all installed tools (kubectl, helm, kind, etc.)${NC}"
echo -e "${WHITE}  • Clean all network configurations${NC}"
echo -e "${WHITE}  • Remove all application data${NC}"
echo -e "${WHITE}  • Reset the system to a clean state${NC}"
echo -e "${RED}  • NO BACKUP WILL BE CREATED${NC}"
echo ""
echo -e "${RED}⚠️  ALL DATA WILL BE PERMANENTLY LOST! ⚠️${NC}"
echo ""
read -p "Are you absolutely sure? Type 'ERASE' to confirm: " -r
echo
if [[ ! $REPLY =~ ^ERASE$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Final confirmation
echo -e "${RED}⚠️  FINAL WARNING: This will permanently delete everything! ⚠️${NC}"
echo -e "${RED}⚠️  No backup will be created! ⚠️${NC}"
echo ""
read -p "Type 'PERMANENT' to proceed with direct cleanup: " -r
echo
if [[ ! $REPLY =~ ^PERMANENT$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# ============================================================================
# PHASE 1: KUBERNETES CLEANUP
# ============================================================================

print_section "PHASE 1: Cleaning Up Kubernetes"

# Cleanup Kubernetes
print_info "Cleaning up Kubernetes..."
if command -v kubectl >/dev/null 2>&1; then
    # Delete all resources from all namespaces
    for namespace in $(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo ""); do
        if [ -n "$namespace" ] && [ "$namespace" != "default" ] && [ "$namespace" != "kube-system" ] && [ "$namespace" != "kube-public" ]; then
            print_info "Deleting namespace: $namespace"
            kubectl delete namespace "$namespace" --timeout=60s 2>/dev/null || true
        fi
    done
    
    # Delete Kind clusters
    if command -v kind >/dev/null 2>&1; then
        for cluster in $(kind get clusters 2>/dev/null || echo ""); do
            if [ -n "$cluster" ]; then
                print_info "Deleting Kind cluster: $cluster"
                kind delete cluster --name "$cluster" 2>/dev/null || true
            fi
        done
    fi
    
    print_status "Kubernetes cleanup completed"
else
    print_warning "kubectl not found, skipping Kubernetes cleanup"
fi

# ============================================================================
# PHASE 2: DOCKER CLEANUP
# ============================================================================

print_section "PHASE 2: Cleaning Up Docker"

# Cleanup Docker
print_info "Cleaning up Docker..."
if command -v docker >/dev/null 2>&1; then
    # Stop all containers
    print_info "Stopping all Docker containers..."
    docker stop $(docker ps -aq) 2>/dev/null || true
    
    # Remove all containers
    print_info "Removing all Docker containers..."
    docker rm $(docker ps -aq) 2>/dev/null || true
    
    # Remove all images
    print_info "Removing all Docker images..."
    docker rmi $(docker images -q) 2>/dev/null || true
    
    # Remove all volumes
    print_info "Removing all Docker volumes..."
    docker volume rm $(docker volume ls -q) 2>/dev/null || true
    
    # Remove all networks (except default)
    print_info "Removing all Docker networks..."
    docker network rm $(docker network ls --format "{{.Name}}" | grep -v "bridge\|host\|none") 2>/dev/null || true
    
    # Prune everything
    print_info "Pruning Docker system..."
    docker system prune -af --volumes 2>/dev/null || true
    
    print_status "Docker cleanup completed"
else
    print_warning "Docker not found, skipping Docker cleanup"
fi

# ============================================================================
# PHASE 3: TOOLS CLEANUP
# ============================================================================

print_section "PHASE 3: Removing Installed Tools"

# Cleanup tools
print_info "Removing installed tools..."

# Remove Kind
if command -v kind >/dev/null 2>&1; then
    print_info "Removing Kind..."
    sudo rm -f /usr/local/bin/kind
    print_status "Kind removed"
fi

# Remove kubectl
if command -v kubectl >/dev/null 2>&1; then
    print_info "Removing kubectl..."
    sudo rm -f /usr/local/bin/kubectl
    print_status "kubectl removed"
fi

# Remove Helm
if command -v helm >/dev/null 2>&1; then
    print_info "Removing Helm..."
    sudo rm -f /usr/local/bin/helm
    print_status "Helm removed"
fi

print_status "Tools cleanup completed"

# ============================================================================
# PHASE 4: APPLICATION FILES CLEANUP
# ============================================================================

print_section "PHASE 4: Cleaning Up Application Files"

# Cleanup application files
print_info "Cleaning up application files..."

# Remove Python virtual environment
if [ -d "venv" ]; then
    print_info "Removing Python virtual environment..."
    rm -rf venv/
    print_status "Virtual environment removed"
fi

# Remove Python cache files
print_info "Removing Python cache files..."
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf __pycache__/ 2>/dev/null || true
rm -rf *.pyc 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove deployment files
if [ -d "deployment/production" ]; then
    print_info "Removing deployment files..."
    rm -rf deployment/production/
    print_status "Deployment files removed"
fi

# Remove infrastructure files
if [ -d "infra/kind" ]; then
    print_info "Removing infrastructure files..."
    rm -rf infra/kind/
    print_status "Infrastructure files removed"
fi

print_status "Application files cleanup completed"

# ============================================================================
# PHASE 5: TEMPORARY FILES CLEANUP
# ============================================================================

print_section "PHASE 5: Cleaning Up Temporary Files"

# Cleanup temporary files
print_info "Cleaning up temporary files..."

# Remove installation scripts
rm -f get-docker.sh 2>/dev/null || true
rm -f kind 2>/dev/null || true
rm -f kubectl 2>/dev/null || true

# Remove archive files
rm -f *.tar 2>/dev/null || true
rm -f *.tar.gz 2>/dev/null || true

# Remove log files
rm -f *.log 2>/dev/null || true

# Clean /tmp directory of NativeSeries files
find /tmp -name "*nativeseries*" -type f -delete 2>/dev/null || true
find /tmp -name "*nativeseries*" -type d -exec rm -rf {} + 2>/dev/null || true

print_status "Temporary files cleanup completed"

# ============================================================================
# PHASE 6: NETWORK CLEANUP
# ============================================================================

print_section "PHASE 6: Cleaning Up Network Configurations"

# Cleanup network configurations
print_info "Cleaning up network configurations..."

# Flush iptables
print_info "Flushing iptables..."
sudo iptables -F 2>/dev/null || true
sudo iptables -X 2>/dev/null || true
sudo iptables -t nat -F 2>/dev/null || true
sudo iptables -t nat -X 2>/dev/null || true

# Remove custom network interfaces
print_info "Removing custom network interfaces..."
for interface in $(ip link show | grep -E "docker|br-" | awk -F: '{print $2}' | tr -d ' '); do
    if [ -n "$interface" ]; then
        sudo ip link delete "$interface" 2>/dev/null || true
    fi
done

print_status "Network cleanup completed"

# ============================================================================
# PHASE 7: SYSTEM PACKAGES CLEANUP
# ============================================================================

print_section "PHASE 7: Cleaning Up System Packages"

# Cleanup system packages (optional)
print_info "Cleaning up system packages..."

if command -v apt-get >/dev/null 2>&1; then
    print_info "Cleaning up APT packages..."
    sudo apt-get autoremove -y 2>/dev/null || true
    sudo apt-get autoclean 2>/dev/null || true
    print_status "APT cleanup completed"
elif command -v yum >/dev/null 2>&1; then
    print_info "Cleaning up YUM packages..."
    sudo yum autoremove -y 2>/dev/null || true
    sudo yum clean all 2>/dev/null || true
    print_status "YUM cleanup completed"
elif command -v dnf >/dev/null 2>&1; then
    print_info "Cleaning up DNF packages..."
    sudo dnf autoremove -y 2>/dev/null || true
    sudo dnf clean all 2>/dev/null || true
    print_status "DNF cleanup completed"
fi

# ============================================================================
# PHASE 8: FINAL VERIFICATION
# ============================================================================

print_section "PHASE 8: Final Verification"

# Check what's left
print_info "Verifying cleanup..."

# Check Kubernetes
if command -v kubectl >/dev/null 2>&1; then
    print_warning "kubectl still available (may be installed via package manager)"
else
    print_status "kubectl removed"
fi

# Check Docker
if command -v docker >/dev/null 2>&1; then
    print_warning "Docker still available (may be installed via package manager)"
    docker ps -a 2>/dev/null | grep -q . && print_warning "Docker containers still exist" || print_status "All Docker containers removed"
    docker images 2>/dev/null | grep -q . && print_warning "Docker images still exist" || print_status "All Docker images removed"
else
    print_status "Docker removed"
fi

# Check Kind
if command -v kind >/dev/null 2>&1; then
    print_warning "Kind still available"
else
    print_status "Kind removed"
fi

# Check Helm
if command -v helm >/dev/null 2>&1; then
    print_warning "Helm still available"
else
    print_status "Helm removed"
fi

# Check application files
if [ -d "venv" ]; then
    print_warning "Virtual environment still exists"
else
    print_status "Virtual environment removed"
fi

if [ -d "deployment/production" ]; then
    print_warning "Deployment files still exist"
else
    print_status "Deployment files removed"
fi

# ============================================================================
# PHASE 9: COMPLETION
# ============================================================================

print_section "PHASE 9: Direct Cleanup Complete"

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 CLEANUP COMPLETE! 🎉                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${WHITE}✅ Direct system cleanup completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 What was cleaned:${NC}"
echo -e "${WHITE}   • All Kubernetes clusters and resources${NC}"
echo -e "${WHITE}   • All Docker containers, images, and volumes${NC}"
echo -e "${WHITE}   • All installed tools (kubectl, helm, kind)${NC}"
echo -e "${WHITE}   • All application data and configurations${NC}"
echo -e "${WHITE}   • All network configurations${NC}"
echo -e "${WHITE}   • All temporary files${NC}"
echo -e "${WHITE}   • All Python cache files${NC}"
echo ""
echo -e "${RED}⚠️  NO BACKUP WAS CREATED - ALL DATA IS PERMANENTLY DELETED! ⚠️${NC}"
echo ""
echo -e "${GREEN}🔄 System is now in a clean state!${NC}"
echo ""

print_status "Direct system cleanup finished!"
print_warning "No backup was created - all data has been permanently deleted!"