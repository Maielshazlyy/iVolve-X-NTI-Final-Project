# Jenkins Continuous Integration

Jenkins will provide the CI stage for the application: checkout source, run checks, build container images, scan them with Trivy, publish approved images to Amazon ECR, and update image references in the deployment repository.

## Planned design

- Run the pipeline on a dedicated Jenkins agent.
- Reuse pipeline actions through the Groovy Shared Library in this repository.
- Store registry and Git credentials in Jenkins Credentials, not in source files.
- Keep CI responsible for building and publishing images; GitHub Actions will handle deployment in this project.

## Current status

This directory contains only a placeholder. The pipeline and shared-library implementation will be added after the infrastructure and host configuration stages are ready.
