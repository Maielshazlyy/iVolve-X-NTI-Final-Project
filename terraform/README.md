# AWS Infrastructure with Terraform

This is the single guide for everything under `terraform/`: backend bootstrap, the deployed dev environment, reusable modules, required inputs, verification, and operational safety. Terraform provisions the IVOLVE environment in `eu-north-1`.

## What Terraform manages

- A VPC across two Availability Zones, public/private subnets, Internet Gateway, NAT Gateway, routes, subnet tags, and stateless Network ACLs.
- A restricted Jenkins EC2 controller with an instance profile and repository-scoped ECR publishing permissions.
- An EKS control plane, private managed worker group, cluster access, EKS Pod Identity, the EBS CSI add-on, and IAM resources for the AWS Load Balancer Controller.
- Private ECR repositories for `frontend`, `auth-service`, and `roadmap-service`.
- Namespace-scoped EKS access for the GitHub Actions deploy identity.
- A versioned, encrypted S3 bucket for the dev Terraform state. The bootstrap root keeps its own state locally.

## Current deployment

- The VPC, EKS cluster `ivolve-x-dev`, and worker group are deployed; two `t3.small` worker nodes were confirmed `Ready`.
- Jenkins runs on the Terraform-managed EC2 host and is configured by Ansible.
- ECR has the three service repositories, and EKS runs the app plus MySQL.
- The public and private Network ACLs were applied, followed by successful node, pod, and Ingress checks.
- The dev state is remote in S3 with key `ivolve-x/dev/terraform.tfstate`; the bucket name is account-specific and comes from the bootstrap output.
- The last reported full dev plan after applying the ACLs returned `No changes`.

## Folder map

| Path | Purpose |
|---|---|
| `bootstrap/state-backend/` | One-time creation of the private, encrypted, versioned S3 state bucket. |
| `environments/dev/` | Root configuration for the running dev environment; composes all modules and uses the S3 backend. |
| `modules/network/` | VPC, subnets, Internet/NAT routes, subnet tags, and public/private ACLs. One shared NAT Gateway is the lower-cost default. |
| `modules/jenkins/` | Ubuntu EC2 controller, instance profile, restricted admin access, encrypted gp3 volume, IMDSv2, and scoped ECR push policy. |
| `modules/eks/` | EKS control plane, private managed nodes, cluster access, Pod Identity, EBS CSI, and Load Balancer Controller IAM role/policy. Add-on versions are pinned to the verified versions. |
| `modules/ecr/` | Private repositories with push scanning, encryption, immutable tags, and untagged-image cleanup. |
| `modules/github-actions/` | Dedicated IAM deploy identity and namespace-scoped EKS access. The AWS organization SCP blocked creation of the GitHub OIDC provider, so the current workflow uses dedicated access-key secrets. |

## Prerequisites and authentication

Use Terraform 1.10 or newer, AWS CLI v2, an authorized AWS identity, and PowerShell. `kubectl` and Helm are needed to verify the cluster and install the AWS Load Balancer Controller. Authenticate with the approved AWS login flow before running Terraform; credentials must be active to refresh remote state and read live AWS resources.

## Bootstrap the S3 state backend

The backend bucket must exist before the dev environment can use it. From PowerShell at the repository root:

```powershell
Set-Location terraform/bootstrap/state-backend
terraform init
terraform validate
terraform plan
terraform apply
terraform output -raw state_bucket_name
```

The bucket bootstrap intentionally uses local state because a Terraform backend cannot create itself. On an authorized workstation, create the ignored backend config from the example, check its bucket value against the bootstrap output, then migrate the existing dev state:

```powershell
Copy-Item terraform/environments/dev/backend.hcl.example terraform/environments/dev/backend.hcl
Set-Location terraform/environments/dev
terraform init -migrate-state -backend-config=backend.hcl
terraform state list
terraform plan
```

Confirm the migration when prompted. Keep the local pre-migration state recovery copy until the S3 state is confirmed and a full plan shows no unintended changes.

## Plan and apply the dev environment

From `terraform/environments/dev`, set trusted administrator CIDRs and an existing EC2 key pair. Use the current public IP, not a previously recorded one:

```powershell
$publicIp = (Invoke-RestMethod "https://checkip.amazonaws.com").Trim()
$env:TF_VAR_cluster_endpoint_public_access_cidrs = ConvertTo-Json -InputObject @("$publicIp/32") -Compress
$env:TF_VAR_jenkins_admin_cidrs = ConvertTo-Json -InputObject @("$publicIp/32") -Compress
$env:TF_VAR_jenkins_key_name = "lab28-ansible"

terraform init -backend-config=backend.hcl
terraform state list
terraform fmt -recursive
terraform validate
terraform plan
```

If the Ansible control host also needs SSH access to Jenkins, append its current public egress IP with `/32` to `TF_VAR_jenkins_admin_cidrs`. Never use `0.0.0.0/0` for Jenkins SSH or its web UI. Inspect every planned CIDR, resource replacement, EKS add-on, and cost before applying:

```powershell
terraform apply
```

## Verify the deployed cluster

```powershell
$awsExe = "$env:LOCALAPPDATA\Programs\Amazon\AWSCLIV2\aws.exe"
& $awsExe eks update-kubeconfig --name ivolve-x-dev --region eu-north-1
kubectl config current-context
kubectl get nodes
kubectl get pods -n ivolve
kubectl get pvc -n ivolve
kubectl get ingress -n ivolve
terraform plan
```

Expected: the kube context points to `ivolve-x-dev`, nodes are `Ready`, app and MySQL pods are ready, the MySQL PVC is `Bound`, the Ingress has an ALB address, and Terraform has no unreviewed drift. The Load Balancer Controller is installed once by a cluster administrator with Helm; its commands and the application manifests are in [`../kubernetes/README.md`](../kubernetes/README.md).

## State, secrets, and cost

- Do not commit `backend.hcl`, Terraform state, `.terraform/`, plan files, AWS credentials, private keys, or secret `.tfvars` files.
- State contains sensitive infrastructure data; restrict S3 access to authorized operators and keep the recovery copy until migration is verified.
- EKS hours, EC2 instances, NAT Gateway, ALB, public IPv4 addresses, EBS volumes, ECR storage, and data transfer can incur AWS charges. Review the current AWS bill and plan a deliberate teardown when the learning environment is no longer needed.
- Network ACLs are stateless. Missing return-path rules can interrupt NAT egress, ECR pulls, EKS API traffic, ALB health checks, SSH, and Jenkins UI access. Review the full plan before changing ACLs on live subnets.
