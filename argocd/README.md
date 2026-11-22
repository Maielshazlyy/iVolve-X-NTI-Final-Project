# Argo CD Continuous Delivery

Argo CD is the CD controller for this project. It watches `main` in GitHub and reconciles `kubernetes/overlays/dev` into the `ivolve` namespace on EKS. GitHub Actions performs CI and publishes immutable images; it does not deploy to the Kubernetes API.

## Install Argo CD once

Use an administrator kubeconfig for the intended cluster:

```powershell
kubectl config current-context
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl rollout status deployment/argocd-server -n argocd --timeout=300s
```

Argo CD needs read access to the Git repository. This repository is public, so the Application can use its HTTPS URL without stored Git credentials. For a private repository, configure a read-only repository credential in Argo CD.

## Prepare secrets and register the Application

Follow [`../kubernetes/README.md`](../kubernetes/README.md) to create the `ivolve` namespace, application Secret, and cluster-scoped storage resources before the first workload sync. Then register the Application:

```powershell
kubectl apply -f argocd/applications/ivolve-dev.yaml
kubectl get applications -n argocd
```

The Application targets `main` and `kubernetes/overlays/dev`. Automated sync is enabled with pruning and self-healing. Review Git changes before merge because merged manifests are applied to the cluster automatically.

## Verify and operate

```powershell
kubectl get applications -n argocd
kubectl get pods,pvc -n ivolve
kubectl get ingress -n ivolve
```

To access the UI locally, use port forwarding:

```powershell
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Then open `https://localhost:8080`. Argo CD's initial admin secret can be read by an authorized cluster administrator with:

```powershell
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | %{ [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) }
```

Change the initial password after first sign-in and do not publish it. For rollback, revert the Git commit that changed the manifest; Argo CD will sync the reverted desired state.
