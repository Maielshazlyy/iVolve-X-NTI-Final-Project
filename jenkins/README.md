# Jenkins Continuous Integration

This folder contains the Jenkins controller setup, the build agent definition, the pipeline, and the reusable Shared Library used by the project.

## CI flow

1. Each Jenkins job checks out this repository and runs the service-specific Jenkinsfile on the `ivolve-build` agent.
2. The selected service's Docker image is built and scanned with Trivy.
3. Jenkins authenticates to Amazon ECR and pushes that service image with the Jenkins build number as its tag.

There are three jobs, one per independently buildable service: `auth-service`, `roadmap-service`, and `frontend`. Each small Jenkinsfile passes its service name and build context to the same `serviceCiPipeline` Shared Library function. The image build, scan, and ECR push logic is therefore reused without coupling all three services to one build.

The pipeline does not deploy to Kubernetes. The chosen deployment design assigns that work to GitHub Actions; the Kubernetes manifests and deployment workflow are separate project work.

## Jenkins controller

The controller Compose file is at the repository root. It exposes Jenkins only on localhost and persists Jenkins home in a named Docker volume:

```powershell
docker compose -f jenkins/compose.yaml up -d
```

Install these Jenkins plugins from **Manage Jenkins → Plugins**:

- Pipeline
- Git
- Credentials Binding
- Pipeline: Shared Groovy Libraries

The inbound agent is defined in `agent.Dockerfile` and `agent.compose.yaml`. It includes Docker CLI, AWS CLI, and Trivy, and mounts the Docker Desktop engine socket for image builds. Keep the controller and agent running on the same Docker Desktop host so the agent can reach the controller at `host.docker.internal:8080`.

To use the agent definition, create `jenkins/.env` locally (it is ignored by Git) with the secret shown on the Jenkins node page:

```dotenv
JENKINS_SECRET=paste-the-node-secret-here
```

Then start or rebuild the agent:

```powershell
docker compose --env-file jenkins/.env -f jenkins/agent.compose.yaml up -d --build
```

The Jenkins node must be named `ivolve-build-agent`, have label `ivolve-build`, use one executor, and use inbound/WebSocket launch. The agent image gets broad access to the local Docker engine through its socket; only run trusted pipeline code on this agent.

## Configure the Shared Library

In Jenkins, open **Manage Jenkins → System → Global Trusted Pipeline Libraries → Add** and enter:

- **Name:** `ivolve-shared` (must match the `@Library` line in the Jenkinsfile)
- **Default version:** `main`
- **Retrieval method:** Modern SCM → Git
- **Project Repository:** this repository's clone URL
- **Library Path:** `jenkins/shared-library`

The library path points Jenkins to the `vars/` folder nested under this project directory. Keep the name and path in sync with the Jenkinsfiles and repository layout.

## Configure Amazon ECR credentials

The current agent is on Docker Desktop, so it does not automatically receive the IAM instance profile attached to the separate EC2 Jenkins host. In Jenkins, add a **Username with password** credential:

- **Username:** AWS access key ID for a dedicated least-privilege IAM identity
- **Password:** that identity's AWS secret access key
- **ID:** `aws-ecr-push`

The identity needs permission to obtain an ECR login token and upload image layers/manifests to the three repositories under `ivolve-x/dev/` in `eu-north-1`. Do not put AWS keys in this repository, the Jenkinsfile, or the agent Compose file. For a durable setup, prefer an EC2-based agent with an IAM instance profile or another short-lived AWS credential flow over long-lived access keys.

## Create the Pipeline job

Create three Jenkins **Pipeline** jobs and configure each as **Pipeline script from SCM**. Use the same repository and branch for all three, and set each Script Path as follows:

| Job name | Script Path |
|---|---|
| `ivolve-auth-service` | `jenkins/pipelines/auth-service.Jenkinsfile` |
| `ivolve-roadmap-service` | `jenkins/pipelines/roadmap-service.Jenkinsfile` |
| `ivolve-frontend` | `jenkins/pipelines/frontend.Jenkinsfile` |

For each job, set **SCM** to Git, **Repository URL** to this repository's clone URL, and **Branch** to `*/main`.

Save and run the job. The build needs the `ivolve-build` label, the configured Shared Library, the Docker socket, and the `aws-ecr-push` Jenkins credential.

## Files

```text
jenkins/
├── pipelines/                  # One small Jenkinsfile per service/job
│   ├── auth-service.Jenkinsfile
│   ├── frontend.Jenkinsfile
│   └── roadmap-service.Jenkinsfile
├── agent.Dockerfile            # Agent tools: Docker CLI, AWS CLI, Trivy
├── agent.compose.yaml          # Separate agent service; requires local secret
└── shared-library/
    └── vars/
        ├── buildAndScanImage.groovy
        ├── pushImageToEcr.groovy
        └── serviceCiPipeline.groovy
```
