# EKS Module

Creates an Amazon EKS control plane and a managed EC2 worker group in the private subnets supplied by the network module.

## Resources and access

- Creates separate IAM roles for the EKS control plane and worker nodes.
- Uses the EKS Kubernetes version selected by the environment's supported-version data source. EKS add-on versions are pinned to the deployed, verified versions (`eks-pod-identity-agent` `v1.5.0-eksbuild.3`; `aws-ebs-csi-driver` `v1.68.0-eksbuild.1`) so unrelated Terraform applies do not silently upgrade them.
- Enables private and public Kubernetes API access. The public endpoint is restricted to the CIDRs provided by the environment; use your current public IPv4 address with `/32`.
- Allows the Jenkins-hosted GitHub Actions runner to reach the private Kubernetes API endpoint over TCP 443 using a security-group reference.
- Installs the EKS Pod Identity Agent and Amazon EBS CSI add-ons. A dedicated Pod Identity role scopes EBS permissions to the CSI controller without requiring an IAM OIDC provider.
- Provisions a dedicated IAM policy, role, and EKS Pod Identity association for the AWS Load Balancer Controller. The IAM policy is the upstream controller policy pinned to release v3.6.3.
- Starts with two `t3.small` on-demand nodes, with a configurable range of one to two.

The AWS Load Balancer Controller itself is installed by Helm using the associated service account; see the Kubernetes README for the one-time cluster-admin install. The controller uses explicit region and VPC values instead of relying on node IMDS access.

EKS control-plane hours, EC2 worker hours, NAT gateway hours, public IPv4 addresses, and data transfer can incur charges. Review the environment plan and AWS pricing before applying. This module does not create the cluster until `terraform apply` is run.
