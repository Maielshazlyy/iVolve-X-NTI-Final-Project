# Jenkins Service Pipelines

Each file is a small Declarative Pipeline entry point that passes a service name, Docker build context, and Kubernetes manifest path to `serviceCiPipeline` in the [`ivolve-shared` library](../shared-library/README.md).

| Jenkins job | File | Build context | Manifest updated |
|---|---|---|---|
| `ivolve-frontend` | `frontend.Jenkinsfile` | `app/frontend` | `kubernetes/base/frontend.yaml` |
| `ivolve-auth-service` | `auth-service.Jenkinsfile` | `app/auth-service` | `kubernetes/base/auth-service.yaml` |
| `ivolve-roadmap-service` | `roadmap-service.Jenkinsfile` | `app/roadmap-service` | `kubernetes/base/roadmap-service.yaml` |

## Jenkins job configuration

Create each as **Pipeline script from SCM**, point SCM at this GitHub repository and branch `main`, and use the matching script path above. Configure the trusted global library named `ivolve-shared`, default version `main`, path `jenkins/shared-library`.

## Expected pipeline sequence

1. Declarative checkout of the repository.
2. Build the selected service container and run Trivy image scanning.
3. Authenticate to ECR with Jenkins credential `aws-ecr-push`, then publish the image.
4. Change only that service's manifest to the published build image tag and push the Git commit with `github-manifest-push`.
5. Remove the local image references in the post action.

The proof is a successful Stage View and a successful GitHub Actions deployment run triggered by that manifest commit. Do not screenshot or paste credential contents.
