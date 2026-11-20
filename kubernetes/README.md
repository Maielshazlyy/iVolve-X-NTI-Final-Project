# Kubernetes Deployment

Jenkins builds and scans each service image, publishes it to ECR, updates that service's Kubernetes manifest to the selected Jenkins build-number image tag, and pushes the manifest change to GitHub. The GitHub Actions `Deploy Dev to EKS` workflow applies the development Kustomize overlay and waits for MySQL and all three application Deployment rollouts.

## Layout and behavior

- `base/` contains the MySQL StatefulSet and persistent EBS claim, app ConfigMap, service Deployments, and internal Services.
- `overlays/dev/` scopes namespaced resources to the existing `ivolve` namespace.
- The workflow creates or updates the Kubernetes Secret from GitHub repository secrets. Credentials are not stored in manifests.
- `base/storageclass.yaml` is cluster-scoped and must be installed once by a cluster administrator; the GitHub deploy identity is limited to the `ivolve` namespace.
- `base/frontend-ingress.yaml` defines an internet-facing AWS Application Load Balancer Ingress routing HTTP traffic to the frontend ClusterIP Service.
- The Ingress requires the AWS Load Balancer Controller, its EKS Pod Identity role/association, and tagged public subnets. The cluster administrator installs the controller; the GitHub deploy identity applies the namespaced Ingress.

## Development deployment

Run the relevant Jenkins service job. Its manifest push triggers **Deploy Dev to EKS** automatically; the workflow can also be run manually. MySQL data is stored on an encrypted 5 GiB `gp3` EBS volume. The StorageClass uses `Delete` reclaim policy, so deleting the MySQL PVC deletes its EBS volume.

After the AWS Load Balancer Controller is installed, the deployment workflow applies the Ingress. Get the public URL with `kubectl get ingress -n ivolve`.

## One-time AWS Load Balancer Controller install

The controller is cluster-scoped, so install it with a kubeconfig that has cluster-admin access. First apply the Terraform IAM role, controller policy, and Pod Identity association from `terraform/environments/dev`. Then, from that Terraform directory in PowerShell, install the pinned chart:

```powershell
$clusterName = terraform output -raw eks_cluster_name
$vpcId = terraform output -raw vpc_id

helm repo add eks https://aws.github.io/eks-charts
helm repo update eks
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller `
  --namespace kube-system `
  --version 3.6.3 `
  --set clusterName=$clusterName `
  --set region=eu-north-1 `
  --set vpcId=$vpcId `
  --set serviceAccount.create=true `
  --set serviceAccount.name=aws-load-balancer-controller

kubectl rollout status deployment/aws-load-balancer-controller `
  --namespace kube-system --timeout=300s
kubectl get ingressclass
```

The public ALB is created when the GitHub Actions deployment workflow applies `kubernetes/overlays/dev`. It is an AWS billable resource. Confirm the Ingress address with `kubectl get ingress -n ivolve` and test its HTTP URL in a browser.

## Verify the deployed application

With kubectl pointed at `ivolve-x-dev`, run:

```powershell
kubectl get nodes
kubectl get pods -n ivolve
kubectl get pvc -n ivolve
kubectl get ingress -n ivolve
```

Expected result: worker nodes are `Ready`; auth-service, roadmap-service, frontend, and MySQL are Running/ready; the MySQL PVC is `Bound`; and the frontend Ingress has an ALB `ADDRESS`. The user confirmed these checks passed after applying the ACLs.
