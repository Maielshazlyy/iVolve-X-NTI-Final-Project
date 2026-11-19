# Kubernetes Base Manifests

The base contains the MySQL StatefulSet and internal headless Service, application ConfigMap, Deployments/ClusterIP Services for the auth API, roadmap API, and frontend, plus an AWS ALB Ingress that routes public HTTP traffic to the frontend.

The Ingress requires the AWS Load Balancer Controller. Its IAM permissions and Pod Identity association are managed in Terraform; install the controller with Helm as a cluster administrator before applying the dev overlay. Image references use the dev ECR repositories and mutable `latest` tags; Jenkins also pushes immutable build-number tags for traceability.

`storageclass.yaml` is separate from the Kustomize base because it is cluster-scoped. Apply it once with an administrator kubeconfig after Terraform installs the EKS Pod Identity Agent and EBS CSI add-ons:

```bash
kubectl apply -f kubernetes/base/storageclass.yaml
```

The Kustomize base intentionally excludes Namespace creation. The `ivolve` namespace already exists, and the GitHub deploy identity is limited to that namespace.
