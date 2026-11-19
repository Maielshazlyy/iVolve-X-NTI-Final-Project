# Jenkins Infrastructure Module

Creates an Ubuntu 24.04 EC2 controller host in a public subnet and attaches a dedicated EC2 instance profile. The IAM role can authenticate to ECR and push images only to the repositories passed into the module.

## Access and host settings

- The default instance size is `t3.small`; use a dedicated agent for image builds so the controller stays lightweight.
- SSH (port 22) and the Jenkins UI (port 8080) are restricted to the configured administrator CIDRs. Use your current public IPv4 with `/32`; include the Ansible control host's public egress IP only if Ansible will connect from that host.
- The host uses an existing EC2 key pair in the selected Region. The private key stays outside the repository.
- The root EBS volume is encrypted gp3 storage and IMDSv2 is required.
- The host receives only the ECR image-push permissions required by this project's repositories. `ecr:GetAuthorizationToken` must use `Resource: "*"`; repository upload actions are scoped to the supplied repository ARNs.

Terraform creates the host but does not install Jenkins. Ansible will configure the operating system and Jenkins in the next stage. An EC2 instance, EBS storage, and public IPv4 can incur ongoing charges; review the plan before applying.
