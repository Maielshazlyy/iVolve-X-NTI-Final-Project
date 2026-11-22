variable "project_name" {
  description = "Project identifier used in AWS resource names and tags."
  type        = string
}

variable "environment" {
  description = "Environment name used in AWS resource names and tags."
  type        = string
}

variable "ci_user_name" {
  description = "Existing IAM user whose access keys GitHub Actions uses to publish images."
  type        = string
}

variable "ecr_repository_arns" {
  description = "ECR repository ARNs where the GitHub Actions CI workflow may publish images."
  type        = list(string)
}
