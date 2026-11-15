# Development Environment

This directory will compose the project's development AWS environment from the modules under `terraform/modules/`.

It currently contains only a placeholder. Planned resources include networking, EKS, ECR, and Jenkins infrastructure. Before applying a future configuration, initialize the configured remote backend, inspect `terraform plan`, and use explicit approval for billable AWS resources.
