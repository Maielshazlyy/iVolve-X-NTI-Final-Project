# IVOLVE × NTI Cloud DevOps Project

An end-to-end cloud delivery project for the IVOLVE microservices application. It brings together local containers, AWS infrastructure, configuration management, Jenkins-based continuous integration, Kubernetes, and GitHub Actions deployment.

> **Deployment choice:** this implementation uses GitHub Actions to deploy to Amazon EKS. The project brief names Argo CD; GitHub Actions is used here in its place, so the cluster is updated by workflow runs rather than by a continuously reconciling GitOps controller.

## Project goals

- Run the application and MySQL locally with Docker Compose.
- Provision a reproducible AWS environment with Terraform.
- Configure the Jenkins host with reusable Ansible roles.
- Build, scan, and publish service images through Jenkins.
- Keep Kubernetes manifests in Git and deploy their changes to EKS through GitHub Actions.
- Document the architecture, setup, operating steps, and evidence for each stage.

## Architecture

### Delivery workflow

```mermaid
flowchart LR
    Dev[Application change] --> Repo[GitHub source repository]
    Repo --> Jenkins[Jenkins on EC2<br/>dedicated agent and shared library]
    Jenkins --> Test[Test and build service images]
    Test --> Scan[Trivy image scan]
    Scan --> ECR[Amazon ECR]
    ECR --> Manifests[Update image tags in Kubernetes manifests]
    Manifests --> Git[Commit manifest change to GitHub]
    Git --> Actions[GitHub Actions deployment workflow]
    Actions --> IAMUser[Dedicated IAM deploy user<br/>repository secrets]
    IAMUser --> EKS[Amazon EKS]
    EKS --> Rollout[Kubernetes rollout]
```

Jenkins is responsible for CI: it builds and scans images and publishes them to ECR. GitHub Actions is the selected deployment mechanism for EKS. The organization SCP currently blocks creation of the GitHub OIDC provider, so the temporary fallback is a dedicated IAM deploy user whose access keys are stored as repository secrets. The user is limited to the application namespace; OIDC remains the preferred option when the organization policy permits it.

GitHub Actions performs deployment when a workflow runs. It does not provide Argo CD's continuous drift detection or automatic reconciliation between runs.

### Application services

```mermaid
flowchart LR
    Browser[Browser] --> Frontend[Frontend<br/>Node.js / Express :3000]
    Frontend --> Auth[Auth service<br/>Flask :5000]
    Frontend --> Roadmap[Roadmap service<br/>Spring Boot :8080]
    Auth --> MySQL[(MySQL :3306)]
```

| Service | Technology | Port | Responsibility |
|---|---|---:|---|
| Frontend | Node.js, Express, EJS | 3000 | Login, signup, and roadmap pages |
| Auth service | Python, Flask | 5000 | Signup and login API; persists user accounts |
| Roadmap service | Java 21, Spring Boot | 8080 | Serves roadmap data through an API |
| Database | MySQL 8 | 3306 | Stores authentication data for the Auth service |

The frontend calls the Auth and Roadmap services over the internal container network. Only the frontend port is published to the host for local development. The Auth service creates its `users` table when it connects to the database.

## Technology

| Area | Tools |
|---|---|
| Application | Node.js, Express, EJS, Python, Flask, Java 21, Spring Boot, MySQL |
| Containers | Docker, Docker Compose |
| Infrastructure | AWS, Terraform, Amazon EKS, Amazon ECR, S3 |
| Configuration | Ansible playbooks, roles, and dynamic inventory |
| CI | Jenkins, a dedicated agent, Groovy Shared Library, Trivy |
| Deployment | GitHub Actions, IAM deploy user, Kubernetes |

## Repository layout

```text
.
├── app/
│   ├── auth-service/          # Flask authentication API
│   ├── frontend/              # Express and EJS web application
│   └── roadmap-service/       # Spring Boot roadmap API
├── docker/
│   ├── compose.yaml            # Local multi-service environment
│   └── .env.example            # Local configuration template
├── terraform/
│   ├── modules/                # Network, EKS, Jenkins, and ECR modules
│   └── environments/dev/       # Development environment composition
├── ansible/
│   ├── inventory/              # Static or dynamic inventory configuration
│   ├── playbooks/              # Host configuration entry points
│   └── roles/                  # Reusable Jenkins host setup
├── jenkins/                    # Pipeline and shared-library integration
├── kubernetes/
│   ├── base/                   # Shared Kubernetes resources
│   └── overlays/dev/           # Development environment settings
├── .github/workflows/          # EKS deployment workflow
└── docs/                       # Architecture, setup, and project evidence
```

## Run locally with Docker Compose

### Prerequisites

- Docker Engine or Docker Desktop with Docker Compose v2.
- Git, with this repository cloned locally.

### Start the application

In PowerShell, create the local environment file:

```powershell
Copy-Item docker/.env.example docker/.env
```

Edit `docker/.env` and replace the example passwords and session secret with local values. The file is ignored by Git; do not commit it.

Start the services from the repository root:

Build the Spring Boot JAR in a temporary Maven container first. This avoids
running Maven as a Docker build step on machines where Docker Desktop's build
engine has an architecture or emulation issue:

```powershell
docker compose --profile build --env-file docker/.env -f docker/compose.yaml run --rm roadmap-builder
```

Then build and start the application containers:

```powershell
docker compose --env-file docker/.env -f docker/compose.yaml up --build --detach
docker compose --env-file docker/.env -f docker/compose.yaml ps
```

