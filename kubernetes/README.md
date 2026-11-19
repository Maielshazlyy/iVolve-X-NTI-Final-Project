# Kubernetes Deployment

Jenkins builds and scans each service image, then pushes both its Jenkins build-number tag and `latest` to ECR. The GitHub Actions `Deploy Dev to EKS` workflow applies the development Kustomize overlay and rolls the three application Deployments to the latest images.

## Layout and behavior

- `base/` contains the MySQL StatefulSet and persistent EBS claim, app ConfigMap, service Deployments, and internal Services.
- `overlays/dev/` scopes namespaced resources to the existing `ivolve` namespace.
- The workflow creates or updates the Kubernetes Secret from GitHub repository secrets. Credentials are not stored in manifests.
- `base/storageclass.yaml` is cluster-scoped and must be installed once by a cluster administrator; the GitHub deploy identity is limited to the `ivolve` namespace.
- The frontend is a ClusterIP Service. Use `kubectl port-forward` for local verification; public ingress is a later step.

## Development deployment

Run all three Jenkins service jobs so each ECR repository receives a fresh `latest` image, then trigger **Deploy Dev to EKS** from GitHub Actions. MySQL data is stored on an encrypted 5 GiB `gp3` EBS volume. The StorageClass uses `Delete` reclaim policy, so deleting the MySQL PVC deletes its EBS volume.
