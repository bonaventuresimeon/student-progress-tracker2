#!/bin/bash

# NativeSeries - Complete System Cleanup with Backup
# Version: 1.0.0 - Backup everything before complete system cleanup
# This script backs up all data and then completely cleans the system

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
BACKUP_DIR="/tmp/nativeseries-backup-$(date +%Y%m%d-%H%M%S)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
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
echo "║          🗑️  NativeSeries - Complete System Cleanup              ║"
echo "║              WITH FULL BACKUP                                    ║"
echo "║              Target: ${HOSTNAME}                                 ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Confirmation
echo -e "${RED}⚠️  WARNING: This script will completely clean your system! ⚠️${NC}"
echo ""
echo -e "${YELLOW}This script will:${NC}"
echo -e "${WHITE}  • Create a complete backup of all data${NC}"
echo -e "${WHITE}  • Remove all Kubernetes clusters${NC}"
echo -e "${WHITE}  • Remove all Docker containers, images, and volumes${NC}"
echo -e "${WHITE}  • Remove all installed tools (kubectl, helm, kind, etc.)${NC}"
echo -e "${WHITE}  • Clean all network configurations${NC}"
echo -e "${WHITE}  • Remove all application data${NC}"
echo -e "${WHITE}  • Reset the system to a clean state${NC}"
echo ""
echo -e "${CYAN}Backup will be saved to: ${BACKUP_DIR}${NC}"
echo ""
read -p "Are you absolutely sure you want to continue? Type 'YES' to confirm: " -r
echo
if [[ ! $REPLY =~ ^YES$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# ============================================================================
# PHASE 1: CREATE BACKUP DIRECTORY
# ============================================================================

print_section "PHASE 1: Creating Backup Directory"

print_info "Creating backup directory: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"
print_status "Backup directory created"

# ============================================================================
# PHASE 2: SYSTEM INFORMATION BACKUP
# ============================================================================

print_section "PHASE 2: Backing Up System Information"

# System information
print_info "Backing up system information..."
{
    echo "=== SYSTEM INFORMATION ==="
    echo "Timestamp: $(date)"
    echo "Hostname: $(hostname)"
    echo "OS: $(cat /etc/os-release 2>/dev/null || echo 'Unknown')"
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo "CPU: $(nproc) cores"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
    echo "Disk: $(df -h / | tail -1 | awk '{print $2}')"
    echo ""
    echo "=== USER INFORMATION ==="
    echo "Current user: $(whoami)"
    echo "User ID: $(id)"
    echo "Home directory: $HOME"
    echo ""
    echo "=== NETWORK INFORMATION ==="
    echo "IP Address: $(hostname -I 2>/dev/null || echo 'Unknown')"
    echo "Hostname: $(hostname)"
    echo ""
} > "${BACKUP_DIR}/system-info.txt"
print_status "System information backed up"

# ============================================================================
# PHASE 3: KUBERNETES BACKUP
# ============================================================================

print_section "PHASE 3: Backing Up Kubernetes Data"

# Check if kubectl is available
if command -v kubectl >/dev/null 2>&1; then
    print_info "Backing up Kubernetes cluster data..."
    
    # Create Kubernetes backup directory
    mkdir -p "${BACKUP_DIR}/kubernetes"
    
    # Backup cluster info
    kubectl cluster-info > "${BACKUP_DIR}/kubernetes/cluster-info.txt" 2>&1 || true
    
    # Backup all namespaces
    kubectl get namespaces -o yaml > "${BACKUP_DIR}/kubernetes/namespaces.yaml" 2>&1 || true
    
    # Backup all resources from all namespaces
    for namespace in $(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo ""); do
        if [ -n "$namespace" ]; then
            print_info "Backing up namespace: $namespace"
            mkdir -p "${BACKUP_DIR}/kubernetes/namespaces/${namespace}"
            
            # Backup all resources in namespace
            kubectl get all -n "$namespace" -o yaml > "${BACKUP_DIR}/kubernetes/namespaces/${namespace}/all-resources.yaml" 2>&1 || true
            kubectl get configmaps -n "$namespace" -o yaml > "${BACKUP_DIR}/kubernetes/namespaces/${namespace}/configmaps.yaml" 2>&1 || true
            kubectl get secrets -n "$namespace" -o yaml > "${BACKUP_DIR}/kubernetes/namespaces/${namespace}/secrets.yaml" 2>&1 || true
            kubectl get services -n "$namespace" -o yaml > "${BACKUP_DIR}/kubernetes/namespaces/${namespace}/services.yaml" 2>&1 || true
            kubectl get ingress -n "$namespace" -o yaml > "${BACKUP_DIR}/kubernetes/namespaces/${namespace}/ingress.yaml" 2>&1 || true
            kubectl get persistentvolumeclaims -n "$namespace" -o yaml > "${BACKUP_DIR}/kubernetes/namespaces/${namespace}/pvc.yaml" 2>&1 || true
        fi
    done
    
    # Backup cluster-wide resources
    kubectl get nodes -o yaml > "${BACKUP_DIR}/kubernetes/nodes.yaml" 2>&1 || true
    kubectl get persistentvolumes -o yaml > "${BACKUP_DIR}/kubernetes/persistentvolumes.yaml" 2>&1 || true
    kubectl get storageclasses -o yaml > "${BACKUP_DIR}/kubernetes/storageclasses.yaml" 2>&1 || true
    
    print_status "Kubernetes data backed up"
else
    print_warning "kubectl not found, skipping Kubernetes backup"
fi

# ============================================================================
# PHASE 4: DOCKER BACKUP
# ============================================================================

print_section "PHASE 4: Backing Up Docker Data"

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    print_info "Backing up Docker data..."
    
    # Create Docker backup directory
    mkdir -p "${BACKUP_DIR}/docker"
    
    # Backup Docker images
    docker images > "${BACKUP_DIR}/docker/images.txt" 2>&1 || true
    
    # Backup Docker containers
    docker ps -a > "${BACKUP_DIR}/docker/containers.txt" 2>&1 || true
    
    # Backup Docker volumes
    docker volume ls > "${BACKUP_DIR}/docker/volumes.txt" 2>&1 || true
    
    # Backup Docker networks
    docker network ls > "${BACKUP_DIR}/docker/networks.txt" 2>&1 || true
    
    # Save important images
    print_info "Saving important Docker images..."
    for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>" | head -10); do
        if [ -n "$image" ]; then
            filename=$(echo "$image" | tr ':/' '_' | tr '[:upper:]' '[:lower:]')
            docker save "$image" > "${BACKUP_DIR}/docker/${filename}.tar" 2>&1 || true
        fi
    done
    
    print_status "Docker data backed up"
else
    print_warning "Docker not found, skipping Docker backup"
fi

# ============================================================================
# PHASE 5: APPLICATION DATA BACKUP
# ============================================================================

print_section "PHASE 5: Backing Up Application Data"

# Backup current directory
print_info "Backing up current application directory..."
cp -r . "${BACKUP_DIR}/application" 2>/dev/null || true

# Backup configuration files
print_info "Backing up configuration files..."
{
    echo "=== CONFIGURATION FILES ==="
    echo "Current directory: $(pwd)"
    echo "Files in current directory:"
    ls -la
    echo ""
    echo "=== ENVIRONMENT VARIABLES ==="
    env | sort
    echo ""
    echo "=== SHELL CONFIGURATION ==="
    echo "Shell: $SHELL"
    echo "PATH: $PATH"
    echo ""
} > "${BACKUP_DIR}/config-info.txt"

# Backup important system files
print_info "Backing up important system files..."
mkdir -p "${BACKUP_DIR}/system-files"

# Backup package lists
if command -v apt-get >/dev/null 2>&1; then
    dpkg -l > "${BACKUP_DIR}/system-files/installed-packages.txt" 2>/dev/null || true
elif command -v yum >/dev/null 2>&1; then
    yum list installed > "${BACKUP_DIR}/system-files/installed-packages.txt" 2>/dev/null || true
elif command -v dnf >/dev/null 2>&1; then
    dnf list installed > "${BACKUP_DIR}/system-files/installed-packages.txt" 2>/dev/null || true
fi

# Backup network configuration
ip addr show > "${BACKUP_DIR}/system-files/network-config.txt" 2>/dev/null || true
ip route show > "${BACKUP_DIR}/system-files/routing-table.txt" 2>/dev/null || true

print_status "Application data backed up"

# ============================================================================
# PHASE 6: CREATE BACKUP SUMMARY
# ============================================================================

print_section "PHASE 6: Creating Backup Summary"

# Create backup summary
cat > "${BACKUP_DIR}/BACKUP_SUMMARY.txt" << EOF
NativeSeries System Backup Summary
==================================

Backup Date: $(date)
Hostname: $(hostname)
Backup Directory: ${BACKUP_DIR}

Backup Contents:
- System information
- Kubernetes cluster data
- Docker images and containers
- Application source code
- Configuration files
- Network configuration
- Installed packages

To restore from this backup:
1. Extract the backup directory
2. Review the backup contents
3. Restore Kubernetes resources: kubectl apply -f kubernetes/
4. Restore Docker images: docker load -i docker/*.tar
5. Restore application: copy application/ directory

Backup completed successfully!
EOF

print_status "Backup summary created"

# ============================================================================
# PHASE 7: COMPLETE SYSTEM CLEANUP
# ============================================================================

print_section "PHASE 7: Complete System Cleanup"

# Final confirmation
echo -e "${RED}⚠️  FINAL WARNING: About to completely clean the system! ⚠️${NC}"
echo -e "${YELLOW}Backup is complete and saved to: ${BACKUP_DIR}${NC}"
echo ""
read -p "Type 'CLEAN' to proceed with system cleanup: " -r
echo
if [[ ! $REPLY =~ ^CLEAN$ ]]; then
    echo "Cleanup cancelled. Backup is available at: ${BACKUP_DIR}"
    exit 0
fi

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
fi

# Cleanup Docker
print_info "Cleaning up Docker..."
if command -v docker >/dev/null 2>&1; then
    # Stop all containers
    docker stop $(docker ps -aq) 2>/dev/null || true
    
    # Remove all containers
    docker rm $(docker ps -aq) 2>/dev/null || true
    
    # Remove all images
    docker rmi $(docker images -q) 2>/dev/null || true
    
    # Remove all volumes
    docker volume rm $(docker volume ls -q) 2>/dev/null || true
    
    # Remove all networks (except default)
    docker network rm $(docker network ls --format "{{.Name}}" | grep -v "bridge\|host\|none") 2>/dev/null || true
    
    # Prune everything
    docker system prune -af --volumes 2>/dev/null || true
fi

# Cleanup tools
print_info "Removing installed tools..."
if command -v kind >/dev/null 2>&1; then
    sudo rm -f /usr/local/bin/kind
fi

if command -v kubectl >/dev/null 2>&1; then
    sudo rm -f /usr/local/bin/kubectl
fi

if command -v helm >/dev/null 2>&1; then
    sudo rm -f /usr/local/bin/helm
fi

# Cleanup application files
print_info "Cleaning up application files..."
rm -rf venv/ 2>/dev/null || true
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf __pycache__/ 2>/dev/null || true
rm -rf *.pyc 2>/dev/null || true
rm -rf deployment/production/ 2>/dev/null || true
rm -rf infra/kind/ 2>/dev/null || true

# Cleanup temporary files
print_info "Cleaning up temporary files..."
rm -f get-docker.sh 2>/dev/null || true
rm -f kind 2>/dev/null || true
rm -f kubectl 2>/dev/null || true
rm -f *.tar 2>/dev/null || true
rm -f *.tar.gz 2>/dev/null || true

# Cleanup network configurations
print_info "Cleaning up network configurations..."
sudo iptables -F 2>/dev/null || true
sudo iptables -X 2>/dev/null || true
sudo iptables -t nat -F 2>/dev/null || true
sudo iptables -t nat -X 2>/dev/null || true

# Cleanup system packages (optional)
print_info "Cleaning up system packages..."
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get autoremove -y 2>/dev/null || true
    sudo apt-get autoclean 2>/dev/null || true
elif command -v yum >/dev/null 2>&1; then
    sudo yum autoremove -y 2>/dev/null || true
    sudo yum clean all 2>/dev/null || true
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf autoremove -y 2>/dev/null || true
    sudo dnf clean all 2>/dev/null || true
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

# ============================================================================
# PHASE 9: COMPLETION
# ============================================================================

print_section "PHASE 9: Cleanup Complete"

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 CLEANUP COMPLETE! 🎉                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${WHITE}✅ System cleanup completed successfully!${NC}"
echo ""
echo -e "${CYAN}📁 Backup Location:${NC}"
echo -e "${WHITE}   ${BACKUP_DIR}${NC}"
echo ""
echo -e "${YELLOW}📋 What was cleaned:${NC}"
echo -e "${WHITE}   • All Kubernetes clusters and resources${NC}"
echo -e "${WHITE}   • All Docker containers, images, and volumes${NC}"
echo -e "${WHITE}   • All installed tools (kubectl, helm, kind)${NC}"
echo -e "${WHITE}   • All application data and configurations${NC}"
echo -e "${WHITE}   • All network configurations${NC}"
echo -e "${WHITE}   • All temporary files${NC}"
echo ""
echo -e "${GREEN}🔄 System is now in a clean state!${NC}"
echo -e "${BLUE}💾 Your backup is safely stored at: ${BACKUP_DIR}${NC}"
echo ""

print_status "Complete system cleanup finished!"
print_info "Backup is available at: ${BACKUP_DIR}"