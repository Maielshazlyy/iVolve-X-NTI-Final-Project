# Terraform Modules

This directory holds reusable Terraform modules for the cloud platform. Each module defines its inputs, outputs, and resources so an environment can compose infrastructure without duplicating configuration.

`network/` provisions the VPC, public/private subnets, routes, and shared NAT Gateway. `eks/` provisions the EKS control plane and managed workers. `ecr/` provisions private repositories for the application images. `jenkins/` provisions the Jenkins host and ECR publishing role. `github-actions/` grants a dedicated IAM deploy user EKS access scoped to the application namespace. Terraform configuration does not create cloud resources until an apply is run.
