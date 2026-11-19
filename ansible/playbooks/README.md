# Ansible Playbooks

`configure-jenkins.yml` targets the `jenkins` group from the dynamic EC2 inventory and calls the `java`, `docker`, `trivy`, and `jenkins` roles. It checks that the discovered host runs Ubuntu and that the SSH key path is supplied through `ANSIBLE_PRIVATE_KEY_FILE`.

Run `ansible-playbook playbooks/configure-jenkins.yml --syntax-check` before applying it. Apply from the repository's `ansible/` directory with `ansible-playbook playbooks/configure-jenkins.yml --ask-become-pass` when the control host needs a sudo password.
