output "instance_id" {
  description = "EC2 instance ID of the Jenkins host."
  value       = aws_instance.this.id
}

output "public_ip" {
  description = "Public IPv4 address for SSH and restricted Jenkins UI access."
  value       = aws_instance.this.public_ip
}

output "public_dns" {
  description = "Public DNS name of the Jenkins host."
  value       = aws_instance.this.public_dns
}

output "iam_role_arn" {
  description = "IAM role attached to the Jenkins EC2 instance profile."
  value       = aws_iam_role.this.arn
}

output "security_group_id" {
  description = "Security group attached to the Jenkins EC2 host and self-hosted GitHub Actions runner."
  value       = aws_security_group.this.id
}
