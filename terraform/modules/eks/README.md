# EKS Module

Creates an Amazon EKS control plane and a managed EC2 worker group in the private subnets supplied by the network module.

## Resources and access

- Creates separate IAM roles for the EKS control plane and worker nodes.
- Uses the currently latest EKS Kubernetes version exposed by the AWS provider data source.
- Enables private and public Kubernetes API access. The public endpoint is restricted to the CIDRs provided by the environment; use your current public IPv4 address with `/32`.
- Allows the Jenkins-hosted GitHub Actions runner to reach the private Kubernetes API endpoint over TCP 443 using a security-group reference.
- Installs the EKS Pod Identity Agent and Amazon EBS CSI add-ons. A dedicated Pod Identity role scopes EBS permissions to the CSI controller without requiring an IAM OIDC provider.
- Starts with two `t3.small` on-demand nodes, with a configurable range of one to two.

EKS control-plane hours, EC2 worker hours, NAT gateway hours, public IPv4 addresses, and data transfer can incur charges. Review the environment plan and AWS pricing before applying. This module does not create the cluster until `terraform apply` is run.
