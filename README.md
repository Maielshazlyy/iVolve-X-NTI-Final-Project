# IVOLVE × NTI Cloud DevOps Accelerator

This project takes the iVolve DevOps training application from local source code to a running, cloud-hosted service. It demonstrates the full delivery path: containerize the application, provision AWS infrastructure with Terraform, build and scan images with GitHub Actions, and continuously deploy Kubernetes manifests with Argo CD.

The application includes a frontend, an authentication API, a roadmap API, and MySQL. The local Docker Compose stack helps develop the services together. In AWS, the services run on Amazon EKS, images are stored in Amazon ECR, MySQL uses persistent EBS storage, and an AWS Application Load Balancer exposes the frontend.

## Project requirements and implementation

| Area | Project outcome |
|---|---|
| GitHub and source | Source, infrastructure, deployment manifests, workflows, and documentation are version-controlled in this repository. |
| Docker | `docker/compose.yaml` runs the frontend, APIs, and MySQL locally. |
| Terraform | Reusable modules provision the VPC, public/private subnets, gateways, network ACLs, EKS with two workers, ECR repositories, IAM permissions, and an encrypted S3 state backend. Jenkins EC2 has been removed from the design. |
| Kubernetes | Manifests define the `ivolve` namespace, Deployments and Services, MySQL StatefulSet and headless Service, gp3 StorageClass, ConfigMap, Secret contract, and frontend Ingress. |
| CI | GitHub Actions builds each service image, scans images with Trivy, pushes immutable commit-tagged images to ECR, then commits the updated image references to Kubernetes manifests. |
| CD | Argo CD watches the Git repository and automatically syncs `kubernetes/overlays/dev` to EKS. The workflow does not call `kubectl` or deploy directly. |
| Documentation | Each major folder has one README explaining that component's files, setup, commands, and verification. Start with the linked folder guides below. |

## Delivery architecture

![Architecture: GitHub Actions CI builds, scans and publishes to ECR; Argo CD syncs Git manifests to EKS](docs/images/ivolve-platform-architecture.png)

```text
Application change
  → GitHub Actions builds and scans Docker images
  → immutable image tags are pushed to Amazon ECR
  → GitHub Actions commits those tags to Kubernetes manifests
  → Argo CD sees the Git change and syncs the dev overlay to Amazon EKS
  → AWS Load Balancer Controller routes browser traffic to the frontend
```

Terraform provisions the AWS foundation and stores dev state remotely in S3. The AWS Load Balancer Controller handles the public ALB; Argo CD manages the application resources declared in Git.

## Repository guides

Each major folder has **one README at its top level**. The guide describes all files and commands for that folder; subfolders do not have separate README files.

| Guide | Covers |
|---|---|
| [`app/README.md`](app/README.md) | Service layout, local development, and application behavior. |
| [`docker/README.md`](docker/README.md) | Local Compose setup, environment values, build, run, and cleanup. |
| [`terraform/README.md`](terraform/README.md) | S3 backend bootstrap, AWS modules, plan/apply, verification, and safe teardown. |
| [`kubernetes/README.md`](kubernetes/README.md) | Manifests, secrets, Argo CD bootstrap/Application, sync, and workload checks. |
| [`.github/README.md`](.github/README.md) | CI workflow, required GitHub secrets, triggers, image publishing, and manifest updates. |
| [`argocd/README.md`](argocd/README.md) | Installing Argo CD and registering the dev Application. |
| [`docs/README.md`](docs/README.md) | Architecture image, demo videos, evidence screenshots, and regeneration steps. |

## Start here

### Local application

Follow [`docker/README.md`](docker/README.md) to create local environment values and launch the complete stack. The source services are under `app/frontend/`, `app/auth-service/`, and `app/roadmap-service/`.

### AWS foundation

Follow [`terraform/README.md`](terraform/README.md) to bootstrap the remote S3 state backend, authenticate to AWS, review the dev environment plan, and provision infrastructure. Terraform provisions two private EKS worker nodes across two Availability Zones and the ECR repositories used by CI.

### GitHub Actions CI

Configure the GitHub repository secrets documented in [`.github/README.md`](.github/README.md). On a pull request, the CI workflow builds and scans service images. On `main`, it additionally pushes immutable images to ECR and commits the matching image references to `kubernetes/base/`.

### Argo CD continuous delivery

Install Argo CD in the cluster, create the `app-secrets` Secret without committing its values, then apply [`argocd/applications/ivolve-dev.yaml`](argocd/applications/ivolve-dev.yaml). Argo CD watches the `main` branch and syncs `kubernetes/overlays/dev`; see [`argocd/README.md`](argocd/README.md) and [`kubernetes/README.md`](kubernetes/README.md).

## Verification evidence

Screenshots and the project walkthrough video are collected in [`docs/README.md`](docs/README.md). The repository includes evidence of the local Compose stack, the application through the ALB, healthy EKS nodes and workloads, successful CI runs, and successful Argo CD synchronization when available.

<details>
<summary>View project screenshots</summary>

### Local Docker Compose

![Local Docker Compose services started](docs/images/evidence/docker-compose-started.png)

### GitHub Actions CI

![GitHub Actions successfully built and scanned images, published to ECR, and updated manifests](docs/images/evidence/github-actions-ci-success.png)

### Argo CD continuous delivery

![Argo CD application is Healthy and Synced](docs/images/evidence/argocd-healthy-synced.png)

### EKS workloads and persistent storage

![EKS nodes and application workloads are healthy, with MySQL storage and Ingress](docs/images/evidence/eks-workloads-healthy.png)

### Application through the AWS ALB

![iVolve application served through the AWS Application Load Balancer](docs/images/evidence/application-live-on-alb.png)

</details>

## Operational and security notes

- Never commit `.env` files, `kubernetes/app-secrets.local`, AWS access keys, GitHub tokens, SSH keys, Terraform state, or secret backend configuration.
- The CI IAM user should only publish images to the project's ECR repositories. Argo CD receives read access to the Git repository and uses its in-cluster identity to manage application resources.
- Review every Terraform plan before applying. Removing the Jenkins module will plan deletion of the Jenkins EC2 instance and related IAM/security-group resources; the apply is intentionally left for the operator to review and approve.
- EKS, worker EC2, NAT Gateway, ALB, public IPv4, EBS, ECR storage, and data transfer can incur charges. For safe shutdown and data retention, use the teardown and backup instructions in [`terraform/README.md`](terraform/README.md).
