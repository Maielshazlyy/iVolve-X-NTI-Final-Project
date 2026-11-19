output "vpc_id" {
  description = "ID of the development VPC."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs intended for internet-facing load balancers."
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs intended for EKS nodes and internal services."
  value       = module.network.private_subnet_ids
}

output "availability_zones" {
  description = "Availability Zones used by the development network."
  value       = module.network.availability_zones
}

output "network_acl_ids" {
  description = "Network ACL IDs assigned to the public and private subnets."
  value = {
    public  = module.network.public_network_acl_id
    private = module.network.private_network_acl_id
  }
}

output "eks_cluster_name" {
  description = "Name of the development EKS cluster."
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Kubernetes API endpoint for the development EKS cluster."
  value       = module.eks.cluster_endpoint
}

output "eks_node_group_name" {
  description = "Name of the EKS managed worker node group."
  value       = module.eks.node_group_name
}

output "ecr_repository_urls" {
  description = "Private ECR image repositories for the application services."
  value       = module.ecr.repository_urls
}

output "jenkins_instance_id" {
  description = "EC2 instance ID of the Jenkins controller host."
  value       = module.jenkins.instance_id
}

output "jenkins_public_ip" {
  description = "Public address for Jenkins UI and SSH from approved CIDRs."
  value       = module.jenkins.public_ip
}

output "jenkins_public_dns" {
  description = "Public DNS name of the Jenkins host."
  value       = module.jenkins.public_dns
}

output "github_actions_deploy_user_arn" {
  description = "IAM user ARN used by GitHub Actions for EKS deployments."
  value       = module.github_actions.user_arn
}
