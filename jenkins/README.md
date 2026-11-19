# Jenkins CI

Jenkins runs on the Terraform-managed EC2 controller. The `ivolve-build-agent` is a Docker container on the developer workstation and connects to that controller over WebSocket. The agent builds and scans images with Docker and Trivy, publishes them to ECR, updates its service manifest with the immutable build tag, and pushes the manifest change to GitHub. A GitHub Actions workflow deploys the changed manifest to EKS.

## Jobs and shared library

Create three Jenkins Pipeline jobs using **Pipeline script from SCM**, the repository's `main` branch, and these script paths:

| Job | Script path |
|---|---|
| `ivolve-auth-service` | `jenkins/pipelines/auth-service.Jenkinsfile` |
| `ivolve-roadmap-service` | `jenkins/pipelines/roadmap-service.Jenkinsfile` |
| `ivolve-frontend` | `jenkins/pipelines/frontend.Jenkinsfile` |

Configure the global trusted shared library:

- **Name:** `ivolve-shared`
- **Default version:** `main`
- **SCM:** Git, this repository's clone URL
- **Library path:** `jenkins/shared-library`

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

The `Deploy Dev to EKS` GitHub Actions workflow runs manually or when one of the three service manifests changes on `main`. It applies the Kubernetes overlay, updates the application Secret, and waits for MySQL and application rollouts. The workflow runs on the self-hosted GitHub runner on the Jenkins EC2 host, which can reach the private EKS API endpoint.

## Local controller note

The old Docker Desktop Jenkins controller is retained only as a rollback source during migration. The required project controller is Jenkins on EC2, configured by Ansible. Do not start both controllers against the same Jenkins home volume.
