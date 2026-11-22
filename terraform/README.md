# Terraform and AWS Infrastructure

This guide covers the Terraform configuration under `terraform/`: the S3 state backend, AWS dev environment, reusable modules, commands, and operational notes. The design provisions an AWS network and EKS/ECR platform for the application. GitHub Actions is the CI system; Argo CD handles CD. Jenkins EC2 and its Ansible setup have been removed.

## Resources managed

- VPC in two Availability Zones with public/private subnets, Internet Gateway, a cost-conscious shared NAT Gateway, routes, subnet tags, and public/private Network ACLs.
- EKS control plane and managed worker group across private subnets, EBS CSI driver with Pod Identity, and IAM resources for the AWS Load Balancer Controller.
- Private ECR repositories for `frontend`, `auth-service`, and `roadmap-service`.
- Existing IAM user policy allowing GitHub Actions CI to push images only to the project's ECR repositories.
- Encrypted, versioned S3 bucket for remote dev state.

Terraform does not install Argo CD itself. Follow [`../argocd/README.md`](../argocd/README.md) to install it and register the Kubernetes Application.

## Directory map

| Path | Purpose |
|---|---|
| `bootstrap/state-backend/` | One-time creation of the encrypted, versioned S3 state bucket. |
| `environments/dev/` | Root configuration that composes network, EKS, ECR, and GitHub Actions CI IAM modules. |
| `modules/network/` | VPC, subnets, gateways, routes, and network ACLs. |
| `modules/eks/` | EKS cluster and nodes, Pod Identity, EBS CSI, and Load Balancer Controller IAM. |
| `modules/ecr/` | Private service image repositories. |
| `modules/github-actions/` | Least-privilege ECR push policy for the existing GitHub Actions IAM user. |

## Prerequisites

Use Terraform 1.10+, AWS CLI v2, an authorized AWS identity, and PowerShell. `kubectl` and Helm are needed for cluster operations. Authenticate before Terraform commands that read remote state or AWS resources. Do not put credentials in Terraform files.

## Bootstrap remote state

The backend must exist before the dev state can be stored in it. From the repository root:

```powershell
Set-Location terraform/bootstrap/state-backend
terraform init
terraform validate
terraform plan
terraform apply
terraform output -raw state_bucket_name
```

Create the ignored backend configuration from the example, confirm the bucket name matches the bootstrap output, and migrate existing state:

```powershell
Copy-Item terraform/environments/dev/backend.hcl.example terraform/environments/dev/backend.hcl
Set-Location terraform/environments/dev
terraform init -migrate-state -backend-config=backend.hcl
terraform state list
terraform plan
```

Keep a recovery copy until the state is visible in S3 and a full plan has no unexpected changes.

## Plan and apply the dev environment

From `terraform/environments/dev`, set the current public IP for the EKS public API allow-list:

```powershell
$publicIp = (Invoke-RestMethod "https://checkip.amazonaws.com").Trim()
$env:TF_VAR_cluster_endpoint_public_access_cidrs = ConvertTo-Json -InputObject @("$publicIp/32") -Compress

terraform init -backend-config=backend.hcl
terraform state list
terraform fmt -recursive
terraform validate
terraform plan
```

Review the full plan before applying. Terraform no longer asks for Jenkins key names, Jenkins admin CIDRs, or an EC2 size. The plan should remove the Jenkins EC2 module and its related permissions/security group; it should not destroy EKS, ECR, the VPC, or the S3 backend. Apply only after confirming that the plan matches that expectation:

```powershell
terraform apply
```

This change does not delete the pre-existing IAM user or its access keys. It updates the Terraform-managed inline IAM policy to authorize ECR image publishing for the CI workflow.

## Verify EKS

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

Expected: EKS nodes are `Ready`, the application and MySQL pods are healthy, the MySQL PVC is `Bound`, and the frontend Ingress has an ALB address. Install the AWS Load Balancer Controller once with cluster-admin privileges; its commands are in [`../kubernetes/README.md`](../kubernetes/README.md).

## Cost and data retention

- The VPC, EKS, worker EC2, NAT Gateway, ALB, public IPv4, EBS volumes, ECR storage, and data transfer can incur charges. Stopping worker nodes alone does not stop all EKS/NAT/ALB charges.
- Before destroying infrastructure, back up MySQL data and export any ECR images that must be retained. The MySQL StorageClass has `Delete` reclaim policy; deleting its PVC can delete its EBS volume.
- Use `terraform plan -destroy` and inspect the complete resource list before any teardown. Keep the S3 state bucket until all state-managed resources are intentionally removed and the state is no longer needed.
- Do not commit `backend.hcl`, Terraform state, `.terraform/`, plan files, AWS credentials, SSH keys, or secret `.tfvars` files.
- Network ACLs are stateless; inspect return-path rules before changing live ACLs.
