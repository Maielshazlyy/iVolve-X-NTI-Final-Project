output "repository_urls" {
  description = "Map of service names to private ECR repository URLs."
  value       = { for name, repository in aws_ecr_repository.services : name => repository.repository_url }
}

output "registry_id" {
  description = "AWS account ID that owns these ECR repositories."
  value       = values(aws_ecr_repository.services)[0].registry_id
}

output "repository_arns" {
  description = "Map of service names to private ECR repository ARNs."
  value       = { for name, repository in aws_ecr_repository.services : name => repository.arn }
}
