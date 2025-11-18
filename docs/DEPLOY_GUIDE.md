
# Kubernetes Deployment (Helm) Guide

**Environment:** `dev`  
**Region:** `eu-west-1`  
**Project:** **nimbus-signals**

---

## 📦 1. Helm Chart Overview

**Chart name:** `price-service`  
**Chart path:**  
`apps/price-service/helm/price-service`  
**Target namespace:** `platform`  
**Helm release name:** `price-service`

### 📁 Chart Structure

```
price-service/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── servicemonitor.yaml
    └── hpa.yaml
```

---

## 🖼 2. Image Configuration

**ECR Repository:**
```
<AWS_ACCOUNT_ID>.dkr.ecr.eu-west-1.amazonaws.com/nimbus-signals/price-service
```

Default tag: `latest`

### `values.yaml` Image Block
```yaml
image:
  repository: <AWS_ACCOUNT_ID>.dkr.ecr.eu-west-1.amazonaws.com/nimbus-signals/price-service
  tag: "latest"
  pullPolicy: IfNotPresent
```

---

## ⚙️ 3. Application Configuration (values.yaml)

### 🔢 Replicas
```yaml
replicaCount: 1
```

### 🌍 Environment Variables
```yaml
env:
  symbols: "BTC,ETH"
  fetchIntervalSeconds: "15"
  windowSize: "120"
```

Mapped to container env vars:

- `SYMBOLS`
- `FETCH_INTERVAL_SECONDS`
- `WINDOW_SIZE`

### 🧵 Resources
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 250m
    memory: 256Mi
```

---

## 🏗 4. Kubernetes Objects

### 🟦 Deployment
- **Kind:** Deployment  
- **API Version:** `apps/v1`
- **Port:** `8080` (named `http`)
- **Probes:**
  - `/healthz` (liveness)
  - `/readyz` (readiness)

### 🟩 Service
- **Kind:** Service  
- **Type:** ClusterIP  
- **Port:** `8080` → `http`

Selector labels:
```
app.kubernetes.io/name: price-service
app.kubernetes.io/instance: price-service
```

### 📡 ServiceMonitor
- **Kind:** ServiceMonitor  
- **API Version:** `monitoring.coreos.com/v1`
- **Endpoint:**
  - `port: http`
  - `path: /metrics`
  - `interval: 15s`

`values.yaml`:
```yaml
serviceMonitor:
  enabled: true
  interval: 15s
```

> Note: ServiceMonitor works once Prometheus Operator CRDs are installed..

---

## 🚀 5. Helm Deployment Commands

From **repo root**:

### 👉 Set kubeconfig
```powershell
aws eks update-kubeconfig `
  --region eu-west-1 `
  --name nimbus-signals-eks-dev
```

### 👉 Deploy/upgrade the release
```powershell
cd apps/price-service/helm/price-service

helm upgrade --install price-service . `
  --namespace platform `
  --create-namespace
```

### Verify the release:
```powershell
helm list -n platform
```

---

## 🔍 6. Runtime Verification

### 📌 Pods
```powershell
kubectl get pods -n platform
```

Expected:
- Pod name `price-service-xxxxx`
- `STATUS: Running`
- `READY: 1/1`

### 📡 Service
```powershell
kubectl get svc -n platform
```

Expected:
- `price-service` ClusterIP on port **8080**

### 🔄 Port Forward
Terminal 1:
```powershell
kubectl port-forward svc/price-service -n platform 8080:8080
```

Terminal 2:
```powershell
curl http://localhost:8080/metrics
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz
curl http://localhost:8080/prices
```

Expected:
- `/metrics` → Prometheus metrics  
- `/healthz` → OK  
- `/readyz` → OK  
- `/prices` → BTC/ETH latest price JSON  

---

## 📌 7. Notes for later (Argo CD / GitOps)

You will use:

- **Chart path:** `apps/price-service/helm/price-service`
- **Namespace:** `platform`
- **Release name:** `price-service`
- **Image:**  
  ```
  <AWS_ACCOUNT_ID>.dkr.ecr.eu-west-1.amazonaws.com/nimbus-signals/price-service:latest
  ```
- **Health checks:** `/healthz`, `/readyz`
- **Metrics:** `/metrics` on port `http`
- **ServiceMonitor:** enabled (can toggle via GitOps repo)



