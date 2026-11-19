# AWS Infrastructure (Terraform)

This section provisions the cloud platform that will host the project. The planned infrastructure includes a VPC and subnets, EKS, ECR repositories, a Jenkins host, and remote Terraform state in S3.

## Current status

The development VPC, public and private subnets across two Availability Zones, internet routing, a shared NAT Gateway, EKS cluster, managed worker nodes, ECR repositories, and Jenkins EC2 controller are deployed. Ansible configures Jenkins. Network ACL configuration and an S3 backend bootstrap are now in code; review and apply the ACL plan, then run the backend bootstrap and migrate the current state.

## Planned structure

- `environments/dev/` — development stack composition, variables, and outputs; calls the network, EKS, and ECR modules.
- `modules/network/` — VPC, subnet, internet routing, NAT, and public/private Network ACLs.
- `modules/eks/` — EKS control plane, managed nodes, and access configuration.
- `modules/ecr/` — private container image repositories with scan-on-push and image-retention settings.
- `modules/jenkins/` — Jenkins EC2 resources and supporting IAM/security configuration.

`bootstrap/state-backend/` creates a versioned, encrypted, private S3 bucket for state. The dev environment uses S3 native lock files and requires Terraform 1.10 or newer. Bootstrap remains on local state. Apply it first, then run `terraform init -migrate-state` from `environments/dev` to move the current local state safely. Keep local state, backend config files, credentials, private keys, and real `.tfvars` out of Git. Review the full `terraform plan` before applying Network ACL changes. S3 storage and request costs are usage-based; Network ACLs have no additional charge. EKS workers and the NAT Gateway continue to incur charges while running.
