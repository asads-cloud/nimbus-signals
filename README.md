# 📡 Nimbus Signals

**Nimbus Signals** is a cloud-native, production-aligned **real-time
price intelligence platform** engineered using modern **DevOps, GitOps,
platform engineering, and Kubernetes** practices.

It continuously ingests BTC/ETH price data, exposes operational and
business metrics, and runs end-to-end on a fully automated **Terraform →
EKS → Argo CD → GitHub Actions** delivery pipeline.

This project demonstrates how to design, deploy, and operate a
**resilient microservice platform** using 2025-grade cloud engineering
standards, including:

-   Immutable infrastructure
-   GitOps-driven deployments
-   Observability-first design
-   Secure AWS-native CI/CD
-   Modular, scalable infrastructure as code

------------------------------------------------------------------------

## ⚙️ Core Capabilities

| Category                   | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| **Real-Time Data Service** | FastAPI microservice scraping live BTC/ETH prices with probe endpoints + structured logs |
| **Metrics & Telemetry**    | Prometheus metrics for application, business KPIs, and scrape health        |
| **GitOps Delivery**        | Fully declarative deployments managed by Argo CD                             |
| **Infrastructure as Code** | Terraform modules for VPC, EKS, node groups, IAM, ECR, networking            |
| **Automated CI/CD**        | GitHub Actions pipelines for build, test, image publishing, and chart updates |
| **Observability Stack**    | kube-prometheus-stack with Grafana dashboards                                |
| **Scalable Kubernetes Runtime** | Namespaced EKS architecture for application, monitoring, and platform components |

> 💡 **Nimbus Signals is engineered as a compact yet realistic
> representation of a production microservice platform, suitable for
> real-world extension, team handoffs, and platform-engineering
> conversations.**

------------------------------------------------------------------------

## 🏗️ Architecture Overview

                 ┌──────────────────────────┐
                 │ GitHub Actions (CI/CD)   │
                 └────────────┬─────────────┘
                              │  Build/Test
                              ▼
                      Amazon ECR (Images)
                              │
                              ▼
                    Argo CD (GitOps Control)
                              │ Sync
                              ▼
                    AWS EKS (Workload Runtime)
            ┌──────────────┬───────────────┬─────────────┐
            │ price-service │  Monitoring   │   Argo CD    │
            │ (FastAPI)     │ (Prom+Grafana)│   Control    │
            └──────────────┴───────────────┴─────────────┘

### **Key Components**

-   **Auth:** IAM Roles for Service Accounts (IRSA)
-   **Runtime:** Kubernetes + Horizontal scalability
-   **State:** Fully stateless, infra recreated via Terraform
-   **Delivery model:** Git-driven environment promotion
-   **Observability:** End-to-end metrics and dashboards

------------------------------------------------------------------------

## 🧬 Tech Stack

| Area           | Technologies                               |
|----------------|---------------------------------------------|
| Application    | Python 3.12, FastAPI                        |
| Containers     | Docker, Amazon ECR                          |
| Orchestration  | Kubernetes (AWS EKS)                        |
| IaC            | Terraform (VPC, EKS, ECR, IAM)              |
| GitOps         | Argo CD                                     |
| Monitoring     | Prometheus Operator, Grafana                |
| CI/CD          | GitHub Actions                              |
| Tooling        | awscli, kubectl, helm, terraform, docker    |

------------------------------------------------------------------------

## 📁 Repository Structure

    nimbus-signals/
      apps/
        price-service/       # FastAPI service, Dockerfile, metrics
      terraform/
        envs/                # Per-environment entrypoints (dev, prod)
        modules/
          eks/               # EKS cluster, node groups, IAM, ECR, VPC
      platform/
        argocd/              # GitOps applications
        monitoring/          # kube-prometheus-stack config
      .github/
        workflows/           # CI/CD automation
      README.md

------------------------------------------------------------------------

## 🚀 Getting Started

### 🧩 1. Clone the repository

``` bash
git clone https://github.com/<your-username>/nimbus-signals.git
cd nimbus-signals
```

### 🧩 2. Verify your toolchain

``` bash
aws --version
terraform -version
kubectl version --client
helm version
docker --version
python --version
```

### 🧩 3. Authenticate to AWS

