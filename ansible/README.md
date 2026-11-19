# Ansible Configuration

This directory contains the Ansible configuration for the Terraform-managed Jenkins EC2 controller required by the project brief. It uses the `amazon.aws.aws_ec2` inventory plugin to discover the running instance by its `Project`, `Environment`, and `Name` tags.

## What the playbook configures

`playbooks/configure-jenkins.yml` applies reusable roles to install Java 21, Docker Engine with Compose, Trivy, and Jenkins LTS. Docker is enabled at boot and the Jenkins service account is added to the Docker group so Jenkins jobs can build images.

The Jenkins service on EC2 is the project's controller target. The Docker Desktop Jenkins container can remain available for local experimentation, but the project pipelines should be configured and demonstrated on the EC2 controller after Ansible setup and agent connection are complete.

## Control host prerequisites

Run Ansible from an Ubuntu control host that can reach the Jenkins EC2 host over SSH and has AWS credentials for `ec2:DescribeInstances`. The control host also needs Ansible, Python boto3/botocore, and the `amazon.aws` collection:

```bash
sudo apt-get update
sudo apt-get install -y ansible-core python3-boto3
ansible-galaxy collection install -r ansible/requirements.yml
```

Clone or update this repository on that control host. Keep the SSH private key outside the repository and set its path only in the current shell:

```bash
export ANSIBLE_PRIVATE_KEY_FILE="$HOME/.ssh/lab28-ansible.pem"
chmod 600 "$ANSIBLE_PRIVATE_KEY_FILE"
```

## Discover and configure the EC2 host

From the repository root on the control host:

```bash
cd ansible
ansible-inventory --graph
ansible jenkins -m ping
ansible-playbook playbooks/configure-jenkins.yml --syntax-check
ansible-playbook playbooks/configure-jenkins.yml --ask-become-pass
```

If the Ubuntu control host uses an EC2 instance profile with passwordless sudo, omit `--ask-become-pass`. The inventory uses the Jenkins instance's public IP, so the control host must have network access to that IP and the Jenkins security group must allow SSH from the control host's egress address.

## Safety and secrets

- The inventory targets only running EC2 instances matching all three project tags and the Jenkins instance name.
- Do not commit private keys, AWS credentials, Terraform state, Ansible Vault passwords, or decrypted secret files.
- The playbook configures the Jenkins EC2 controller; it does not configure the optional local Docker Desktop Jenkins container.
