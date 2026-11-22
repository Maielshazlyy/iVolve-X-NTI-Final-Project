variable "project_name" {
  description = "Project identifier used in resource names and tags."
  type        = string
}

variable "environment" {
  description = "Environment name used in resource names and tags."
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name used for subnet discovery tags."
  type        = string
}

variable "vpc_cidr" {
  description = "IPv4 CIDR range for the VPC."
  type        = string
}

variable "public_subnet_cidrs" {
  description = "One public subnet CIDR per Availability Zone."
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "One private subnet CIDR per Availability Zone."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_cidrs) == length(var.public_subnet_cidrs) && length(var.private_subnet_cidrs) >= 2
    error_message = "Provide matching public and private subnet CIDR lists for at least two Availability Zones."
  }
}

variable "single_nat_gateway" {
  description = "Create one shared NAT Gateway instead of one per Availability Zone."
  type        = bool
  default     = true
}
