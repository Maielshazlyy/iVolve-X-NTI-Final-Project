# Kubernetes Kustomize Overlays

Overlays select and configure the shared Kubernetes base for a particular environment. The deployed environment is [`dev/`](dev/README.md), which targets the existing namespace `ivolve` and uses the `eu-north-1` ECR repositories.

The GitHub Actions workflow applies this overlay after Jenkins pushes a service manifest update:

```bash
kubectl apply -k kubernetes/overlays/dev
```

In normal operation use the **Deploy Dev to EKS** GitHub Actions workflow, which also creates/updates the Kubernetes application Secret and waits for MySQL and the three deployments. The deploy IAM identity is namespace-scoped; cluster-scoped resources such as the `gp3` StorageClass and AWS Load Balancer Controller are installed separately by a cluster administrator.
