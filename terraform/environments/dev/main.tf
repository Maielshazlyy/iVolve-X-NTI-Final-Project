module "network" {
  source = "../../modules/network"

  project_name         = var.project_name
  environment          = var.environment
  cluster_name         = var.cluster_name
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  single_nat_gateway   = var.single_nat_gateway
}

module "eks" {
  source = "../../modules/eks"

  project_name                         = var.project_name
  environment                          = var.environment
  cluster_name                         = var.cluster_name
  private_subnet_ids                   = module.network.private_subnet_ids
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
  node_instance_types                  = var.node_instance_types
  node_desired_size                    = var.node_desired_size
  node_min_size                        = var.node_min_size
  node_max_size                        = var.node_max_size
}

module "ecr" {
  source = "../../modules/ecr"

  project_name     = var.project_name
  environment      = var.environment
  repository_names = ["auth-service", "roadmap-service", "frontend"]
}

module "github_actions" {
  source = "../../modules/github-actions"

  project_name       = var.project_name
  environment        = var.environment
  ci_user_name       = var.github_ci_user_name
  ecr_repository_arns = values(module.ecr.repository_arns)
}
