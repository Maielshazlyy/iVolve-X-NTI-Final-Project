# GitHub Automation

GitHub Actions workflows live in [`workflows/`](workflows/). In this project, Actions is intended to deploy Kubernetes manifests to Amazon EKS after CI updates the desired image reference in Git.

Configure AWS authentication with GitHub OIDC and a narrowly scoped IAM role. Do not put long-lived AWS access keys or cluster credentials in workflow files.
