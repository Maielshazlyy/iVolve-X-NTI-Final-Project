# GitHub Actions EKS Deployment Access

This module configures an existing, dedicated IAM user for the GitHub Actions deployment workflow. It attaches `eks:DescribeCluster` for the configured cluster and creates an EKS access entry with `AmazonEKSAdminPolicy` scoped to one Kubernetes namespace.

Create the IAM user and its access key outside Terraform. Store the access key ID and secret access key as GitHub repository Actions secrets named `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. The secret access key is shown only once when created; never commit it or paste it into chat.

This access-key fallback uses long-lived credentials. GitHub OIDC is preferable, but the organization SCP currently blocks creation of the GitHub OIDC provider. Keep this IAM user dedicated to deployment and rotate or revoke its key when it is no longer needed.

The namespace must exist before GitHub Actions manages resources in it. The EKS access policy is scoped to that namespace and does not grant permission to create cluster-scoped resources such as namespaces.

