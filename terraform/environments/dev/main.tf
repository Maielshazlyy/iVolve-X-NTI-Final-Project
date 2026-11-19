module "network" {
  source = "../../modules/network"

  project_name         = var.project_name
  environment          = var.environment
  cluster_name         = var.cluster_name
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  single_nat_gateway   = var.single_nat_gateway
  trusted_admin_cidrs  = var.jenkins_admin_cidrs
}

module "eks" {
  source = "../../modules/eks"

  project_name                         = var.project_name
  environment                          = var.environment
  cluster_name                         = var.cluster_name
  private_subnet_ids                   = module.network.private_subnet_ids
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
  runner_security_group_id             = module.jenkins.security_group_id
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

module "jenkins" {
  source = "../../modules/jenkins"

  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.network.vpc_id
  public_subnet_id    = module.network.public_subnet_ids[0]
  key_name            = var.jenkins_key_name
  admin_cidrs         = var.jenkins_admin_cidrs
  instance_type       = var.jenkins_instance_type
  ecr_repository_arns = values(module.ecr.repository_arns)
}

module "github_actions" {
  source = "../../modules/github-actions"

  project_name     = var.project_name
  environment      = var.environment
  cluster_name     = module.eks.cluster_name
  cluster_arn      = module.eks.cluster_arn
  deploy_user_name = var.github_deploy_user_name
  namespace        = var.kubernetes_namespace
}
