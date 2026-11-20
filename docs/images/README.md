# Architecture and Project Screenshots

This folder contains the project architecture asset and screenshots used as evidence in documentation and the demo.

| File | Purpose |
|---|---|
| `ivolve-platform-architecture.svg` | Full source-to-production architecture diagram; created from the current repository/deployment design. |
| `ivolve-platform-architecture.png` | High-resolution raster version for presentations and social media. Rebuild with `python docs/images/render_architecture.py` from the repository root (requires Pillow). |
| `render_architecture.py` | Local Pillow-based renderer that exports the architecture diagram as PNG. |
| `evidence/` | Optional user-provided screenshots for a separate evidence gallery. Screenshots are not used in the demo videos. |
| `docker-compose-roadmap.png` | Existing local Docker Compose app view. |
| `compose-roadmap.png` | Existing Compose app evidence image. |
| `evidence/` | Destination for the final sanitized AWS/Jenkins/GitHub/EKS/application captures. See [`../SCREENSHOT_CHECKLIST.md`](../SCREENSHOT_CHECKLIST.md). |

Review images at full size before publishing. Remove or blur personal emails, access tokens, secret values, private keys, AWS account IDs, and unrelated console information.
