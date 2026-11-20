# Jenkins Inventory Variables

`jenkins.yml` supplies the SSH user, Python interpreter, key lookup, and repository URLs used by the dynamic Jenkins EC2 inventory and roles. The SSH key path is read from `ANSIBLE_PRIVATE_KEY_FILE` in the current Ansible control-host shell; private key bytes are never stored here.

From the Ubuntu control host, set the key variable and inspect the discovered host:

```bash
export ANSIBLE_PRIVATE_KEY_FILE="$HOME/.ssh/lab28-ansible.pem"
chmod 600 "$ANSIBLE_PRIVATE_KEY_FILE"
cd ~/iVolve-X-NTI-Final-Project/ansible
ansible-inventory --graph
ansible jenkins -m ping
```

Expected ping result is `SUCCESS` with `"ping": "pong"`. Keep credentials and machine-specific private key files outside the repository.
