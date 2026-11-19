# Ansible Inventory

`ivolve.aws_ec2.yml` is the dynamic inventory source. It discovers only running EC2 instances in `eu-north-1` tagged with `Project=ivolve-x`, `Environment=dev`, and `Name=ivolve-x-dev-jenkins`, then assigns the host to the `jenkins` group.

The inventory plugin needs AWS credentials and the `amazon.aws` collection on the Ansible control host. SSH uses the `ANSIBLE_PRIVATE_KEY_FILE` environment variable; no private key path or key material is stored in this repository.
