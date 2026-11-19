variable "project_name" {
  description = "Project identifier used in resource names and tags."
  type        = string
}

variable "environment" {
  description = "Environment name used in resource names and tags."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the Jenkins security group is created."
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID for the Jenkins host."
  type        = string
}

variable "key_name" {
  description = "Existing EC2 key pair name in the selected AWS Region."
  type        = string
}

variable "admin_cidrs" {
  description = "Trusted IPv4 CIDRs allowed to SSH to the host and access Jenkins on port 8080."
  type        = set(string)

  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for cidr in var.admin_cidrs : can(cidrhost(cidr, 0))])
    error_message = "Provide at least one valid trusted IPv4 CIDR, such as your public IP with /32."
  }
}

variable "instance_type" {
  description = "EC2 instance type for the Jenkins controller host."
  type        = string
  default     = "t3.small"
}

variable "ecr_repository_arns" {
  description = "ECR repository ARNs Jenkins may publish images to."
  type        = list(string)

  validation {
    condition     = length(var.ecr_repository_arns) > 0
    error_message = "Provide the ECR repository ARNs that Jenkins is allowed to publish to."
  }
}
