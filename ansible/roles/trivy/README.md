# Trivy Role

Configures Aqua Security's package repository and installs Trivy on the Jenkins EC2 host. The Docker build agent also has Trivy installed in its image so the pipeline can scan images next to the Docker daemon it uses.

Run the playbook from `ansible/`:

```bash
ansible-playbook playbooks/configure-jenkins.yml --syntax-check
ansible-playbook playbooks/configure-jenkins.yml --ask-become-pass
```

Verify with `trivy --version` on the managed host. In Jenkins, the `Build and scan` stage runs `trivy image`; findings are reported but the current baseline configuration uses `--exit-code 0`, so findings do not fail builds yet. Review findings before enabling a severity gate.
