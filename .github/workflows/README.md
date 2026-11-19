# GitHub Actions Workflows

## EKS access check

`eks-access-check.yml` is a manually run check that connects to EKS and verifies that the deploy identity can manage Deployments in the `ivolve` namespace.

## Development deployment

`deploy-dev.yml` runs on the self-hosted Linux runner attached to the Jenkins EC2 host. It updates the Kubernetes `app-secrets` Secret from repository secrets, applies `kubernetes/overlays/dev`, waits for MySQL and application rollouts, and prints the resulting resources. It runs manually or when Jenkins pushes a change to one of the three service manifests on `main`.

Before the first deployment:

1. Run Terraform to install EKS Pod Identity and the Amazon EBS CSI add-ons.
2. Using an administrator kubeconfig, apply `kubernetes/base/storageclass.yaml` once. The GitHub deploy identity has namespace-scoped access and cannot create cluster-scoped StorageClasses.
3. Add repository Actions secrets `MYSQL_ROOT_PASSWORD`, `DB_USER`, `DB_PASSWORD`, and `SESSION_SECRET` in addition to `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
4. Run the Jenkins pipeline for auth-service, roadmap-service, and frontend. Jenkins publishes immutable build-number tags, updates the corresponding manifest, and pushes the change; that push starts deployment automatically.
5. From **Actions**, you can still run **Deploy Dev to EKS** manually for a deliberate re-apply.

The workflow is event-driven for Jenkins manifest commits and also supports manual dispatch. Jenkins uses immutable build-number tags so the manifest commit records exactly which image version is deployed.
