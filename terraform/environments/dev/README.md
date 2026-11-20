# Development Environment

This is the root Terraform configuration for the deployed `ivolve-x-dev` AWS environment in `eu-north-1`. It composes network, Jenkins EC2, EKS, ECR, and GitHub Actions access modules. Its state is stored in S3 after migrating the original local state.

## Current environment outputs

| Output | Deployed value/purpose |
|---|---|
| Region | `eu-north-1` |
| Cluster | `ivolve-x-dev` |
| Worker group | `ivolve-x-dev-workers` |
| Worker nodes | Two `t3.small` EKS nodes in private subnets |
| Jenkins host | Terraform-managed Ubuntu EC2 with restricted SSH/UI access |
| Image repositories | `ivolve-x/dev/frontend`, `ivolve-x/dev/auth-service`, `ivolve-x/dev/roadmap-service` |
| State backend | S3 bucket `ivolve-x-tfstate-335452653010-eu-north-1`, key `ivolve-x/dev/terraform.tfstate` |

`terraform output` prints current resource identifiers. Do not copy public IPs, account identifiers, or credential values into public documentation unless they are intentionally redacted.

## First setup on an authorized workstation

Prerequisites: Terraform `>=1.10`, AWS CLI v2, AWS account access, kubectl, and Helm for the one-time AWS Load Balancer Controller install.

1. Authenticate to the authorized AWS account and region.
2. Copy the backend template if it is not already present:

```powershell
Copy-Item backend.hcl.example backend.hcl
```

3. Confirm `backend.hcl` points to the project S3 bucket, then initialize and inspect:

```powershell
terraform init -backend-config=backend.hcl
terraform state list
terraform validate
terraform plan
```

The current deployment has already been migrated and applied. Its latest reported `terraform plan` was `No changes`.

## Required variable inputs for future plans/applies

This environment intentionally requires the EKS API and Jenkins admin CIDRs and an existing EC2 key pair name. Use your current public IPv4 address rather than reusing an old IP:

```powershell
$publicIp = (Invoke-RestMethod "https://checkip.amazonaws.com").Trim()
$env:TF_VAR_cluster_endpoint_public_access_cidrs = ConvertTo-Json -InputObject @("$publicIp/32") -Compress

$jenkinsCidrs = @("$publicIp/32")
# If the Ansible control host must SSH to Jenkins, append its current public egress IP:
# $jenkinsCidrs += "<ANSIBLE_CONTROL_HOST_EGRESS_IP>/32"
$env:TF_VAR_jenkins_admin_cidrs = ConvertTo-Json -InputObject $jenkinsCidrs -Compress
$env:TF_VAR_jenkins_key_name = "lab28-ansible"
```

Run `terraform plan` after setting required values. Review all CIDRs; do not use `0.0.0.0/0` for Jenkins SSH or UI. If the Ansible host public address changes, refresh it before applying.

## Applying infrastructure changes

```powershell
terraform fmt -recursive
terraform validate
terraform plan
```

Inspect every change, especially EKS cluster access, Jenkins security group ingress, and public/private Network ACL rules. Network ACLs are stateless; the current private ACL includes TCP ephemeral return traffic for NAT egress and the public ACL includes the required return rules. Only apply a reviewed plan:

```powershell
terraform apply
```

The latest project ACL plan applied `2 to add, 2 to change, 0 to destroy`. Afterward both EKS nodes were `Ready`, the app/database pods were `Running`, and the frontend Ingress retained its ALB address.

## Verify Kubernetes access after Terraform

```powershell
$awsExe = "$env:LOCALAPPDATA\Programs\Amazon\AWSCLIV2\aws.exe"
& $awsExe eks update-kubeconfig --name ivolve-x-dev --region eu-north-1
kubectl config current-context
kubectl get nodes
kubectl get pods -n ivolve
kubectl get ingress -n ivolve
```

Expected context is `arn:aws:eks:eu-north-1:<account-id>:cluster/ivolve-x-dev`; nodes should be `Ready`, service pods should be `Running`, and the Ingress should have an ALB address. The exact hostname can change.

## State and secrets safety

- The bucket bootstrap root at `terraform/bootstrap/state-backend/` uses its own local state; this dev environment's state is remote in S3.
- Keep the original local state backup until S3 `terraform state list` and a clean plan are confirmed. The user confirmed the post-migration plan reports `No changes`.
- `backend.hcl`, state files, AWS profiles/credentials, `.tfvars`, and plan files are excluded from Git. Do not remove protection or upload state to the repository.
- S3 state is sensitive and should only be accessible to authorized infrastructure operators.

See [`../../../README.md`](../../../README.md) for the project overview, [`../../bootstrap/state-backend/README.md`](../../bootstrap/state-backend/README.md) for bootstrap, and [`../../modules/README.md`](../../modules/README.md) for module responsibilities.
