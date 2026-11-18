FROM jenkins/inbound-agent:jdk21

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg docker.io awscli \
    && install -m 0755 -d /usr/share/keyrings \
    && curl -fsSL https://aquasecurity.github.io/trivy-repo/deb/public.key \
       | gpg --dearmor -o /usr/share/keyrings/trivy.gpg \
    && chmod 0644 /usr/share/keyrings/trivy.gpg \
    && echo 'deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main' \
       > /etc/apt/sources.list.d/trivy.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends trivy \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
