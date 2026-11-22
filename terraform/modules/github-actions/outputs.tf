output "ci_user_arn" {
  description = "IAM user ARN used by GitHub Actions to publish container images to ECR."
  value       = data.aws_iam_user.ci.arn
}
