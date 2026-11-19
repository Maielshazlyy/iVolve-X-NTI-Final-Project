output "state_bucket_name" {
  description = "Account- and region-specific S3 bucket used by the dev Terraform backend."
  value       = aws_s3_bucket.state.id
}

output "state_key" {
  description = "Object key for the dev Terraform state."
  value       = "ivolve-x/dev/terraform.tfstate"
}
