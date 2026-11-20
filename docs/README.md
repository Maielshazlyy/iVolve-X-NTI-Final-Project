# Project Documentation and Portfolio Evidence

Start with the root [project README](../README.md), which explains the project goal, architecture, stage order, verification commands, and folder-by-folder README index. Each major implementation folder has its own `README.md` with the commands and expected result for that stage.

## Contents

- [`images/`](images/README.md) — architecture image, local app screenshots, and sanitized project evidence.
- [`SCREENSHOT_CHECKLIST.md`](SCREENSHOT_CHECKLIST.md) — optional screenshot names for a separate project evidence gallery.
- [`demo/`](demo/README.md) — finished screenshot-free GitHub and LinkedIn explainer videos, captions, covers, and regeneration commands.

The application, Terraform state backend/ACLs, Ansible Jenkins setup, all three Jenkins pipelines, GitHub Actions deployments, EKS workloads, and ALB app were reported working. The explainer videos use original graphics and stage descriptions rather than captured screens. Do not put credentials, tokens, private keys, real passwords, or unredacted AWS account IDs in public portfolio material.

The deployment implementation uses event-driven GitHub Actions because the AWS Organization SCP blocks creation of the GitHub OIDC provider. If the assignment rubric requires Argo CD specifically, GitHub Actions is not a continuous-reconciliation equivalent and the rubric gap should be handled explicitly.
