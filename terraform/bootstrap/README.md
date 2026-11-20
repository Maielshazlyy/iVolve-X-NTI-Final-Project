# Terraform Bootstrap Roots

Bootstrap roots create Terraform support resources that cannot be created by the backend they are bootstrapping. This project currently has one root, [`state-backend/`](state-backend/README.md), which creates the encrypted/versioned S3 bucket for the dev environment state.

From `state-backend/`, run `terraform init`, inspect `terraform plan`, and apply the bucket. The bootstrap root keeps its own state locally; the dev infrastructure state is migrated to S3 afterwards. Follow the child README for the exact bucket name, migration command, verification, and recovery precautions.
