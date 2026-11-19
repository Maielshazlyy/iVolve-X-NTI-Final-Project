variable "project_name" {
  description = "Project identifier used in AWS resource names and tags."
  type        = string
}

variable "environment" {
  description = "Environment name used in AWS resource names and tags."
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster that GitHub Actions will deploy to."
  type        = string
}

variable "cluster_arn" {
  description = "EKS cluster ARN for least-privilege DescribeCluster access."
  type        = string
}

variable "deploy_user_name" {
  description = "Name of the existing IAM user used by GitHub Actions."
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace that the deployment role can manage."
  type        = string
}
