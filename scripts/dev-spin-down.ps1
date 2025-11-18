<#
  Dev spin-down script for Nimbus Signals

  What this does:
    1. Uninstalls the price-service Helm release
    2. Runs `terraform destroy` against the dev environment

  Usage (from repo root):
    .\scripts\dev-spin-down.ps1

  configs:
    -TerraformEnvDir  (defaults to terraform/envs/dev)
#>

param(
  [string]$TerraformEnvDir = "terraform/envs/dev"
)

# Fail fast on errors
$ErrorActionPreference = "Stop"

Write-Host "=== Nimbus Signals - Dev spin-down ===" -ForegroundColor Cyan
Write-Host "Terraform env dir: $TerraformEnvDir"
Write-Host ""

# Helper so step output looks consistent
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

# 1) Helm uninstall (ignore if it doesn't exist)
Invoke-Step -Number 1 -Total 2 -Message "Uninstalling price-service Helm release (if present)" -Action {
    try {
        helm uninstall price-service -n platform
    }
    catch {
        Write-Host "Helm release 'price-service' not found or already removed. Continuing..." -ForegroundColor DarkYellow
    }
}

# 2) Terraform destroy (dev environment)
Invoke-Step -Number 2 -Total 2 -Message "Terraform destroy for dev environment" -Action {
    Push-Location $TerraformEnvDir
    try {
        terraform destroy -auto-approve
    }
    finally {
        Pop-Location
    }
}

Write-Host "`n✅ Dev spin-down complete. EKS + dev infra destroyed." -ForegroundColor Green
Write-Host "Note: any ECR repos/images or other resources managed by Terraform in this env will also be removed." -ForegroundColor DarkGray
