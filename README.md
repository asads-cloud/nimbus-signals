# 📡 Nimbus Signals

**Nimbus Signals** is a production-aligned, cloud-native **real-time price intelligence platform** built with Terraform → EKS → Argo CD → GitHub Actions.

It demonstrates practical **platform engineering**, **GitOps**, **Kubernetes operations**, and **cloud automation** using modern 2025 standards.  
The platform continuously ingests BTC/ETH prices, exposes operational + business metrics, and runs end‑to‑end through an automated and declarative delivery pipeline.

---

## 🎯 Why This Project Matters

Nimbus Signals shows that I can:

- Design and operate a **real Kubernetes platform** on AWS  
- Build modular **Terraform IaC** (VPC, EKS, IAM, ECR, networking)  
- Implement **GitOps with Argo CD** to drive cluster state from Git  
- Build secure **AWS-native CI/CD pipelines** with GitHub Actions + OIDC  
- Deploy a real microservice with **metrics, probes, dashboards, and alerts**  
- Run production-style infrastructure with observability baked in  

This project reflects the day-to-day work of **Cloud, DevOps, and Platform Engineers**.

---

## ⚙️ Core Capabilities

| Category | Description |
|---------|-------------|
| **Real-Time Data Service** | FastAPI microservice scraping live BTC/ETH prices with structured logs + probe endpoints |
| **Metrics & Telemetry** | Prometheus metrics for app health, scrape freshness, and business KPIs |
| **GitOps Delivery** | Declarative deployments via Argo CD; Git = source of truth |
| **Infrastructure as Code** | Terraform modules for VPC, EKS, node groups, IAM, ECR, networking |
| **Automated CI/CD** | GitHub Actions: build → test → image publish → Helm/Chart updates |
| **Observability Stack** | kube-prometheus-stack + Grafana dashboards |
| **Scalable Kubernetes Runtime** | Namespaced EKS layout for app, monitoring, and platform components |

> 💡 Nimbus Signals is intentionally engineered as a **compact yet realistic production microservice platform** that mirrors how real teams deliver and operate cloud workloads.

---

## 🏗️ Architecture Overview

```
┌──────────────────────────┐
│ GitHub Actions (CI/CD)   │
└────────────┬─────────────┘
             │ Build/Test
             ▼
      Amazon ECR (Images)
             │
             ▼
     Argo CD (GitOps Control)
             │ Sync
             ▼
     AWS EKS (Workload Runtime)
 ┌──────────────┬───────────────┬─────────────┐
 │ price-service│  Monitoring   │   Argo CD    │
 │ (FastAPI)    │ (Prom+Grafana)│   Control    │
 └──────────────┴───────────────┴─────────────┘
```

### Key Components

- **Auth:** IRSA (IAM Roles for Service Accounts)  
- **Runtime:** Kubernetes with horizontal scalability  
- **State:** Fully stateless; infra recreated via Terraform  
- **Delivery:** GitOps-driven environment promotion  
- **Observability:** End‑to‑end metrics and dashboards  

---

## 🧬 Tech Stack

| Area | Technologies |
|------|--------------|
| Application | Python 3.12, FastAPI |
| Containers | Docker, Amazon ECR |
| Orchestration | Kubernetes (AWS EKS) |
| IaC | Terraform (VPC, EKS, ECR, IAM) |
| GitOps | Argo CD |
| Monitoring | Prometheus Operator, Grafana |
| CI/CD | GitHub Actions |
| Tooling | awscli, kubectl, helm, terraform, docker |

---

## 📁 Repository Structure

```
nimbus-signals/
  apps/
    price-service/       # FastAPI service + Dockerfile + metrics
  terraform/
    envs/                # Environment entrypoints (dev, prod)
    modules/
      eks/               # EKS cluster, node groups, IAM, ECR, VPC
  platform/
    argocd/              # GitOps applications
    monitoring/          # Prometheus + Grafana config
  .github/
    workflows/           # CI/CD automation
  README.md
```

---

## 🚀 Getting Started

### 1. Clone

```bash
git clone https://github.com/asads-cloud/nimbus-signals.git
cd nimbus-signals
```

### 2. Verify Toolchain

```bash
aws --version
terraform -version
kubectl version --client
helm version
docker --version
python --version
```

### 3. Authenticate to AWS

```bash
aws configure
aws sts get-caller-identity
```

### 4. Deploy Infrastructure

```bash
cd terraform/envs/dev
terraform init
terraform apply
```

### 5. Deploy Platform Components (GitOps)

Argo CD auto-syncs:

- price-service  
- kube-prometheus-stack  
- Argo CD itself  

All Kubernetes state is **driven from Git**.

---

## 📊 Observability

Nimbus Signals exposes:

- Application latency, errors, throughput  
- Scrape freshness + scheduler delays  
- Business metrics (price spread, movement, frequency)  
- Cluster metrics: CPU, memory, node status  
- Pre-built Grafana dashboards  

All scraped via ServiceMonitors.

---

## 🧠 Design Principles

- **Git as the single source of truth**  
- **Security-first:** IRSA, least privilege IAM, no static secrets  
- **Modular IaC:** Terraform modules with clean separation  
- **Observability everywhere**  
- **Production-minded architecture**  

---

## 🧩 Future Expansion

- Additional assets/exchanges  
- Historical time-series DB (Timestream, VictoriaMetrics)  
- HPA/KEDA autoscaling  
- Gateway/API-level auth + rate limiting  
- Multi-service architecture (alerts, enrichers, aggregators)  
- Multi-region deployments  

---

## 🧽 Cleanup & Cost Management

EKS clusters incur cost, use Terraform to create/destroy everything.

### Teardown

```bash
cd terraform/envs/dev
terraform plan -destroy
terraform destroy
```

Verify no leftover:

- EKS clusters / node groups  
- Load balancers  
- ASGs  
- ECR images  
- CloudWatch log groups  

Terraform is authoritative, update modules if anything is left unmanaged.

---

## 🧾 License

MIT — see [LICENSE](./LICENSE).

---

## 👤 Author

Designed and built by **Asad Rana**\
Cloud & Platform Engineer | AWS, Terraform, GitOps, CI/CD
