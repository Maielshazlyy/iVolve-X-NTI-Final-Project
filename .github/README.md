# GitHub Actions CI

This guide covers workflows in `.github/workflows/`. The CI workflow builds and scans service container images, publishes successful `main` builds to ECR with immutable commit-SHA tags, and updates the matching Kubernetes image references in Git. Argo CD handles deployment after that Git change; no GitHub Actions workflow deploys directly to EKS.

## Workflow

`workflows/ci.yml` runs for application changes on pull requests and pushes to `main`, and can also be started manually. It builds the frontend, auth service, and roadmap service, scans the images with Trivy, and fails on unfixed HIGH/CRITICAL findings. Pull requests build and scan but do not use AWS credentials or push images. On `main`, it authenticates to ECR, publishes images tagged with the commit SHA, and commits those tags to `kubernetes/base/*.yaml`.

Argo CD detects the updated Git manifests and syncs `kubernetes/overlays/dev` to the `ivolve` namespace. Check sync/health from Argo CD; use `kubectl get pods -n ivolve` to verify runtime state.

## Required GitHub repository secrets

Configure these under **Settings → Secrets and variables → Actions**:

| Secret | Purpose |
|---|---|
| `AWS_ACCESS_KEY_ID` | Access key for the existing CI IAM user. |
| `AWS_SECRET_ACCESS_KEY` | Secret key for that user. |

Terraform limits the user to push images to the three project ECR repositories. The AWS Organizations policy blocks GitHub OIDC provider creation in this account, so this implementation uses the existing access-key based identity. Rotate credentials if they were exposed; never put them in a workflow file.

Application database/session secrets are created in the Kubernetes cluster once by an administrator and are not consumed by this CI workflow. See [`../kubernetes/README.md`](../kubernetes/README.md).

## Verify a run

In GitHub, open **Actions → Build, scan, and publish images**. A successful run on `main` should show image build and scan success, image pushes to ECR, and a commit updating service manifests. Argo CD should then report the `ivolve-dev` Application as synced and healthy.

## Permissions and behavior

The workflow uses `contents: write` so it can commit new image references. It does not need an EKS deployment identity, Kubernetes API access, self-hosted runner, or Jenkins. An app change triggers all three service image builds; tags remain immutable and match the source commit SHA.
