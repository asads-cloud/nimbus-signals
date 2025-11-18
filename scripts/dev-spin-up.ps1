<#
  Dev spin-up script for Nimbus Signals

  What this does:
    1. Runs Terraform for the dev env
    2. Updates kubeconfig for the dev EKS cluster
    3. Logs in to ECR
    4. Builds and pushes the price-service Docker image
    5. Deploys price-service via Helm into the "platform" namespace

  Usage (from repo root):
    .\scripts\dev-spin-up.ps1 -AwsAccountId 123456789012

  Optional configs:
    -Region       (defaults to eu-west-1)
    -ClusterName  (defaults to nimbus-signals-eks-dev)
#>

param(
  [string]$Region       = "eu-west-1",
  [string]$ClusterName  = "nimbus-signals-eks-dev",
  [string]$AwsAccountId = "<AWS_ACCOUNT_ID>"
)

# Fail fast if anything goes wrong
$ErrorActionPreference = "Stop"

# Basic sanity check so we don't accidentally push to a fake account
if ($AwsAccountId -eq "<AWS_ACCOUNT_ID>") {
    Write-Error "Please pass a real -AwsAccountId (not the placeholder)."
    exit 1
}

# ----- Paths and derived values ---------------- -----

$TerraformEnvDir = "terraform/envs/dev"
$HelmChartDir    = "apps/price-service/helm/price-service"
$EcrRepo         = "$AwsAccountId.dkr.ecr.$Region.amazonaws.com/nimbus-signals/price-service"

Write-Host "=== Nimbus Signals - Dev spin-up ===" -ForegroundColor Cyan
Write-Host "Region:       $Region"
Write-Host "Cluster:      $ClusterName"
Write-Host "AWS Account:  $AwsAccountId"
Write-Host ""

# Helper to make step output consistent
function Invoke-Step {
    param(
        [int]   $Number,
        [int]   $Total,
        [string]$Message,
        [scriptblock]$Action
    )

    Write-Host "`n[$Number/$Total] $Message..." -ForegroundColor Yellow
    & $Action
}

# 1) Terraform init + apply (dev env)
Invoke-Step -Number 1 -Total 5 -Message "Terraform apply for dev environment" -Action {
    Push-Location $TerraformEnvDir
    try {
        terraform init
        terraform apply -auto-approve
    }
    finally {
        Pop-Location
    }
}

# 2) Update kubeconfig so kubectl/helm talk to the right EKS cluster
Invoke-Step -Number 2 -Total 5 -Message "Updating kubeconfig for EKS cluster '$ClusterName'" -Action {
    aws eks update-kubeconfig `
        --region $Region `
        --name $ClusterName
}

# 3) ECR login (docker -> AWS ECR)
Invoke-Step -Number 3 -Total 5 -Message "Logging in to ECR" -Action {
    aws ecr get-login-password --region $Region `
        | docker login `
            --username AWS `
            --password-stdin "$AwsAccountId.dkr.ecr.$Region.amazonaws.com"
}

# 4) Build, tag, and push the Docker image for price-service
Invoke-Step -Number 4 -Total 5 -Message "Building and pushing Docker image for price-service" -Action {
    # Build image from apps/price-service/Dockerfile
    docker build `
        -t price-service:latest `
        -f .\apps\price-service\Dockerfile `
        .\apps\price-service

    Write-Host "Tagging image for ECR repo '$EcrRepo'..."
    docker tag price-service:latest "$EcrRepo:latest"

    Write-Host "Pushing image to ECR..."
    docker push "$EcrRepo:latest"
}

# 5) Helm deploy into the 'platform' namespace
Invoke-Step -Number 5 -Total 5 -Message "Deploying price-service Helm release" -Action {
    Push-Location $HelmChartDir
    try {
        # Base Helm args
        $helmArgs = @(
            "upgrade", "--install", "price-service", ".",
            "--namespace", "platform",
            "--create-namespace",
            "-f", "values.yaml"
        )

        # local override file if you have per-dev values!!!!!!!!!!!!!!!!!
        if (Test-Path "values.dev.local.yaml") {
            Write-Host "Using values.dev.local.yaml override file."
            $helmArgs += @("-f", "values.dev.local.yaml")
        }
        else {
            Write-Host "values.dev.local.yaml not found – using only values.yaml."
        }

        helm @helmArgs
    }
    finally {
        Pop-Location
    }
}

Write-Host "`nDone. price-service should now be running in the 'platform' namespace on the dev cluster." -ForegroundColor Green
