# Architecture, Evidence, and Demo

This guide covers documentation artifacts in `docs/`: the branded architecture image, user-provided evidence captures, and project walkthrough videos. The architecture and video source scripts reflect the current delivery model: GitHub Actions handles CI, and Argo CD handles CD. Jenkins and the Jenkins-specific Ansible host configuration were removed from the project.

## Architecture diagram

![iVolve architecture with GitHub Actions CI and Argo CD CD](images/ivolve-platform-architecture.png)

- Editable vector diagram: [`images/ivolve-platform-architecture.svg`](images/ivolve-platform-architecture.svg).
- PNG used by the repository README and presentations: [`images/ivolve-platform-architecture.png`](images/ivolve-platform-architecture.png).
- Pillow source: [`images/render_architecture.py`](images/render_architecture.py). From the repository root, regenerate the PNG with `python docs/images/render_architecture.py`.

The diagram shows GitHub Actions building and scanning images, publishing to ECR, committing new immutable image references, and Argo CD syncing Git manifests to EKS. Terraform provisions the AWS network, EKS, ECR, IAM, and S3 state. EKS runs the frontend, APIs, and persistent MySQL database; the AWS Load Balancer Controller exposes the frontend through an ALB.

## Demo videos

The silent video set is designed for GitHub/portfolio and LinkedIn. It uses the iVolve and NTI branding plus technology and AWS logos, with animated process graphics. Captions are available as separate sidecar files; clean versions have no transcript panels or captions.

| Use | Video | Cover | Captions |
|---|---|---|---|
| GitHub / portfolio | [`demo/ivolve-devops-explainer.mp4`](demo/ivolve-devops-explainer.mp4) | [`demo/ivolve-devops-explainer-cover.png`](demo/ivolve-devops-explainer-cover.png) | [`demo/ivolve-devops-explainer.srt`](demo/ivolve-devops-explainer.srt) |
| LinkedIn | [`demo/ivolve-devops-linkedin.mp4`](demo/ivolve-devops-linkedin.mp4) | [`demo/ivolve-devops-linkedin-cover.png`](demo/ivolve-devops-linkedin-cover.png) | [`demo/ivolve-devops-linkedin.srt`](demo/ivolve-devops-linkedin.srt) |
| GitHub / portfolio, clean | [`demo/ivolve-devops-explainer-no-captions.mp4`](demo/ivolve-devops-explainer-no-captions.mp4) | [`demo/ivolve-devops-explainer-no-captions-cover.png`](demo/ivolve-devops-explainer-no-captions-cover.png) | None |
| LinkedIn, clean | [`demo/ivolve-devops-linkedin-no-captions.mp4`](demo/ivolve-devops-linkedin-no-captions.mp4) | [`demo/ivolve-devops-linkedin-no-captions-cover.png`](demo/ivolve-devops-linkedin-no-captions-cover.png) | None |

The videos explain the application and Docker Compose, Terraform, GitHub Actions CI, Trivy, ECR, Argo CD CD, EKS workloads, persistent MySQL storage, and the public ALB.

## Evidence screenshots

These captures document the local stack, the CI/CD handoff, and the running EKS application. Older Jenkins and direct GitHub Actions-to-EKS deployment screenshots are intentionally omitted because that architecture has been replaced by GitHub Actions CI plus Argo CD CD.

<details>
<summary>Docker Compose started the local services</summary>

![Docker Compose build and local services](images/evidence/docker-compose-started.png)

</details>

<details>
<summary>GitHub Actions built, scanned, and published service images</summary>

![Successful GitHub Actions CI run showing image build, Trivy scans, ECR publishing, and manifest update](images/evidence/github-actions-ci-success.png)

</details>

<details>
<summary>Argo CD synced the Git revision and reported the application healthy</summary>

![Argo CD application showing Healthy, Synced, and a successful sync](images/evidence/argocd-healthy-synced.png)

</details>

<details>
<summary>EKS nodes, workloads, persistent storage, and Ingress</summary>

![EKS verification showing ready nodes, services, MySQL persistence, and ALB Ingress](images/evidence/eks-workloads-healthy.png)

</details>

<details>
<summary>Application served through the AWS ALB</summary>

![IVOLVE roadmap application served through the ALB](images/evidence/application-live-on-alb.png)

</details>

## Regenerate the assets and videos

From the repository root on Windows, use Python with Pillow and FFmpeg built with `libx264`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File docs/demo/render_simple_icons.ps1
python docs/images/render_architecture.py
python docs/demo/generate_explainer.py --ffmpeg "C:\tools\ffmpeg\bin\ffmpeg.exe"
python docs/demo/generate_explainer.py --ffmpeg "C:\tools\ffmpeg\bin\ffmpeg.exe" --no-captions
```

The generator writes the widescreen and vertical silent videos, cover images, and separate `.srt` captions. Its content is sourced from [`demo/generate_explainer.py`](demo/generate_explainer.py). Logo license information is in [`demo/assets/SIMPLE-ICONS-LICENSE.md`](demo/assets/SIMPLE-ICONS-LICENSE.md).
