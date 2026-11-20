# Ansible Configuration

This is the single guide for everything under `ansible/`: dynamic inventory, variables, the Jenkins host playbook, reusable roles, setup commands, and verification. The control node is the Ubuntu Ansible host; the managed node is the Terraform-created Jenkins EC2 instance.

## What is in this folder

| Path | Role |
|---|---|
| `ansible.cfg` | Selects the project's dynamic inventory and Ansible defaults. |
| `requirements.yml` | Installs the `amazon.aws` collection used to discover EC2 instances. |
| `inventory/ivolve.aws_ec2.yml` | Finds the running Jenkins EC2 instance in `eu-north-1` by project/environment/name tags and groups it as `jenkins`. |
| `inventory/group_vars/jenkins.yml` | Sets SSH user, Python interpreter, SSH-key lookup, and repository variables for the discovered host. The key path comes from `ANSIBLE_PRIVATE_KEY_FILE`. |
| `playbooks/configure-jenkins.yml` | Checks the target and applies the configuration roles in order. |
| `roles/java/` | Installs OpenJDK 21 and fontconfig. |
| `roles/docker/` | Installs Docker Engine and Compose, enables Docker, and adds the Jenkins user to the Docker group. |
| `roles/trivy/` | Installs Trivy from Aqua Security's package repository. |
| `roles/jenkins/` | Installs Jenkins LTS, enables the service, and waits for its HTTP endpoint. |

## What the playbook configures

`playbooks/configure-jenkins.yml` applies reusable roles to install Java 21, Docker Engine with Compose, Trivy, and Jenkins LTS. Docker is enabled at boot and the Jenkins service account is added to the Docker group so Jenkins jobs can build images.

The Jenkins service on EC2 is the project's controller target. The Docker Desktop Jenkins container can remain available for local experimentation, but the project pipelines should be configured and demonstrated on the EC2 controller after Ansible setup and agent connection are complete.

The inventory is filtered to running instances in the configured region with `Project=ivolve-x`, `Environment=dev`, and `Name=ivolve-x-dev-jenkins`. Ansible also requires AWS credentials with `ec2:DescribeInstances`; SSH requires the management host's egress IP to be allowed by the Jenkins security group.

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

## Verify the configured host

From the `ansible/` directory on the control host:

```bash
ansible-inventory --graph
ansible jenkins -m ping
ansible jenkins -b -m command -a 'java -version'
ansible jenkins -b -m command -a 'docker version'
ansible jenkins -b -m command -a 'trivy --version'
ansible jenkins -b -m command -a 'systemctl is-active jenkins'
ansible-playbook playbooks/configure-jenkins.yml
```

Expected results: the inventory graph contains `jenkins`; ping returns `SUCCESS` and `pong`; Java reports major version 21; Docker and Trivy return versions; Jenkins reports `active`; and a repeated playbook run completes without failures. If the SSH connection times out, check the host's current public egress IP against the Jenkins security group and network ACL. If SSH returns `Permission denied (publickey)`, verify the key file path and permissions.

## Safety and secrets

- The inventory targets only running EC2 instances matching all three project tags and the Jenkins instance name.
- Do not commit private keys, AWS credentials, Terraform state, Ansible Vault passwords, or decrypted secret files.
- The playbook configures the Jenkins EC2 controller; it does not configure the optional local Docker Desktop Jenkins container.
