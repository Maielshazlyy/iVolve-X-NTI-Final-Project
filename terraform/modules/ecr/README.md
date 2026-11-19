# ECR Module

Creates private Amazon ECR repositories for the application containers.

## Repository settings

- Repository names include project and environment, for example `ivolve-x/dev/auth-service`.
- Image scanning on push is enabled.
- Images are encrypted with AES-256 using ECR-managed encryption.
- Tags are immutable so a published tag cannot silently point to different image contents. Use a unique commit SHA or build tag for each image.
- Untagged images expire after seven days to limit unused image storage.

The development environment creates repositories for `auth-service`, `roadmap-service`, and `frontend`. EKS worker nodes already have the ECR pull policy attached; publishing permissions for GitHub Actions will be configured in the CI stage.
