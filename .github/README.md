# GitHub Automation

GitHub Actions workflows live in [`workflows/`](workflows/). Jenkins builds, scans, and publishes the application images to ECR. GitHub Actions deploys those images to Amazon EKS using the self-hosted runner on the Jenkins EC2 host.

- `eks-access-check.yml` verifies AWS and Kubernetes access in the `ivolve` namespace.
- `deploy-dev.yml` creates the app Secret from repository secrets, applies the Kustomize overlay, and rolls out the latest images.

The organization SCP blocks creation of a GitHub OIDC provider, so these workflows use a dedicated IAM deploy user stored as repository Actions secrets. Keep credentials out of workflow files and application manifests. Rotate or revoke the access key when this fallback is no longer needed.
