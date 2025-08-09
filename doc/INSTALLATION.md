# NativeSeries - Complete Installation Guide

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
- [Detailed Installation](#detailed-installation)
- [Production Deployment](#production-deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Testing & Verification](#testing--verification)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This guide provides comprehensive instructions for installing and deploying the NativeSeries application with full monitoring, logging, security, and auto-scaling capabilities. The application is designed to be deployed using modern cloud-native practices with Docker, Kubernetes, and GitOps.

### What You'll Get

- ✅ **FastAPI Application**: Modern Python web framework
- ✅ **Docker Containerization**: Portable and scalable deployment
- ✅ **Kubernetes Orchestration**: Production-ready container orchestration
- ✅ **ArgoCD GitOps**: Automated deployment and management
- ✅ **Prometheus & Grafana**: Complete monitoring stack
- ✅ **Loki Logging**: Centralized log aggregation
- ✅ **Secrets & ConfigMaps**: Secure configuration management
- ✅ **Horizontal Pod Autoscaler**: Automatic scaling based on CPU/memory
- ✅ **Pod Disruption Budget**: High availability during updates
- ✅ **Network Policies**: Security and traffic control

## 🔧 Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, Amazon Linux 2)
- **Memory**: Minimum 8GB RAM (16GB recommended for monitoring stack)
- **Storage**: Minimum 50GB free space (for monitoring data)
- **Network**: Internet connection for downloading dependencies

### Required Tools

- **Python**: 3.11 or higher
- **Docker**: 20.10 or higher
- **kubectl**: 1.28 or higher
- **Helm**: 3.13 or higher
- **Kind**: 0.20.0 or higher (for local Kubernetes)
- **ArgoCD CLI**: 2.9.3 or higher

## 🚀 Quick Installation

### Automated Installation Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/bonaventuresimeon/nativeseries.git
cd nativeseries

# Run the automated installation script
chmod +x scripts/install-all.sh
./scripts/install-all.sh
```

This script will install:
1. All required tools (Docker, kubectl, Helm, Kind, ArgoCD)
2. Kubernetes cluster with Kind
3. Application deployment
4. **Monitoring stack (Prometheus + Grafana)**
5. **Logging stack (Loki)**
6. **Secrets and ConfigMaps**
7. **Auto-scaling configuration (HPA)**
8. **Network policies and security**

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/bonaventuresimeon/nativeseries.git
cd nativeseries

# Install Python dependencies
pip install -r requirements.txt

# Build Docker image
docker build -t ghcr.io/bonaventuresimeon/nativeseries:latest .

# Run locally
docker run -p 8000:8000 ghcr.io/bonaventuresimeon/nativeseries:latest
```

## 📖 Detailed Installation

### Step 1: Environment Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git unzip jq build-essential software-properties-common

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Docker

```bash
# Install Docker
sudo apt install -y docker.io docker-compose

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
```

### Step 3: Install kubectl

```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make executable and move to PATH
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

### Step 4: Install Kind

```bash
# Download Kind
curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64"

# Make executable and move to PATH
chmod +x ./kind
sudo mv ./kind /usr/local/bin/

# Verify installation
kind version
```

### Step 5: Install Helm

```bash
# Download Helm
curl https://get.helm.sh/helm-v3.13.0-linux-amd64.tar.gz | tar xz

# Move to PATH
sudo mv linux-amd64/helm /usr/local/bin/
rm -rf linux-amd64

# Verify installation
helm version
```

### Step 6: Install ArgoCD CLI

```bash
# Download ArgoCD CLI
curl -sSL -o argocd-linux-amd64 "https://github.com/argoproj/argo-cd/releases/download/v2.9.3/argocd-linux-amd64"

# Install to PATH
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

# Verify installation
argocd version --client
```

### Step 7: Create Kubernetes Cluster

```bash
# Create Kind cluster
kind create cluster --name nativeseries --config infra/kind/cluster-config.yaml

# Verify cluster
kubectl get nodes
kubectl cluster-info
```

### Step 8: Install ArgoCD

```bash
# Create ArgoCD namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.9.3/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# Configure ArgoCD for insecure access
kubectl patch deployment argocd-server -n argocd -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--insecure"}]' --type=json

# Create NodePort service
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: argocd-server-nodeport
  namespace: argocd
spec:
  type: NodePort
  ports:
  - name: server
    port: 80
    protocol: TCP
    targetPort: 8080
    nodePort: 30080
  selector:
    app.kubernetes.io/name: argocd-server
EOF

# Get admin password
ARGOCD_PASSWORD=$(kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d)
echo "$ARGOCD_PASSWORD" > .argocd-password
```

### Step 9: Deploy Application

```bash
# Create application namespace
kubectl create namespace nativeseries

# Deploy with Helm
helm install nativeseries ./helm-chart \
  --namespace nativeseries \
  --set monitoring.enabled=true \
  --set logging.enabled=true \
  --set hpa.enabled=true \
  --set networkPolicy.enabled=true

# Verify deployment
kubectl get pods -n nativeseries
kubectl get services -n nativeseries
```

### Step 10: Install Monitoring Stack

```bash
# Create monitoring namespace
kubectl create namespace monitoring

# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.enabled=true \
  --set grafana.service.type=NodePort \
  --set grafana.service.nodePort=30081 \
  --set prometheus.service.type=NodePort \
  --set prometheus.service.nodePort=30082

# Wait for monitoring stack to be ready
kubectl wait --for=condition=available --timeout=300s deployment/prometheus-operator -n monitoring
```

### Step 11: Install Loki Logging

```bash
# Create logging namespace
kubectl create namespace logging

# Add Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Loki Stack
helm upgrade --install loki grafana/loki-stack \
  --namespace logging \
  --set loki.enabled=true \
  --set promtail.enabled=false \
  --set grafana.enabled=false \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi \
  --set loki.service.type=NodePort \
  --set loki.service.nodePort=30083

# Wait for Loki to be ready
kubectl wait --for=condition=available --timeout=300s deployment/loki -n logging
```

### Step 12: Configure Monitoring

```bash
# Create ServiceMonitor for application
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nativeseries-monitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: nativeseries
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
EOF

# Create PodMonitor for pod-level metrics
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: nativeseries-pod-monitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: nativeseries
  podMetricsEndpoints:
  - port: http
    path: /metrics
    interval: 30s
EOF
```

### Step 13: Configure Security

```bash
# Create secrets
kubectl create secret generic nativeseries-db-secret \
  --from-literal=username=admin \
  --from-literal=password=password123 \
  -n nativeseries

kubectl create secret generic nativeseries-api-secret \
  --from-literal=jwt-secret=your-jwt-secret-key \
  --from-literal=api-key=your-api-key \
  -n nativeseries

# Create ConfigMaps
kubectl create configmap nativeseries-config \
  --from-literal=log-level=INFO \
  --from-literal=environment=production \
  -n nativeseries

# Create Network Policy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nativeseries-network-policy
  namespace: nativeseries
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: nativeseries
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
EOF
```

### Step 14: Configure Auto-scaling

```bash
# Create Horizontal Pod Autoscaler
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nativeseries-hpa
  namespace: nativeseries
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nativeseries
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF

# Create Pod Disruption Budget
cat <<EOF | kubectl apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nativeseries-pdb
  namespace: nativeseries
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: nativeseries
EOF
```

## 🌐 Production Deployment

### Production Environment

The application is deployed to production at:
- **Application**: http://54.166.101.159:30011
- **ArgoCD UI**: http://54.166.101.159:30080
- **Grafana**: http://54.166.101.159:30081
- **Prometheus**: http://54.166.101.159:30082
- **Loki**: http://54.166.101.159:30083

### Deployment Components

#### Application Deployment
- **Namespace**: `nativeseries`
- **Service**: NodePort on port 30011
- **Replicas**: 2-10 (auto-scaled)
- **Health Checks**: Liveness and readiness probes
- **Resource Limits**: CPU and memory constraints

#### Monitoring Stack
- **Namespace**: `monitoring`
- **Prometheus**: Metrics collection and storage
- **Grafana**: Dashboards and visualization
- **ServiceMonitor**: Application metrics monitoring
- **PodMonitor**: Pod-level metrics collection

#### Logging Stack
- **Namespace**: `logging`
- **Loki**: Log aggregation and querying
- **Log Forwarding**: Application logs to Loki
- **Grafana Integration**: Log visualization in Grafana

#### Security Configuration
- **Secrets**: Database and API credentials
- **ConfigMaps**: Application configuration
- **Network Policies**: Traffic control and security
- **RBAC**: Role-based access control

#### Auto-scaling
- **HPA**: Horizontal Pod Autoscaler
- **Min Replicas**: 2
- **Max Replicas**: 10
- **CPU Threshold**: 70%
- **Memory Threshold**: 80%

## 🔍 Monitoring & Observability

### Prometheus & Grafana

**Access URLs:**
- Grafana: `http://54.166.101.159:30081` (admin/admin123)
- Prometheus: `http://54.166.101.159:30082`

**Components:**
- Prometheus Operator for metrics collection
- Grafana dashboards for visualization
- ServiceMonitor for application metrics
- PodMonitor for pod-level metrics
- PrometheusRule for alerting

### Loki Logging

**Access URL:**
- Loki: `http://54.166.101.159:30083`

**Components:**
- Loki server for log aggregation
- Log forwarding from application pods
- Log querying and visualization in Grafana

### Application Metrics

The application exposes the following metrics:
- **Health Status**: Application health and readiness
- **Request Metrics**: HTTP request counts and latencies
- **Resource Usage**: CPU and memory consumption
- **Custom Metrics**: Application-specific metrics

### Alerting Rules

Configured alerts for:
- **High CPU Usage**: CPU > 80% for 5 minutes
- **High Memory Usage**: Memory > 85% for 5 minutes
- **Pod Restarts**: Pod restart count > 3 in 10 minutes
- **Service Availability**: Service down for > 2 minutes

## 🧪 Testing & Verification

### Health Checks

```bash
# Application health
curl http://54.166.101.159:30011/health

# Metrics endpoint
curl http://54.166.101.159:30011/metrics

# API documentation
curl http://54.166.101.159:30011/docs
```

### Monitoring Tests

```bash
# Run monitoring tests
./scripts/test-monitoring.sh

# Check application status
kubectl get pods -n nativeseries

# Check monitoring stack
kubectl get pods -n monitoring

# Check logging stack
kubectl get pods -n logging
```

### Smoke Tests

```bash
# Run smoke tests
./scripts/smoke-tests.sh

# Validate deployment
./scripts/validate-deployment.sh
```

### Verification Commands

```bash
# Check all namespaces
kubectl get namespaces

# Check application deployment
kubectl get pods -n nativeseries
kubectl get services -n nativeseries
kubectl get hpa -n nativeseries

# Check monitoring stack
kubectl get pods -n monitoring
kubectl get servicemonitors -n monitoring

# Check logging stack
kubectl get pods -n logging

# Check secrets and configmaps
kubectl get secrets -n nativeseries
kubectl get configmaps -n nativeseries

# Check network policies
kubectl get networkpolicies -n nativeseries
```

## 🐛 Troubleshooting

### Common Issues

#### Installation Issues
1. **Docker not starting**: Check Docker daemon and permissions
2. **kubectl not found**: Ensure kubectl is in PATH
3. **Helm installation failed**: Check network connectivity
4. **Kind cluster creation failed**: Ensure Docker is running

#### Application Issues
1. **Application not starting**: Check logs with `kubectl logs`
2. **Database connection failed**: Verify MongoDB configuration
3. **Health checks failing**: Check application configuration
4. **Metrics not appearing**: Verify ServiceMonitor configuration

#### Monitoring Issues
1. **Grafana not accessible**: Check NodePort service
2. **Prometheus not collecting metrics**: Verify ServiceMonitor
3. **Loki logs not appearing**: Check log forwarding configuration
4. **Alerts not firing**: Verify PrometheusRule configuration

### Debug Commands

```bash
# Check application logs
kubectl logs -f deployment/nativeseries -n nativeseries

# Check monitoring logs
kubectl logs -f deployment/prometheus -n monitoring
kubectl logs -f deployment/grafana -n monitoring

# Check Loki logs
kubectl logs -f deployment/loki -n logging

# Check cluster status
kubectl get nodes
kubectl get pods --all-namespaces

# Check services
kubectl get svc --all-namespaces

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

### Log Locations

- **Application Logs**: `/app/logs/app.log`
- **Container Logs**: `kubectl logs <pod-name>`
- **System Logs**: `/var/log/`
- **Docker Logs**: `docker logs <container-id>`

---

**🎉 Installation Complete! Your NativeSeries application is now running with full monitoring, logging, and auto-scaling capabilities. 🚀**