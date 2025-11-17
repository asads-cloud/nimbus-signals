terraform {
  backend "local" {
    path = "../../state/dev/terraform.tfstate"
  }
}

locals {
  project     = "nimbus-signals"
  environment = "dev"
  region      = "eu-west-1"

  common_tags = {
    project     = local.project
    environment = local.environment
  }
}

#------------ VPC Module ------------------------------------------------------------------

module "vpc" {
  source = "../../modules/vpc"

  vpc_name = "nimbus-signals-vpc"

  cidr_block = "10.0.0.0/16"

  azs = [
    "eu-west-1a",
    "eu-west-1b",
  ]

  public_subnet_cidrs = [
    "10.0.0.0/24",
    "10.0.1.0/24",
  ]

  private_subnet_cidrs = [
    "10.0.10.0/24",
    "10.0.11.0/24",
  ]

  tags = local.common_tags
}

#------------ KUBERNETES (EKS) Module ------------------------------------------------------------------

module "eks" {
  source = "../../modules/eks"

  cluster_name    = "nimbus-signals-eks-dev"
  cluster_version = "1.29"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  node_group_name    = "nimbus-signals-ng-dev"
  node_instance_type = "t3.small"

  node_desired_size = 1
  node_min_size     = 1
  node_max_size     = 2

  tags = local.common_tags
}

#------------ DOCKER ON THE CLOUD (ECR) Module ------------------------------------------------------------------

module "ecr_price_service" {
  source = "../../modules/ecr"

  repository_name = "nimbus-signals/price-service"

  tags = local.common_tags
}