For local Compose, the roadmap service uses `app/roadmap-service/Dockerfile.local`
to package the JAR produced above. The regular multistage `Dockerfile` remains
available for CI builds.

Open [http://localhost:3000](http://localhost:3000), create a local account, and sign in to view the roadmap.

The screenshot below shows the roadmap page running locally after sign-in. The account email is hidden for privacy.

![Roadmap application running locally with Docker Compose](docs/images/docker-compose-roadmap.png)

*Figure: The application roadmap served by the local Docker Compose stack.*

To view service logs, run:

```powershell
docker compose --env-file docker/.env -f docker/compose.yaml logs --follow
```

Stop the containers while keeping the MySQL volume:

```powershell
docker compose --env-file docker/.env -f docker/compose.yaml down
```

### Local environment variables

| Variable | Used by | Purpose |
|---|---|---|
| `MYSQL_ROOT_PASSWORD` | MySQL | Local database administrator password |
| `DB_NAME` | MySQL, Auth service | Application database name; defaults to `ivolve` |
| `DB_USER` | MySQL, Auth service | Application database account |
| `DB_PASSWORD` | MySQL, Auth service | Application database password |
| `SESSION_SECRET` | Frontend | Signs the frontend session cookie |

The Compose file supplies service discovery addresses (`mysql`, `auth-service`, and `roadmap-service`) inside the Docker network. These are container names, not host addresses.

## Requirements progress

This table tracks the requirements checklist recorded in this README; the original assignment sheet is not stored in the repository. Argo CD was explicitly replaced with GitHub Actions by agreement; explain that substitution during the project review.

| Brief requirement | Status | Current implementation and remaining work |
|---|---|---|
| GitHub repository with README | Complete | The project repository and this README are in place. |
| Docker Compose for the application and database | Complete | `docker/compose.yaml` defines the local application stack and is committed. |
| Terraform Network, Server, EKS, and ECR modules | Implemented in code; pending backend migration and ACL apply | AWS VPC, subnets, routes, NAT, Jenkins EC2, EKS, and ECR resources are provisioned. Public/private Network ACLs and an encrypted/versioned S3 backend bootstrap are now in code. Apply the bootstrap, migrate the existing local state, then review and apply the complete ACL plan. |
| Ansible playbook, roles, and dynamic inventory for Jenkins | Complete and verified | `ansible/` contains the AWS EC2 dynamic inventory, Jenkins host playbook, and roles for Java 21, Jenkins LTS, Docker, and Trivy. The playbook was rerun successfully with `changed=0` and `failed=0`. |
| Kubernetes application and database resources | Complete and deployed | The `ivolve` overlay applies the app Deployments/Services, MySQL StatefulSet and headless Service, gp3 StorageClass/PVC, ConfigMap/Secret, and frontend Ingress. The Ingress provisions an internet-facing ALB. |
| Jenkins CI pipeline for each service and Shared Library | Implemented in the working tree; credential and run pending | All three previous builds passed on Jenkins EC2 through the connected Docker agent. The shared library now includes targeted local image cleanup and immutable image-tag updates to the service manifests, followed by a GitHub push. Add Jenkins credential `github-manifest-push` and rerun the pipelines to verify those new stages. |
| Argo CD continuous deployment | Replaced by GitHub Actions | The `Deploy Dev to EKS` workflow successfully applied the Kubernetes overlay and checked rollouts on the self-hosted runner. The workflow now also has a push trigger for service-manifest changes. AWS Organizations blocks GitHub OIDC provider creation, so the workflow uses a dedicated IAM deploy user in repository secrets. This is event-driven deployment, not Argo CD's continuous reconciliation. |
| Comprehensive documentation | In progress | Architecture, local setup, and stage guides are documented. Update final evidence after the newly added Jenkins manifest-push flow and Terraform S3 state migration/ACL deployment are completed. |

## Security practices

- Keep `docker/.env`, private SSH keys, AWS credentials, Terraform state, and real variable files out of Git.
- Prefer short-lived AWS access through OIDC. The current organization policy blocks provider creation, so the fallback uses a dedicated deploy-only IAM user in GitHub Actions secrets.
- Use Kubernetes Secrets for sensitive workload values and avoid placing real credentials in manifests.
- Limit the GitHub Actions IAM user to `eks:DescribeCluster` and namespace-scoped Kubernetes deployment access.

## Current deployment status

- The EKS cluster has two Ready worker nodes in private subnets, and the application workloads and MySQL PVC were observed healthy.
- The frontend, authentication, and roadmap pages were opened successfully through the ALB address. The roadmap content is static application data; it is not a user-editable list stored in MySQL.
- The AWS Load Balancer Controller deployment is healthy, and the `frontend` Ingress has an ALB address.
- The GitHub Actions deployment workflow completed successfully and reapplied the development manifests.
- Jenkins now runs on the Terraform-managed EC2 host, its Docker-based build agent is connected, and the three service pipelines passed before the manifest-push stage was added.
- Docker Desktop local runtime has experienced disk-space/daemon startup problems. The AWS deployment is separate from that local Docker issue.

## Remaining work

1. Add the repository-scoped Jenkins credential `github-manifest-push`; run all three pipelines and confirm each manifest push starts the GitHub Actions deployment.
2. Apply `terraform/bootstrap/state-backend/`, then migrate the dev environment's local Terraform state to S3 and confirm a clean plan.
3. Review and apply the public/private Network ACL changes, then confirm Jenkins access, ALB traffic, and EKS workloads remain healthy.
4. Capture final evidence and update this checklist with the verified outcomes.
