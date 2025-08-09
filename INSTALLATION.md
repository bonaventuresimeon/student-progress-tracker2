# NativeSeries Installation Guide

## 📋 Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation Options](#installation-options)
- [Automated Installation](#automated-installation)
- [Manual Installation](#manual-installation)
- [Environment Setup](#environment-setup)
- [Docker Setup](#docker-setup)
- [Kubernetes Setup](#kubernetes-setup)
- [Netlify Setup](#netlify-setup)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This guide provides comprehensive installation instructions for NativeSeries, covering all deployment options including local development, Docker containers, Kubernetes orchestration, and serverless deployment.

## 💻 System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, Amazon Linux 2)
- **CPU**: 2 vCPUs
- **Memory**: 8GB RAM (16GB recommended for monitoring stack)
- **Storage**: 50GB free space (for monitoring data)
- **Network**: Internet connection for downloading dependencies

### Recommended Requirements
- **CPU**: 4+ vCPUs
- **Memory**: 16GB RAM
- **Storage**: 100GB SSD
- **Network**: Stable internet connection

### Required Tools
- **Python**: 3.11 or higher
- **Docker**: 20.10 or higher
- **kubectl**: 1.28 or higher
- **Helm**: 3.13 or higher
- **Kind**: 0.20.0 or higher (for local Kubernetes)
- **ArgoCD CLI**: 2.9.3 or higher

## 🚀 Installation Options

### 1. Automated Installation (Recommended)
Complete setup with one command using the installation script.

### 2. Manual Installation
Step-by-step installation for custom configurations.

### 3. Development Setup
Local development environment for coding and testing.

### 4. Docker Setup
Containerized deployment using Docker.

### 5. Kubernetes Setup
Production-grade deployment using Kubernetes.

### 6. Netlify Setup
Serverless deployment using Netlify Functions.

## 🤖 Automated Installation

### Quick Start (Recommended)

```bash
# Clone the repository
git clone https://github.com/bonaventuresimeon/nativeseries.git
cd nativeseries

# Run the automated installation script
chmod +x scripts/install-all.sh
./scripts/install-all.sh
```

### What the Script Installs

1. **System Dependencies**
   - curl, wget, git, unzip, jq
   - Python 3.11 and pip
   - Build tools and development libraries

2. **Container Tools**
   - Docker 24.0.7
   - Docker Compose

3. **Kubernetes Tools**
   - kubectl 1.33.3
   - Helm 3.18.4
   - Kind 0.20.0
   - ArgoCD CLI

4. **Application Setup**
   - Python virtual environment
   - Application dependencies
   - Docker image building

5. **Infrastructure**
   - Kind Kubernetes cluster
   - ArgoCD installation
   - Monitoring stack (Prometheus, Grafana, Loki)
   - Application deployment

6. **Verification**
   - Health checks
   - Service verification
   - Monitoring validation

## 🛠️ Manual Installation

### Step 1: System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install basic tools
sudo apt install -y curl wget git unzip jq gcc g++ make \
    python3 python3-pip python3-venv python3-dev \
    build-essential libssl-dev libffi-dev \
    ca-certificates gnupg lsb-release \
    software-properties-common apt-transport-https
```

### Step 2: Install Docker

```bash
# Remove old Docker installations
sudo apt remove -y docker docker-engine docker.io containerd runc

# Install Docker using official script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh --version 24.0.7

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

**⚠️ Important**: Log out and back in for Docker group permissions to take effect.

### Step 3: Install kubectl

```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/v1.33.3/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client --short
```

### Step 4: Install Kind

```bash
# Download Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Verify installation
kind version
```

### Step 5: Install Helm

```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

### Step 6: Install ArgoCD CLI

```bash
# Download ArgoCD CLI
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

# Verify installation
argocd version --client
```

### Step 7: Application Setup

```bash
# Clone repository
git clone https://github.com/bonaventuresimeon/nativeseries.git
cd nativeseries

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Build Docker image
docker build -t ghcr.io/bonaventuresimeon/nativeseries:latest .
```

### Step 8: Kubernetes Cluster Setup

```bash
# Create Kind cluster configuration
mkdir -p infra/kind
cat > infra/kind/cluster-config.yaml << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: gitops-cluster
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 30011
    hostPort: 30011
    protocol: TCP
    listenAddress: "0.0.0.0"
  - containerPort: 30080
    hostPort: 30080
    protocol: TCP
    listenAddress: "0.0.0.0"
  - containerPort: 30081
    hostPort: 30081
    protocol: TCP
    listenAddress: "0.0.0.0"
  - containerPort: 30082
    hostPort: 30082
    protocol: TCP
    listenAddress: "0.0.0.0"
  - containerPort: 30083
    hostPort: 30083
    protocol: TCP
    listenAddress: "0.0.0.0"
- role: worker
- role: worker
EOF

# Create cluster
kind create cluster --config infra/kind/cluster-config.yaml

# Load Docker image into cluster
kind load docker-image ghcr.io/bonaventuresimeon/nativeseries:latest --name gitops-cluster
```

### Step 9: Deploy Application

```bash
# Create namespaces
kubectl create namespace nativeseries
kubectl create namespace argocd
kubectl create namespace monitoring
kubectl create namespace logging

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.9.3/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=Available deployment/argocd-server -n argocd --timeout=300s

# Deploy application
kubectl apply -f deployment/production/01-namespace.yaml
kubectl apply -f deployment/production/02-application.yaml
kubectl apply -f deployment/production/04-argocd-service.yaml
kubectl apply -f deployment/production/05-argocd-application.yaml
```

## 🌍 Environment Setup

### Environment Variables

Create a `.env` file in the project root:

```bash
# Application Configuration
APP_ENV=production
APP_NAME=NativeSeries
APP_VERSION=1.0.0
SECRET_KEY=your-secret-key-here
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=nativeseries
COLLECTION_NAME=students
MONGO_URI=mongodb://localhost:27017

# Security and CORS
CORS_ORIGINS=*
ALLOWED_HOSTS=*

# Vault Configuration (if using HashiCorp Vault)
VAULT_ADDR=http://your-vault-server:8200
VAULT_ROLE_ID=your-role-id
VAULT_SECRET_ID=your-secret-id
```

### Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## 🐳 Docker Setup

### Build Docker Image

```bash
# Build image
docker build -t nativeseries:latest .

# Build with specific tag
docker build -t ghcr.io/bonaventuresimeon/nativeseries:v1.0.0 .

# Build for different architectures
docker buildx build --platform linux/amd64,linux/arm64 -t nativeseries:latest .
```

### Run Docker Container

```bash
# Run with environment variables
docker run -d \
  --name nativeseries \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e SECRET_KEY=your-secret-key \
  nativeseries:latest

# Run with volume mounting
docker run -d \
  --name nativeseries \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  nativeseries:latest

# Run with custom configuration
docker run -d \
  --name nativeseries \
  -p 8000:8000 \
  --env-file .env \
  nativeseries:latest
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - SECRET_KEY=your-secret-key
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mongodb_data:
  redis_data:
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## ☸️ Kubernetes Setup

### Create Kubernetes Cluster

```bash
# Create Kind cluster
kind create cluster --name nativeseries --config infra/kind/cluster-config.yaml

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### Deploy with Helm

```bash
# Add Helm repository (if needed)
helm repo add nativeseries https://charts.example.com
helm repo update

# Install application
helm install nativeseries ./helm-chart \
  --namespace nativeseries \
  --create-namespace \
  --set image.repository=ghcr.io/bonaventuresimeon/nativeseries \
  --set image.tag=latest

# Upgrade application
helm upgrade nativeseries ./helm-chart \
  --namespace nativeseries \
  --set image.tag=v1.0.1
```

### Deploy with kubectl

```bash
# Apply all manifests
kubectl apply -f deployment/production/

# Apply specific components
kubectl apply -f deployment/production/01-namespace.yaml
kubectl apply -f deployment/production/02-application.yaml
kubectl apply -f deployment/production/06-monitoring-stack.yaml
```

### Verify Deployment

```bash
# Check all resources
kubectl get all --all-namespaces

# Check application status
kubectl get pods -n nativeseries
kubectl get services -n nativeseries

# Check logs
kubectl logs -f deployment/nativeseries -n nativeseries

# Port forward for local access
kubectl port-forward svc/nativeseries-service 8000:80 -n nativeseries
```

## 🌐 Netlify Setup

### Prerequisites

- Netlify account
- GitHub repository connected to Netlify
- Netlify CLI installed

### Install Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Verify installation
netlify --version
```

### Deploy to Netlify

```bash
# Login to Netlify
netlify login

# Initialize Netlify project
netlify init

# Build and deploy
./build.sh
netlify deploy --prod --dir=public --functions=netlify/functions
```

### Configure Netlify

The `netlify.toml` file is already configured with:

- Build command: `./build.sh`
- Publish directory: `public`
- Functions directory: `netlify/functions`
- Redirects for API endpoints
- Security headers
- Environment variables

### Environment Variables in Netlify

Set these in your Netlify dashboard:

```bash
APP_ENV=production
APP_NAME=NativeSeries
SECRET_KEY=your-secret-key
DATABASE_URL=memory://
DATABASE_NAME=nativeseries
COLLECTION_NAME=students
CORS_ORIGINS=*
ALLOWED_HOSTS=*
```

## 🛠️ Development Setup

### Local Development

```bash
# Clone repository
git clone https://github.com/bonaventuresimeon/nativeseries.git
cd nativeseries

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Development with Docker

```bash
# Build development image
docker build -t nativeseries:dev .

# Run with volume mounting
docker run -p 8000:8000 \
  -v $(pwd):/app \
  -v $(pwd)/logs:/app/logs \
  nativeseries:dev
```

### Development with Kubernetes

```bash
# Create development cluster
kind create cluster --name nativeseries-dev

# Deploy to development cluster
kubectl apply -f deployment/development/

# Port forward for local access
kubectl port-forward svc/nativeseries-service 8000:80 -n nativeseries
```

### Testing

```bash
# Run unit tests
python -m pytest

# Run integration tests
python -m pytest tests/integration/

# Run with coverage
python -m pytest --cov=app tests/

# Run specific test file
python -m pytest tests/test_main.py -v
```

## 🔧 Troubleshooting

### Common Issues

#### Docker Issues

**Docker not starting:**
```bash
# Check Docker service
sudo systemctl status docker

# Start Docker service
sudo systemctl start docker

# Check Docker daemon
sudo docker info
```

**Permission denied:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

#### Kubernetes Issues

**kubectl not found:**
```bash
# Check PATH
echo $PATH

# Reinstall kubectl
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

**Cluster not accessible:**
```bash
# Check cluster status
kubectl cluster-info

# Check kubeconfig
kubectl config view

# Reset kubeconfig
kind export kubeconfig --name gitops-cluster
```

#### Application Issues

**Application not starting:**
```bash
# Check logs
kubectl logs -f deployment/nativeseries -n nativeseries

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'

# Check pod status
kubectl describe pod -l app=nativeseries -n nativeseries
```

**Database connection failed:**
```bash
# Check database service
kubectl get svc -n nativeseries

# Check database logs
kubectl logs -f deployment/mongodb -n nativeseries

# Test database connectivity
kubectl exec -it deployment/nativeseries -n nativeseries -- curl localhost:27017
```

### Debug Commands

```bash
# Check all resources
kubectl get all --all-namespaces

# Check specific namespace
kubectl get all -n nativeseries

# Check pod logs
kubectl logs -f <pod-name> -n <namespace>

# Check service endpoints
kubectl get endpoints --all-namespaces

# Check persistent volumes
kubectl get pv,pvc --all-namespaces

# Check configmaps and secrets
kubectl get configmaps,secrets --all-namespaces
```

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Kubernetes health
kubectl get componentstatuses

# Node health
kubectl get nodes -o wide

# Pod health
kubectl get pods --all-namespaces -o wide
```

### Performance Monitoring

```bash
# Check resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Check metrics
kubectl get --raw /metrics

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Helm Documentation](https://helm.sh/docs/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)

### Community Support
- [GitHub Issues](https://github.com/bonaventuresimeon/nativeseries/issues)
- [Discussions](https://github.com/bonaventuresimeon/nativeseries/discussions)
- [Wiki](https://github.com/bonaventuresimeon/nativeseries/wiki)

---

**🎉 Installation Complete!**

Your NativeSeries application should now be running. Check the [README.md](README.md) for access URLs and next steps.