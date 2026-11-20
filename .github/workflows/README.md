# GitHub Actions Workflows

## EKS access check

`eks-access-check.yml` is a manually run check that connects to EKS and verifies that the deploy identity can manage Deployments in the `ivolve` namespace.

From the repository, open **Actions → EKS deployment access check → Run workflow**. A successful run should list deployments and return `yes` for the namespace-scoped `can-i` checks. It needs the same AWS secrets and self-hosted runner as the deployment workflow.

## Development deployment

`deploy-dev.yml` runs on the self-hosted Linux runner attached to the Jenkins EC2 host. It updates the Kubernetes `app-secrets` Secret from repository secrets, applies `kubernetes/overlays/dev`, waits for MySQL and application rollouts, and prints the resulting resources. It runs manually or when Jenkins pushes a change to one of the three service manifests on `main`.

Before the first deployment:

1. Run Terraform to install EKS Pod Identity and the Amazon EBS CSI add-ons.
2. Using an administrator kubeconfig, apply `kubernetes/base/storageclass.yaml` once. The GitHub deploy identity has namespace-scoped access and cannot create cluster-scoped StorageClasses.
3. Add repository Actions secrets `MYSQL_ROOT_PASSWORD`, `DB_USER`, `DB_PASSWORD`, and `SESSION_SECRET` in addition to `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
4. Run the Jenkins pipeline for auth-service, roadmap-service, and frontend. Jenkins publishes immutable build-number tags, updates the corresponding manifest, and pushes the change; that push starts deployment automatically.
5. From **Actions**, you can still run **Deploy Dev to EKS** manually for a deliberate re-apply.

The workflow is event-driven for Jenkins manifest commits and also supports manual dispatch. Jenkins uses immutable build-number tags so the manifest commit records exactly which image version is deployed.

## Runner prerequisites and verification

The deploy job runs on labels `self-hosted`, `linux`, and `x64` on the Jenkins EC2 host. That host needs an active GitHub Actions runner service, AWS CLI v2, `kubectl`, and network access to the EKS API. The workflow checks out manifests, configures AWS credentials, updates kubeconfig, writes the Kubernetes Secret through a temporary file, applies the dev overlay, waits for MySQL and all three Deployments, and prints resources.

Required repository Actions secrets are `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `MYSQL_ROOT_PASSWORD`, `DB_USER`, `DB_PASSWORD`, and `SESSION_SECRET`. Store values only in GitHub's secret settings. The AWS deploy user's access-key approach is a fallback because the AWS Organization SCP denies OIDC provider creation.

To verify the outcome, open the latest successful run in **Actions**, then use an EKS-admin kubeconfig to run `kubectl get pods -n ivolve` and `kubectl get ingress -n ivolve`. Expected result is ready/running pods and a populated ALB address.
