variable "project_name" {
  description = "Project identifier used in the backend bucket name and tags."
  type        = string
  default     = "ivolve-x"
}

variable "aws_region" {
  description = "AWS Region where the Terraform state bucket is created."
  type        = string
  default     = "eu-north-1"
}
