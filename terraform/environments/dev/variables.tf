variable "project_name" {
  description = "Project identifier used in AWS resource names and tags."
  type        = string
  default     = "ivolve-x"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region where the development network will be created."
  type        = string
  default     = "eu-north-1"
}

variable "cluster_name" {
  description = "Name reserved for the EKS cluster that will use these subnets."
  type        = string
  default     = "ivolve-x-dev"
}

variable "vpc_cidr" {
  description = "IPv4 range for the development VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR ranges for public subnets, one per Availability Zone."
  type        = list(string)
  default     = ["10.40.0.0/24", "10.40.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR ranges for private subnets, one per Availability Zone."
  type        = list(string)
  default     = ["10.40.16.0/20", "10.40.32.0/20"]

  validation {
    condition     = length(var.private_subnet_cidrs) == length(var.public_subnet_cidrs) && length(var.private_subnet_cidrs) >= 2
    error_message = "Provide matching public and private subnet CIDR lists for at least two Availability Zones."
  }
}

variable "single_nat_gateway" {
  description = "Use one NAT Gateway to reduce development cost; set false for one per Availability Zone."
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "Public IPv4 CIDRs allowed to reach the EKS Kubernetes API. Set this to your current public IP with /32."
  type        = list(string)

  validation {
    condition     = length(var.cluster_endpoint_public_access_cidrs) > 0
    error_message = "Set a trusted public CIDR, such as your current public IP with /32."
  }
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS managed workers."
  type        = list(string)
  default     = ["t3.small"]
}

variable "node_desired_size" {
  description = "Desired count of EKS worker nodes."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum count of EKS worker nodes."
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum count of EKS worker nodes."
  type        = number
  default     = 2
}

variable "github_ci_user_name" {
  description = "Existing IAM user whose access keys GitHub Actions will use to publish images to ECR."
  type        = string
  default     = "ivolve-x-dev-github-deployer"
}
