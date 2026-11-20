# Demo video brand assets

These assets give the explainer a recognizable visual identity for the application and the tools used in the project.

## Sources

- `logos/*.svg` — Simple Icons brand marks for GitHub, Docker, Terraform, Ansible, Jenkins, Trivy, Kubernetes, MySQL, Spring Boot, Node.js, Python, and Flask. The icon paths are distributed under CC0 1.0; the copy of the license is [`SIMPLE-ICONS-LICENSE.md`](SIMPLE-ICONS-LICENSE.md). Brand names and marks remain the property of their owners.
- `logos/aws/*.png` — AWS service icons for EC2, ECR, S3, EBS, and Elastic Load Balancing, taken from the official [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) package dated July 31, 2026. The videos use these as diagram elements.
- The iVolve and NTI marks are used from the project frontend at `app/frontend/public/images/ivolve-logo.png` and `nti-logo.png`.
- `logos/rasterized/*.png` — colored renderings of the Simple Icons SVG paths used by the video generator. Recreate them on Windows with `powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File docs/demo/render_simple_icons.ps1`.

For the rasterization method, the original SVG files are retained alongside each generated PNG. The video files use the original marks as visual identifiers and are not an endorsement by the represented vendors.
