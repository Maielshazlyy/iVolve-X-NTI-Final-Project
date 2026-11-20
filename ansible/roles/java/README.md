# Java Role

Installs OpenJDK 21 and `fontconfig` on the Ubuntu Jenkins EC2 host, as required by Jenkins LTS. The role is called by `playbooks/configure-jenkins.yml` and needs SSH access plus privilege escalation.

From the `ansible/` directory on the Ubuntu control host, run:

```bash
ansible jenkins -m ping
ansible-playbook playbooks/configure-jenkins.yml --syntax-check
ansible-playbook playbooks/configure-jenkins.yml --ask-become-pass
```

Verify on the Jenkins host with `java -version`; expected major version is 21. The full play recap should show `failed=0`.
