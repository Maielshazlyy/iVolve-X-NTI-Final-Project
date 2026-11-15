# AWS Infrastructure (Terraform)

This section is reserved for provisioning the cloud platform that will host the project. The planned infrastructure includes a VPC and subnets, EKS, ECR repositories, a Jenkins host, and remote Terraform state in S3.

## Current status

The directory structure is prepared, but Terraform modules and environment configuration have not been implemented yet. No AWS infrastructure is created by the placeholder files in this directory.

## Planned structure

- `environments/dev/` — development stack composition, variables, and outputs.
- `modules/network/` — VPC, routing, and subnet resources.
- `modules/eks/` — EKS control plane, managed nodes, and access configuration.
- `modules/ecr/` — container image repositories.
- `modules/jenkins/` — Jenkins EC2 resources and supporting IAM/security configuration.

When implementation begins, configure remote state and review the plan before applying. Keep state files, credentials, private keys, and real `.tfvars` out of Git.
