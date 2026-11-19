output "user_arn" {
  description = "IAM user ARN used by GitHub Actions for EKS deployments."
  value       = data.aws_iam_user.deploy.arn
}
