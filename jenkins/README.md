# Jenkins CI

Jenkins runs on the Terraform-managed EC2 controller. The `ivolve-build-agent` is a Docker container on the developer workstation and connects to that controller over WebSocket. The agent builds and scans images with Docker and Trivy, publishes them to ECR, updates its service manifest with the immutable build tag, and pushes the manifest change to GitHub. A GitHub Actions workflow deploys the changed manifest to EKS.

## Jobs and shared library

Create three Jenkins Pipeline jobs using **Pipeline script from SCM**, the repository's `main` branch, and these script paths:

| Job | Script path |
|---|---|
| `ivolve-auth-service` | `jenkins/pipelines/auth-service.Jenkinsfile` |
| `ivolve-roadmap-service` | `jenkins/pipelines/roadmap-service.Jenkinsfile` |
| `ivolve-frontend` | `jenkins/pipelines/frontend.Jenkinsfile` |

Each small Jenkinsfile selects a build context and target manifest, then calls the shared `serviceCiPipeline` step. The service mappings are:

| Service | Build context | Manifest updated |
|---|---|---|
| Frontend | `app/frontend` | `kubernetes/base/frontend.yaml` |
| Auth API | `app/auth-service` | `kubernetes/base/auth-service.yaml` |
| Roadmap API | `app/roadmap-service` | `kubernetes/base/roadmap-service.yaml` |

Configure the global trusted shared library:

- **Name:** `ivolve-shared`
- **Default version:** `main`
- **SCM:** Git, this repository's clone URL
- **Library path:** `jenkins/shared-library`

The library's callable Groovy steps live in `jenkins/shared-library/vars/`:

| Step | Responsibility |
|---|---|
| `serviceCiPipeline(Map)` | Validates one service's configuration and sequences the CI stages. |
| `buildAndScanImage(Map)` | Builds the service image and runs Trivy. Findings are reported; the current baseline does not fail the build on severity. |
| `pushImageToEcr(Map)` | Authenticates to ECR, tags the image, and publishes it. |
| `updateKubernetesManifest(Map)` | Updates the service manifest to the immutable build tag, checks the Git diff, then commits and pushes to `main`. |

The agent node must be named `ivolve-build-agent`, use the `ivolve-build` label, one executor, inbound launch, and WebSocket transport.

## Jenkins credentials

Add these Jenkins credentials before running the full CI-to-deploy pipeline:

| Credential ID | Kind | Contents |
|---|---|---|
| `aws-ecr-push` | Username with password | Dedicated AWS access key ID and secret access key with ECR push permissions for the three project repositories. |
| `github-manifest-push` | Username with password | GitHub username and a fine-grained token limited to this repository with Contents read/write permission. Jenkins uses it only for the manifest commit. |

Do not put either credential in Git, a Jenkinsfile, or the agent Compose file. Prefer short-lived AWS credentials when available. The GitHub token is only for Jenkins' manifest push. Separately, the organization SCP blocks GitHub OIDC for AWS deployment, so GitHub Actions currently uses the dedicated deploy IAM user's access keys stored as repository secrets.

## Start the Docker build agent

Copy `.env.example` to `.env`, then set `JENKINS_URL` to the EC2 controller URL and `JENKINS_SECRET` to the secret shown on the node page. The `.env` file is ignored by Git.

```powershell
Copy-Item jenkins/.env.example jenkins/.env
# Edit jenkins/.env locally; do not paste the secret into chat or commit it.
docker compose --env-file jenkins/.env -f jenkins/agent.compose.yaml up -d --build
```

The agent mounts the Docker Desktop socket to build images. Only run trusted project pipelines on this agent. For a stable team setup, move the agent to a dedicated EC2 host and use an instance profile for ECR access.

## CI and deployment behavior

Each service pipeline builds and scans its image, pushes both the immutable Jenkins build-number tag and `latest` to ECR, updates only that service's Kubernetes manifest to the immutable tag, commits and pushes the manifest, and removes the local image references in the `post` cleanup.

Expected stage order is checkout → build and scan → publish to ECR → update/push the Kubernetes manifest → cleanup. A successful Jenkins Stage View confirms the service build; the matching GitHub Actions run confirms the manifest was deployed.

Check the local Docker build agent from PowerShell:

```powershell
docker ps --filter name=ivolve-build-agent
docker logs --tail 30 ivolve-build-agent
docker exec ivolve-build-agent docker --version
docker exec ivolve-build-agent trivy --version
docker exec ivolve-build-agent aws --version
```

The agent should be `Up` and its logs should include `WebSocket connection open` and `Connected`. To stop/start the Compose-managed agent from the repository root:

```powershell
docker compose --env-file jenkins/.env -f jenkins/agent.compose.yaml stop
docker compose --env-file jenkins/.env -f jenkins/agent.compose.yaml up -d
```

The `Deploy Dev to EKS` GitHub Actions workflow runs manually or when one of the three service manifests changes on `main`. It applies the Kubernetes overlay, updates the application Secret, and waits for MySQL and application rollouts. The workflow runs on the self-hosted GitHub runner on the Jenkins EC2 host, which can reach the private EKS API endpoint.

## Local controller note

The old Docker Desktop Jenkins controller is retained only as a rollback source during migration. The required project controller is Jenkins on EC2, configured by Ansible. Do not start both controllers against the same Jenkins home volume.
