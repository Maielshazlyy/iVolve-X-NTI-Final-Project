# Docker Role

Installs Docker Engine and the Compose plugin from Docker's official Ubuntu repository, enables the daemon, and adds the `jenkins` service account to the Docker group. It restarts Jenkins after group membership changes so the controller process receives the new group.

Run the parent playbook from `ansible/` on the Ubuntu control host:

```bash
ansible-playbook playbooks/configure-jenkins.yml --syntax-check
ansible-playbook playbooks/configure-jenkins.yml --ask-become-pass
```

Verify on the managed host with `sudo systemctl is-active docker` and `sudo -u jenkins docker version`. The daemon should be active and Docker should return client/server details. The Jenkins EC2 host's IAM role supplies scoped ECR permissions; do not store AWS keys on the host.
