# AWS Infrastructure with Terraform

Terraform provisions the AWS environment for IVOLVE in `eu-north-1`. The development stack includes a VPC across two Availability Zones, public/private subnets, Internet/NAT routing, stateless Network ACLs, the Jenkins EC2 host, EKS managed nodes, ECR repositories, IAM access, and a remote S3 state backend.

## Current deployment

- AWS VPC and EKS are deployed; EKS currently has two Ready `t3.small` worker nodes.
- Jenkins runs on the Terraform-managed EC2 host; Ansible configures the operating system and Jenkins service.
- ECR has the three service repositories.
- Public/private Network ACLs are applied and were followed by a healthy EKS node/pod/Ingress check.
- The development Terraform state was migrated to the encrypted/versioned S3 bucket `ivolve-x-tfstate-335452653010-eu-north-1` under `ivolve-x/dev/terraform.tfstate`.
- The last reported full `terraform plan` after applying changes returned `No changes`.

## Folder map

- `bootstrap/state-backend/` creates the S3 state bucket; bootstrap keeps its own local state.
- `environments/dev/` composes the deployed development environment and uses the S3 backend.
- `modules/network/` provides VPC, subnets, routing, NAT, and ACLs.
- `modules/jenkins/` provides the Jenkins controller EC2 and host IAM/security group resources.
- `modules/eks/` provides EKS, managed nodes, Pod Identity, EBS CSI, and controller access.
- `modules/ecr/` provides private repositories for the three services.
- `modules/github-actions/` provides namespace-scoped EKS deployment access for the GitHub Actions IAM identity.

Each folder has its own README with resource details and stage-specific commands. See [`environments/dev/README.md`](environments/dev/README.md) for operation commands and [`bootstrap/state-backend/README.md`](bootstrap/state-backend/README.md) for state migration.

## Verify the existing environment

From `terraform/environments/dev` in PowerShell, with valid AWS credentials:

```powershell
terraform init -backend-config=backend.hcl
terraform state list
terraform validate
terraform plan
terraform output
```

Expected outcome for the current deployed state: the state list contains the managed resources and the plan reports `No changes`. Do not commit the ignored `backend.hcl`, Terraform state, `.terraform/`, or credential files.

## Deploy a new or changed environment

1. Authenticate to AWS and confirm account/region.
2. Create required `TF_VAR_*` values for current trusted administrator CIDRs and the existing EC2 key pair.
3. Run `terraform init`, `terraform validate`, and inspect the entire `terraform plan`.
4. Apply only after verifying addresses, resource counts, EKS add-on versions, network rules, and costs.
5. Verify nodes, workload pods, ingress/ALB, Jenkins access, and a fresh `terraform plan`.

Network ACLs are stateless. Incomplete rules can interrupt NAT egress, ECR pulls, EKS API access, ALB health checks, SSH, and Jenkins UI access. The current ACLs explicitly allow VPC traffic and ephemeral return ports. See the network module guide before changing rules.

## Cost awareness

EKS control-plane hours, EC2 nodes and Jenkins host, NAT Gateway, ALB, public IPv4 addresses, EBS volumes, ECR storage, and data transfer can incur usage-based AWS charges. Review AWS Billing and remove the learning environment when it is no longer needed. Preserve data and Terraform state until teardown is deliberately planned.
