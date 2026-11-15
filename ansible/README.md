# Ansible Configuration

Ansible will configure the Jenkins host after Terraform provisions it. The planned setup uses an inventory to select hosts, playbooks as execution entry points, and roles to organize reusable configuration tasks.

## Current status

Only the directory structure exists; inventories, playbooks, and roles are placeholders. This section does not configure any hosts yet.

Keep private SSH keys, vault passwords, real inventories, and decrypted secret files outside Git. Commit only sanitized examples and Ansible Vault-encrypted variables.

See the subdirectory READMEs for each component's planned responsibility.
