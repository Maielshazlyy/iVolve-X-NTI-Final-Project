# Kubernetes Deployment

This section will define the application's desired state on Amazon EKS. GitHub Actions is the selected deployment mechanism for this project; a manifest change or workflow trigger will apply Kubernetes resources to the cluster.

## Planned resources

- Namespace and application configuration.
- Deployments and Services for the frontend, Auth API, and Roadmap API.
- MySQL StatefulSet, persistent storage, and internal Service.
- ConfigMaps, Kubernetes Secrets, probes, resource requests, and ingress.
- `base/` for shared resources and `overlays/dev/` for development-specific values.

## Current status

Only placeholder directories exist. No cluster resources are deployed from this directory yet. Keep real credentials out of manifests; use an appropriate secret-management workflow.
