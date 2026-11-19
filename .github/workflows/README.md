# GitHub Actions Workflows

## EKS access check

`eks-access-check.yml` is a manually run check that connects to EKS and verifies that the deploy identity can manage Deployments in the `ivolve` namespace.

## Development deployment

`deploy-dev.yml` runs on the self-hosted Linux runner attached to the Jenkins EC2 host. It updates the Kubernetes `app-secrets` Secret from repository secrets, applies `kubernetes/overlays/dev`, waits for MySQL and application rollouts, and prints the resulting resources.

Before the first deployment:

1. Run Terraform to install EKS Pod Identity and the Amazon EBS CSI add-ons.
2. Using an administrator kubeconfig, apply `kubernetes/base/storageclass.yaml` once. The GitHub deploy identity has namespace-scoped access and cannot create cluster-scoped StorageClasses.
3. Add repository Actions secrets `MYSQL_ROOT_PASSWORD`, `DB_USER`, `DB_PASSWORD`, and `SESSION_SECRET` in addition to `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
4. Run the Jenkins pipeline for auth-service, roadmap-service, and frontend so each ECR repository has an updated `latest` image.
5. From **Actions**, run **Deploy Dev to EKS**.

The workflow is intentionally manual for the dev environment. Jenkins also publishes immutable build-number tags; `latest` is used here to keep the first deployment flow simple.
