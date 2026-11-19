# Project Documentation

This directory holds project documentation and visual evidence. The detailed setup currently lives in the root [project README](../README.md) and in the README files inside each implementation section.

The `images/` directory contains sanitized screenshots embedded in the section where they are relevant. The local Docker Compose screenshots are `images/docker-compose-roadmap.png` and `images/compose-roadmap.png`.

Stage-specific setup guides are in each implementation folder. The final project uses GitHub Actions for deployment because the AWS Organizations policy blocks GitHub OIDC provider creation. Capture sanitized screenshots for the EC2 Jenkins controller, successful service pipelines, EKS workloads, and the ALB-served application before final submission.
