# AWS Infrastructure (Terraform)

This section provisions the cloud platform that will host the project. The planned infrastructure includes a VPC and subnets, EKS, ECR repositories, a Jenkins host, and remote Terraform state in S3.

## Current status

The development VPC, public and private subnets across two Availability Zones, internet routing, and a shared NAT Gateway have been created. The EKS cluster and managed worker nodes are deployed. The ECR module is implemented in Terraform configuration and is ready to plan; it has not been applied yet.

## Planned structure

- `environments/dev/` — development stack composition, variables, and outputs; calls the network, EKS, and ECR modules.
- `modules/network/` — implemented VPC, subnet, internet routing, and NAT resources.
- `modules/eks/` — EKS control plane, managed nodes, and access configuration.
- `modules/ecr/` — private container image repositories with scan-on-push and image-retention settings.
- `modules/jenkins/` — Jenkins EC2 resources and supporting IAM/security configuration.

The development stack currently uses Terraform's local state because the S3 backend bootstrap is not implemented yet. Keep local state, credentials, private keys, and real `.tfvars` out of Git. Review `terraform plan` before any apply. EKS incurs cluster and worker-node charges, while the existing NAT Gateway also has hourly and data-processing charges.
