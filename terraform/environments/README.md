# Terraform Environments

Environment directories compose reusable Terraform modules with environment-specific inputs. The `dev/` environment is the first deployment target and currently composes the network module.

Future environments can reuse the same modules with different regions, CIDR ranges, and sizing. Add backend configuration and environment-specific values as those deployments are introduced. Do not commit Terraform state or secret variable files.
