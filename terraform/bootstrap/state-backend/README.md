# Terraform State Backend Bootstrap

This separate bootstrap root creates the S3 bucket used for the dev environment's Terraform state. It intentionally keeps its own Terraform state local because a backend cannot create itself. The bucket is account/region-specific, versioned, encrypted with SSE-S3, blocked from public access, and rejects non-TLS requests. It uses Terraform's native S3 lock file, so Terraform 1.10 or newer is required.

From this directory, initialize and review the bootstrap before applying:

```powershell
terraform init
terraform plan
terraform apply
terraform output -raw state_bucket_name
```

Then, from the repository root, create the local ignored backend config and set its bucket to the output above if it differs from the example:

```powershell
Copy-Item terraform/environments/dev/backend.hcl.example terraform/environments/dev/backend.hcl
```

From `terraform/environments/dev`, migrate the existing local state:

```powershell
terraform init -migrate-state -backend-config=backend.hcl
```

Confirm the state migration when Terraform prompts. Keep the local `terraform.tfstate` recovery copy until `terraform state list` works against the S3 backend and a fresh plan shows no unintended replacement or deletion. Do not commit `.tfstate`, backend metadata, or credentials. The bucket contains sensitive infrastructure state; only grant access to authorized Terraform operators. S3 incurs usage-based storage and request charges.
