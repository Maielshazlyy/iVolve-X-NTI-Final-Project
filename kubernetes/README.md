# Kubernetes Deployment

Jenkins builds and scans each service image, then pushes both its Jenkins build-number tag and `latest` to ECR. The GitHub Actions `Deploy Dev to EKS` workflow applies the development Kustomize overlay and rolls the three application Deployments to the latest images.

## Layout and behavior

- `base/` contains the MySQL StatefulSet and persistent EBS claim, app ConfigMap, service Deployments, and internal Services.
- `overlays/dev/` scopes namespaced resources to the existing `ivolve` namespace.
- The workflow creates or updates the Kubernetes Secret from GitHub repository secrets. Credentials are not stored in manifests.
- `base/storageclass.yaml` is cluster-scoped and must be installed once by a cluster administrator; the GitHub deploy identity is limited to the `ivolve` namespace.
- `base/frontend-ingress.yaml` defines an internet-facing AWS Application Load Balancer Ingress routing HTTP traffic to the frontend ClusterIP Service.
- The Ingress requires the AWS Load Balancer Controller, its EKS Pod Identity role/association, and tagged public subnets. The cluster administrator installs the controller; the GitHub deploy identity applies the namespaced Ingress.

## Development deployment

Run all three Jenkins service jobs so each ECR repository receives a fresh `latest` image, then trigger **Deploy Dev to EKS** from GitHub Actions. MySQL data is stored on an encrypted 5 GiB `gp3` EBS volume. The StorageClass uses `Delete` reclaim policy, so deleting the MySQL PVC deletes its EBS volume.

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
