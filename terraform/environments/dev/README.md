# Development Environment

This directory composes the project's development AWS environment from modules under `terraform/modules/`.

## Implemented configuration

- `versions.tf` — Terraform and AWS provider version requirements.
- `providers.tf` — AWS region and default resource tags.
- `variables.tf` — project name, environment, region, cluster name, VPC/subnet CIDRs, and NAT choice.
- `main.tf` — calls the reusable network, EKS, ECR, Jenkins, and GitHub Actions modules.
- `outputs.tf` — exposes the VPC, subnet, Availability Zone, cluster, node group, image repository, Jenkins host, and GitHub deployment user details.

Defaults target `eu-north-1`, two Availability Zones, VPC CIDR `10.40.0.0/16`, and one shared NAT Gateway. The shared NAT keeps the development design simpler and cheaper than one NAT per AZ, but it is not a highly available production design.

## Prepare and review

Before planning, set the public IP CIDR allowed to access the Kubernetes API. The following PowerShell commands use your current public IPv4 and keep it in the current shell only:

```powershell
$publicIp = (Invoke-RestMethod "https://checkip.amazonaws.com").Trim()
$env:TF_VAR_cluster_endpoint_public_access_cidrs = "[`"$publicIp/32`"]"
```

Run from this directory after configuring AWS CLI credentials for the account and region:

```powershell
terraform init
terraform fmt -recursive
terraform validate
terraform plan
```

The backend is local for now; S3 state storage is a later bootstrap task. `terraform plan` previews infrastructure changes. Review the resource counts and costs before `terraform apply`. The EKS API is public but restricted to the CIDR configured above; private access remains enabled for in-VPC clients.

The GitHub Actions module configures a dedicated IAM user with `eks:DescribeCluster` and an EKS access entry scoped to the `ivolve` namespace. Create the IAM user `ivolve-x-dev-github-deployer` and its access key in IAM before planning. Add the key pair as repository secrets `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. Create the `ivolve` namespace once with an administrator kubeconfig before running the GitHub access-check workflow.
