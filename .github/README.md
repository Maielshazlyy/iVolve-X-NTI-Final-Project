# GitHub Actions and Repository Automation

This is the single guide for the GitHub automation in `.github/workflows/`. It covers the EKS access check, the development deployment, required repository secrets, the self-hosted runner, and how to verify a run.

## Workflows

| Workflow | File | Trigger | Purpose |
|---|---|---|---|
| Deploy Dev to EKS | `workflows/deploy-dev.yml` | Manual dispatch or a service manifest push to `main` | Writes/updates `app-secrets`, applies the Kustomize dev overlay, waits for MySQL and all three service Deployments, and reports resources. |
| EKS deployment access check | `workflows/eks-access-check.yml` | Manual dispatch | Confirms the deploy identity can list Deployments and perform namespace-scoped checks in `ivolve`. |

The normal delivery path is Jenkins building and scanning an image, pushing it to ECR, and committing the new immutable image tag to that service's manifest. That manifest commit triggers the deployment workflow. The workflow can also be run manually from **GitHub → Actions → Deploy Dev to EKS → Run workflow**.

## Runner requirements

Both workflows use the self-hosted Linux runner installed on the Jenkins EC2 host with labels `self-hosted`, `linux`, and `x64`. The runner service must be online. The host needs AWS CLI v2, `kubectl`, outbound GitHub access, and private network access to the EKS API on TCP 443.

The app deploy identity has EKS access scoped to the existing `ivolve` namespace. Therefore, an EKS administrator must create the namespace and install cluster-scoped resources separately. Before the first workflow deployment:

1. Provision EKS Pod Identity and the EBS CSI add-on through Terraform.
2. Apply `kubernetes/base/storageclass.yaml` once with an administrator kubeconfig.
3. Install the AWS Load Balancer Controller and its IAM Pod Identity association as an EKS administrator.
4. Ensure namespace `ivolve` exists.
5. Add the repository secrets below and run the Jenkins service pipelines to publish images and update manifests.

## Required repository Actions secrets

Add these under **Repository → Settings → Secrets and variables → Actions → New repository secret**. Never add their values to workflow files or commit them.

| Secret | Used for |
|---|---|
| `AWS_ACCESS_KEY_ID` | Dedicated deployment IAM user's access key ID. |
| `AWS_SECRET_ACCESS_KEY` | Secret access key paired with the deployment IAM user. |
| `MYSQL_ROOT_PASSWORD` | MySQL root password in the Kubernetes Secret. |
| `DB_USER` | Application database username. |
| `DB_PASSWORD` | Application database password. |
| `SESSION_SECRET` | Frontend session signing secret. |

GitHub OIDC was not available in this AWS account because the organization's Service Control Policy denied creation of the OIDC provider. The current workflow uses a dedicated IAM user's access keys. Keep that user limited to this deployment, rotate or revoke its key when appropriate, and do not reuse personal credentials.

## Run and verify

1. Open the repository's **Actions** tab.
2. Select **Deploy Dev to EKS** and choose **Run workflow** for a manual deployment, or push a service manifest update through Jenkins.
3. Check that the AWS credential setup, kubeconfig, Secret update, manifest apply, MySQL wait, three rollout checks, and resource summary all succeed.
4. With an EKS-admin kubeconfig, confirm `kubectl get pods -n ivolve` shows the four app/database pods ready and `kubectl get ingress -n ivolve` has an ALB address.

The separate **EKS deployment access check** can be run from the same Actions page. A successful run lists deployments in `ivolve` and returns the expected `yes` results for namespace-scoped permissions.

For service images and the Jenkins manifest-push step, see [`../jenkins/README.md`](../jenkins/README.md). For Kubernetes manifests, storage, Ingress, and workload checks, see [`../kubernetes/README.md`](../kubernetes/README.md).
