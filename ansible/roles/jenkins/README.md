# Jenkins Role

Configures the Jenkins LTS package repository, installs Jenkins, enables the systemd service at boot, and waits for the local Jenkins HTTP endpoint. Java 21 is installed by the separate `java` role first. The role does not configure UI jobs or copy Jenkins credentials; those remain controller configuration.

From the Ubuntu control host, in the repository's `ansible/` directory:

```bash
ansible jenkins -m ping
ansible-playbook playbooks/configure-jenkins.yml --syntax-check
ansible-playbook playbooks/configure-jenkins.yml --ask-become-pass
```

Verify with `sudo systemctl is-active jenkins` and open `http://<jenkins-public-dns>:8080` from an allowed administrator network. Jenkins UI/SSH access is restricted by Terraform security group and public-subnet NACL CIDRs.
