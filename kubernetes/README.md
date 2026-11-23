# Kubernetes Workloads

This guide covers all Kubernetes resources under `kubernetes/`. GitHub Actions builds, scans, and publishes service images to ECR, then updates image tags in Git. Argo CD watches the Git repository and reconciles the dev overlay into EKS. GitHub Actions has no Kubernetes deploy credentials and does not run `kubectl` against the cluster.

## Manifest map

- `base/namespace.yaml` declares namespace `ivolve`.
- `base/` contains app Deployments and ClusterIP Services, MySQL StatefulSet and headless Service, ConfigMap, Secret example, gp3 StorageClass, and frontend Ingress.
- `overlays/dev/` selects the base resources for the development environment.
- `argocd/applications/ivolve-dev.yaml` defines the Argo CD Application (see [`../argocd/README.md`](../argocd/README.md)).

## Create the application Secret

Secret values are not stored in Git. Before the first sync, create `kubernetes/app-secrets.local` on a trusted workstation with these entries:

```dotenv
MYSQL_ROOT_PASSWORD=replace-with-a-strong-value
DB_USER=ivolve
DB_PASSWORD=replace-with-a-strong-value
SESSION_SECRET=replace-with-a-long-random-value
```

Then, with `kubectl` pointed at the intended EKS cluster and an authorized administrator identity:

```powershell
kubectl apply -f kubernetes/base/namespace.yaml
kubectl create secret generic app-secrets -n ivolve `
  --from-env-file=kubernetes/app-secrets.local `
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f kubernetes/base/storageclass.yaml
```

The local file is ignored by Git. Do not apply `base/app-secrets.example.yaml`; it documents the required secret keys and contains placeholders only. If secret values need rotation, repeat the `kubectl create secret ... | kubectl apply` command. Restart affected pods if the application reads secret values only at startup.

## Argo CD deployment

Install Argo CD and apply the Application manifest as described in [`../argocd/README.md`](../argocd/README.md). Once synced, Argo CD creates/maintains namespaced resources from `overlays/dev`. The AWS Load Balancer Controller and the cluster-scoped gp3 StorageClass are installed separately by a cluster administrator.

When GitHub Actions commits a new immutable ECR image tag into one of the service manifests, Argo CD detects the branch change and applies it to EKS. To check sync and workload health:

```powershell
kubectl config current-context
kubectl get applications -n argocd
kubectl get nodes
kubectl get pods,pvc -n ivolve
kubectl get ingress -n ivolve
```

Argo CD UI/CLI can show the Application's detailed sync and health state. `kubectl` is for verification and authorized administration, not the CI/CD handoff.

## Rollouts on the two-node dev cluster

The dev EKS nodes currently report capacity for 11 Pods each. During an image update, the default Deployment rolling strategy can request a temporary extra Pod (`maxSurge`) while keeping the previous Pod available. If both nodes have reached their Pod capacity, the new Pod remains `Pending` with a `Too many pods` scheduling event even while the old application Pod continues to serve traffic.

The three single-replica application Deployments set this strategy in their manifests:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 0
    maxUnavailable: 1
```

This avoids requesting an extra Pod during a rollout and does not add AWS worker capacity. Since each service has one replica, Kubernetes may stop its old Pod before the replacement is ready; expect a brief service interruption during an update. This tradeoff is for the cost-conscious dev cluster, not a highly available production rollout.

To diagnose a future rollout that stays `Pending`, check the node Pod capacity, Deployment state, and the Pending Pod's scheduler events:

```powershell
kubectl get nodes -o custom-columns=NAME:.metadata.name,MAX-PODS:.status.capacity.pods,ALLOCATABLE-PODS:.status.allocatable.pods
kubectl get deployments -n ivolve
kubectl get pods -n ivolve
kubectl describe pod <pending-pod-name> -n ivolve
```

If the event says `Too many pods`, check the Deployment strategy in Git and Argo CD sync status before considering additional worker nodes, which increase AWS cost.

## AWS Load Balancer Controller

The Terraform EKS module provisions its Pod Identity role and association. Install the controller Helm chart once with cluster-admin access; see the Terraform module and commands documented in [`../terraform/README.md`](../terraform/README.md). The Ingress exposes the frontend through an internet-facing ALB.

## MySQL persistence

MySQL stores its data in a 5 GiB EBS volume provisioned through the gp3 StorageClass. The PVC should be `Bound` and `mysql-0` should be ready. The StorageClass has a `Delete` reclaim policy, so deleting the claim can delete its EBS volume. Back up data before deleting the StatefulSet/PVC or tearing down infrastructure.
