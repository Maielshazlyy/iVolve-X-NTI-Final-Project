variable "project_name" {
  description = "Project identifier used in repository names and tags."
  type        = string
}

variable "environment" {
  description = "Environment name used in repository names and tags."
  type        = string
}

variable "repository_names" {
  description = "Names of application services that need private ECR repositories."
  type        = set(string)

  validation {
    condition     = length(var.repository_names) > 0
    error_message = "Provide at least one service repository name."
  }
}
