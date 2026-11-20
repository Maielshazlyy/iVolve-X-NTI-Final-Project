# Development Overlay

This Kustomize overlay configures the deployed development application in the existing `ivolve` namespace. It includes the Auth, Roadmap, and Frontend Deployments/Services, the MySQL StatefulSet and Service, app configuration and Secret reference, and frontend ALB Ingress.

## Normal deployment path

Jenkins updates one service manifest with its published build image tag and pushes that commit to `main`. The GitHub Actions **Deploy Dev to EKS** workflow runs on the self-hosted runner, updates the `app-secrets` Secret from repository secrets, applies this overlay, and waits for MySQL plus all three deployments.

To deploy manually as an administrator (not the routine CI path):

```powershell
kubectl config current-context
kubectl apply -k kubernetes/overlays/dev
kubectl rollout status statefulset/mysql -n ivolve --timeout=600s
kubectl rollout status deployment/auth-service -n ivolve --timeout=300s
kubectl rollout status deployment/roadmap-service -n ivolve --timeout=300s
kubectl rollout status deployment/frontend -n ivolve --timeout=300s
```

Expected result: each rollout reports `successfully rolled out`; `kubectl get pods -n ivolve` shows four Running/ready pods.

## Verify public access

```powershell
kubectl get ingress -n ivolve
```

Open the current `ADDRESS` over HTTP. It is an AWS ALB hostname and can change. The ALB requires the AWS Load Balancer Controller and its IAM Pod Identity association; the `ivolve` namespace and `gp3` StorageClass were provisioned separately by an administrator.

Database credentials and the session signing secret are supplied through GitHub Actions Secrets and the Kubernetes Secret `app-secrets`. Never commit actual secret values into Kustomize files.
