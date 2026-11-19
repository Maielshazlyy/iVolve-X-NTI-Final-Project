# Ansible Roles

The playbook uses four reusable roles:

- `java` installs OpenJDK 21 and fontconfig for the Jenkins LTS service.
- `docker` configures Docker's official Ubuntu apt repository, installs Docker Engine and Compose, enables the daemon, and adds the Jenkins service account to the Docker group.
- `trivy` configures Aqua Security's official apt repository and installs Trivy.
- `jenkins` configures the Jenkins LTS apt repository, installs Jenkins, starts it at boot, and waits for its local HTTP login endpoint.

The Docker role restarts Jenkins after changing group membership so the service receives its updated group list. Roles contain no project credentials or private keys.
