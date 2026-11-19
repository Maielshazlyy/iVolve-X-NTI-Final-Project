# Development Kubernetes Overlay

This overlay applies the shared application workloads to the `ivolve` namespace. Run it through the GitHub Actions `Deploy Dev to EKS` workflow after all Jenkins service jobs have pushed their images to ECR. The workflow restarts the application pods so Kubernetes pulls the updated `latest` tags.

The frontend is internal-only. From a workstation with an authorized EKS kubeconfig, use:

```bash
kubectl port-forward service/frontend 3000:3000 --namespace ivolve
```

Then open `http://localhost:3000`.
