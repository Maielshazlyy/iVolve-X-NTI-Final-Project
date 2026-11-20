# GitHub Repository Automation

This directory contains GitHub-specific automation. The exact workflow behavior, required repository secrets, triggers, and verification steps are documented in [`workflows/README.md`](workflows/README.md).

## Quick workflow checks

1. Open the repository's **Actions** tab.
2. Confirm **Deploy Dev to EKS** has a successful run after a Jenkins manifest commit.
3. Open the run and check that the secret creation, manifest apply, MySQL wait, three deployment rollouts, and resource summary steps completed.
4. Confirm the corresponding EKS rollout with the commands in [`../kubernetes/README.md`](../kubernetes/README.md).

Workflow files should never print secret values. Credentials are configured as repository Actions secrets, not in YAML.