``` bash
aws configure
aws sts get-caller-identity
```

### 🧩 4. Deploy Infrastructure

    cd terraform/envs/dev
    terraform init
    terraform apply

### 🧩 5. Deploy Platform Components (GitOps)

Argo CD automatically syncs:

-   price-service
-   kube-prometheus-stack
-   Argo CD itself

Cluster state is always driven from Git.

------------------------------------------------------------------------

## 📊 Observability

Nimbus Signals ships with:

-   Application-level metrics
-   Latency, errors, scrape freshness
-   Resource usage (CPU/memory)
-   Cluster-level Prometheus metrics
-   Pre-built Grafana dashboards

All metrics are automatically scraped through ServiceMonitors.

------------------------------------------------------------------------

## 🧠 Design Principles

-   **Git as the source of truth**: Argo CD enforces declarative
    infra\
-   **Security-aligned**: IRSA, least-privilege IAM, no long-lived
    secrets\
-   **Modular IaC**: Terraform split into composable modules\
-   **Operational visibility**: metrics at every layer\
-   **Production-centred structure**: mirrors real platform
    engineering workflows

------------------------------------------------------------------------

## 🧩 Future Expansion

Nimbus Signals can be extended into a broader market-data and analytics
platform:

-   🧮 Additional asset classes & exchanges
-   📈 Historical time-series storage (Timestream / Mimir /
    VictoriaMetrics)
-   🛂 API gateway integration for rate limiting & auth
-   ☸️ Autoscaling via HPA/KEDA
-   📦 Additional microservices (alerts, aggregators, enrichers)
-   🔐 Multi-region deployments (Terraform + Argo CD app-of-apps)

------------------------------------------------------------------------


## Cleanup & Cost Management

Nimbus Signals runs on AWS EKS, which can accumulate cost if left running.  
This project uses **Terraform as the single source of truth** for provisioning and destroying infrastructure.

###  Core Principles

- **Terraform is authoritative**  
  All resources should be created and destroyed through Terraform, avoid using the AWS console for modification.

- **Avoid orphaned resources**  
  Double-check no leftover cloud components remain after teardown:
  - EKS clusters / node groups  
  - Load balancers (ELB/NLB/ALB)  
  - ECR images  
  - Auto Scaling Groups  
  - CloudWatch log groups  

- **Short-lived environments**  
  Spin up the cluster only when needed; destroy after testing or demo work.

---

###  Standard Teardown Flow

When you're finished with a dev or demo environment:

1. **Navigate to the Terraform environment directory:**

    ```bash
    cd terraform/envs/dev
    ```

2. **Review what Terraform will destroy:**

    ```bash
    terraform plan -destroy
    ```

3. **Tear down the stack:**

    ```bash
    terraform destroy
    ```

This removes:
- EKS cluster + node groups  
- Node IAM roles / instance profiles (if managed here)  
- ECR repositories (optional based on module settings)  
- Networking components (VPC, subnets, gateways) if provisioned by the module  

---

###  Manual Checks (Post-Destroy)

After `terraform destroy` completes, verify the following in AWS:

- **EKS:** No clusters or node groups named `nimbus-*`  
- **EC2 → Load Balancers:** No leftover NLB/ALB/ELB resources  
- **EC2 → Auto Scaling:** No lingering ASGs  
- **ECR:** Expected repositories removed  
- **CloudWatch Logs:** Clean up unused log groups

If anything remains, update the Terraform modules so it is managed and destroyed automatically next time.

---

###  Cost-Saving Defaults

Terraform modules and Kubernetes configuration follow:

- **Small instance types** for non-production workloads (e.g. `t3.small`, `t3.medium`)  
- **Low node counts** for dev (typically 2–3 nodes)  
- **Minimal addons** to reduce spend (only the essentials)  
- **On-demand nodes** for simplicity (spot integration optional later)  

---

As Nimbus Signals grows, this section can be expanded or moved into a dedicated cleanup guide under:


    
>terraform/modules/eks/docs/cleanup.md
    
---


## 🧾 License

MIT: see [LICENSE](./LICENSE).

---

> **Maintained by:** Asad Rana: Cloud Engineer w/ AWS & Terraform | Specialising in Statistics, Data & Security
