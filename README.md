# IVOLVE X NTI Final Project

An end-to-end cloud and DevOps project built around the IVOLVE application.

## Planned workflow

Docker Compose will run the application and its database locally. Terraform will provision the AWS infrastructure, Ansible will configure the Jenkins server, and Kubernetes will host the application. Jenkins will build, scan, and publish container images. GitHub Actions will deploy the updated manifests to Amazon EKS.

> Deployment uses GitHub Actions in this project, replacing the Argo CD deployment step shown in the original project brief.

## Repository structure

- `app/` — instructor-provided application source, organized by service
- `docker/` — Dockerfiles and local Docker Compose configuration
- `terraform/` — reusable AWS infrastructure modules and environment configuration
- `ansible/` — inventories, playbooks, and configuration roles
- `jenkins/` — Jenkins pipeline and shared library configuration
- `kubernetes/` — Kubernetes manifests and environment overlays
- `.github/workflows/` — GitHub Actions workflows
- `docs/` — architecture, setup, and operating guides

Project implementation is in progress. Sections will be filled in and documented incrementally.

## Local application run

Create a local environment file from the example, then start the services:

```bash
cp docker/.env.example docker/.env
docker compose --env-file docker/.env -f docker/compose.yaml up --build
```

Open <http://localhost:3000> to use the application. See [`app/README.md`](app/README.md) for the confirmed service layout and source attribution.
