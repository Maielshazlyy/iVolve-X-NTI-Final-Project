# Shared Library Steps (`vars/`)

Jenkins exposes each Groovy file here as a global pipeline step:

| Step | Purpose |
|---|---|
| `serviceCiPipeline(Map)` | Orchestrates stages and common pipeline options for one service. |
| `buildAndScanImage(Map)` | Builds the Docker image and runs Trivy. The current scan records findings but does not fail the pipeline on severity. |
| `pushImageToEcr(Map)` | Logs in with the AWS CLI, tags the image for the configured ECR repository, and pushes it. |
| `updateKubernetesManifest(Map)` | Replaces the image reference in the selected manifest, validates the Git diff, commits, and pushes to `main`. |

The required configuration fields are validated by each step. CI credentials are `aws-ecr-push` and `github-manifest-push`; add/change them in Jenkins' credential store, never in Groovy files. Build behavior and per-service mappings are described in [`../../pipelines/README.md`](../../pipelines/README.md).
