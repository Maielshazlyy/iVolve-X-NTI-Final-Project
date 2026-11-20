"""Create silent, caption-first project explainer videos from original graphics.

Requires Pillow and FFmpeg with libx264. No application screenshots are used.
Run from the repository root:
  python docs/demo/generate_explainer.py --ffmpeg PATH_TO_FFMPEG
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
NAVY = (7, 15, 30)
PANEL = (17, 29, 49)
PANEL_2 = (22, 39, 64)
TEXT = (241, 246, 255)
MUTED = (162, 181, 207)
BLUE = (76, 151, 255)
GREEN = (62, 220, 168)
PURPLE = (175, 136, 255)
FONT_DIR = Path("C:/Windows/Fonts")
REGULAR = FONT_DIR / "segoeui.ttf"
BOLD = FONT_DIR / "segoeuib.ttf"


SCENES = [
    {
        "section": "THE PROJECT",
        "title": "IVOLVE × NTI",
        "subtitle": "A cloud DevOps delivery platform",
        "caption": "From a training application in source control to a live deployment on Amazon EKS.",
        "nodes": [("github", "SOURCE", "GitHub"), ("jenkins", "BUILD", "Jenkins"), ("kubernetes", "DEPLOY", "Amazon EKS"), ("aws:elb", "LIVE", "AWS ALB")],
        "accent": BLUE,
    },
    {
        "section": "01 · APPLICATION",
        "title": "One app, four workloads",
        "subtitle": "A web UI, two APIs, and persistent data",
        "caption": "The frontend handles signup, login, and the roadmap page. Auth and Roadmap APIs serve it, while MySQL stores user accounts.",
        "nodes": [("nodedotjs", "WEB", "Frontend"), ("flask", "API", "Auth API"), ("springboot", "API", "Roadmap API"), ("mysql", "DATA", "MySQL")],
        "accent": BLUE,
    },
    {
        "section": "02 · LOCAL DEVELOPMENT",
        "title": "Docker Compose",
        "subtitle": "Reproducible local services",
        "caption": "Docker Compose starts the frontend, APIs, and MySQL together with configured networking, environment values, and health checks.",
        "nodes": [("docker", "RUNTIME", "Docker Compose"), ("nodedotjs", "CONTAINER", "Frontend"), ("flask", "CONTAINER", "Auth API"), ("mysql", "VOLUME", "MySQL data")],
        "accent": PURPLE,
    },
    {
        "section": "03 · INFRASTRUCTURE AS CODE",
        "title": "Terraform builds AWS",
        "subtitle": "Network, compute, registry, and remote state",
        "caption": "Terraform provisions a VPC across two Availability Zones, public and private subnets, EKS, ECR, Jenkins EC2, and encrypted S3 state.",
        "nodes": [("terraform", "INFRASTRUCTURE", "Terraform"), ("aws:ec2", "COMPUTE", "Jenkins EC2"), ("aws:ecr", "REGISTRY", "Amazon ECR"), ("aws:s3", "REMOTE STATE", "Amazon S3")],
        "accent": BLUE,
    },
    {
        "section": "04 · CONFIGURATION MANAGEMENT",
        "title": "Ansible configures Jenkins",
        "subtitle": "Repeatable host setup over SSH",
        "caption": "Ansible discovers the Jenkins EC2 host and installs Java, Docker, Trivy, and Jenkins configuration through reusable roles.",
        "nodes": [("ansible", "CONTROL", "Ansible"), ("aws:ec2", "HOST", "Jenkins EC2"), ("jenkins", "CONTROLLER", "Jenkins"), ("docker", "BUILD TOOLS", "Docker + Trivy")],
        "accent": GREEN,
    },
    {
        "section": "05 · CONTINUOUS INTEGRATION",
        "title": "Three service pipelines",
        "subtitle": "Frontend · Auth · Roadmap",
        "caption": "Each Jenkins pipeline checks out the code, builds its service image on a Docker build agent, and runs a Trivy vulnerability scan.",
        "nodes": [("jenkins", "CI", "Jenkins pipelines"), ("docker", "AGENT", "Docker build agent"), ("nodedotjs", "SERVICE", "Frontend"), ("springboot", "SERVICE", "Java Roadmap API")],
        "accent": PURPLE,
    },
    {
        "section": "06 · IMAGE DELIVERY",
        "title": "Scan, publish, record",
        "subtitle": "Trivy → Amazon ECR → Git commit",
        "caption": "Passing images are pushed to private ECR repositories. Jenkins updates the matching Kubernetes manifest with the new image tag and commits it.",
        "nodes": [("trivy", "SECURITY SCAN", "Trivy"), ("aws:ecr", "IMAGE REGISTRY", "Amazon ECR"), ("github", "MANIFEST", "Image tag"), ("github", "CHANGE", "Git commit")],
        "accent": GREEN,
    },
    {
        "section": "07 · CONTINUOUS DELIVERY",
        "title": "GitHub Actions deploys",
        "subtitle": "A manifest change starts the workflow",
        "caption": "The deployment workflow configures AWS and kubectl, applies the development overlay, waits for MySQL and application rollouts, and reports the deployed resources.",
        "nodes": [("github", "TRIGGER", "Manifest push"), ("github", "WORKFLOW", "GitHub Actions"), ("kubernetes", "DEPLOY", "Kustomize to EKS"), ("kubernetes", "VERIFY", "Rollout status")],
        "accent": BLUE,
    },
    {
        "section": "08 · KUBERNETES",
        "title": "EKS runs the application",
        "subtitle": "Healthy pods and persistent MySQL storage",
        "caption": "The EKS cluster runs the frontend, Auth API, Roadmap API, and MySQL StatefulSet. The EBS CSI driver provisions the gp3 database volume.",
        "nodes": [("kubernetes", "PLATFORM", "Amazon EKS"), ("nodedotjs", "WEB POD", "Frontend"), ("mysql", "STATEFUL", "MySQL") , ("aws:ebs", "STORAGE", "EBS gp3 volume")],
        "accent": PURPLE,
    },
    {
        "section": "09 · USER ACCESS",
        "title": "AWS ALB serves the app",
        "subtitle": "Browser → Ingress → frontend → APIs",
        "caption": "The AWS Load Balancer Controller creates an Application Load Balancer. It routes browser traffic to the frontend, which calls the APIs inside the cluster.",
        "nodes": [("ivolve", "APPLICATION", "iVolve × NTI"), ("aws:elb", "ENTRY POINT", "Application Load Balancer"), ("nodedotjs", "WEB", "Frontend service"), ("flask", "APIs", "Auth + Roadmap")],
        "accent": GREEN,
    },
    {
        "section": "END-TO-END DELIVERY",
        "title": "Code becomes a live service",
        "subtitle": "Build · scan · publish · deploy · verify",
        "caption": "Together, Terraform, Ansible, Jenkins, Trivy, ECR, Kubernetes, and GitHub Actions create a repeatable path from a code change to the live training roadmap.",
        "nodes": [("terraform", "01 · IaC", "Provision AWS"), ("ansible", "02 · CONFIG", "Prepare Jenkins"), ("jenkins", "03 · CI", "Build + scan"), ("kubernetes", "04 · CD", "Deploy + verify")],
        "accent": BLUE,
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = BOLD if bold else REGULAR
    return ImageFont.truetype(str(path), size)


@lru_cache(maxsize=32)
def logo_image(name: str) -> Image.Image:
    if name == "ivolve":
        path = ROOT / "app/frontend/public/images/ivolve-logo.png"
    elif name == "nti":
        path = ROOT / "app/frontend/public/images/nti-logo.png"
    elif name.startswith("aws:"):
        path = ROOT / f"docs/demo/assets/logos/aws/{name.split(':', 1)[1]}.png"
    else:
        path = ROOT / f"docs/demo/assets/logos/rasterized/{name}.png"
    return Image.open(path).convert("RGBA")


def place_logo(base: Image.Image, name: str, box: tuple[int, int, int, int], card=False):
    x, y, width, height = box
    image = logo_image(name)
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    if card:
        draw = ImageDraw.Draw(base)
        rounded(draw, (x, y, x + width, y + height), (28, 45, 70), None, min(24, height // 3), 1)
    base.paste(image, (x + (width - image.width) // 2, y + (height - image.height) // 2), image)


def draw_brand_lockup(base: Image.Image, left: int, top: int, vertical: bool):
    if vertical:
        panel_w, panel_h, gap = 420, 90, 22
        place_logo(base, "ivolve", (left, top, panel_w, panel_h), card=True)
        place_logo(base, "nti", (left + panel_w + gap, top, panel_w, panel_h), card=True)
    else:
        panel_w, panel_h, gap = 290, 76, 18
        place_logo(base, "ivolve", (left, top, panel_w, panel_h), card=True)
        place_logo(base, "nti", (left + panel_w + gap, top, panel_w, panel_h), card=True)


def rounded(draw: ImageDraw.ImageDraw, box, fill, outline=None, radius=22, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap(draw, text, selected_font, max_width):
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=selected_font)[2] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_scene(scene, index, total, vertical=False, include_explanations=True):
    width, height = (1080, 1920) if vertical else (1920, 1080)
    image = Image.new("RGB", (width, height), NAVY)
    draw = ImageDraw.Draw(image)
    accent = scene["accent"]

    # Subtle corner light and a restrained frame grid.
    for radius in range(550, 0, -18):
        alpha = (550 - radius) / 550
        color = (int(8 + 10 * alpha), int(18 + 20 * alpha), int(36 + 34 * alpha))
        draw.ellipse((width - radius * 1.25, -radius, width + radius, radius), fill=color)
    draw.line((0, 0, width, 0), fill=accent, width=9)

    if vertical:
        margin = 68
        if index in (0, total - 1):
            draw_brand_lockup(image, margin, 52, vertical=True)
        else:
            draw.text((margin, 92), "IVOLVE  ×  NTI", font=font(30, True), fill=TEXT)
        draw.text((margin, 180 if index in (0, total - 1) else 168), f"STAGE {index + 1:02d} / {total:02d}", font=font(22, True), fill=accent)
        draw.text((margin, 278), scene["section"], font=font(25, True), fill=accent)
        title_font = font(66, True)
        title_lines = wrap(draw, scene["title"], title_font, width - 2 * margin)
        y = 334
        for line in title_lines:
            draw.text((margin, y), line, font=title_font, fill=TEXT)
            y += 82
        subtitle_font = font(32)
        sublines = wrap(draw, scene["subtitle"], subtitle_font, width - 2 * margin)
        y += 12
        for line in sublines:
            draw.text((margin, y), line, font=subtitle_font, fill=MUTED)
            y += 48

        cards_top = 650
        card_h, gap = 144, 24
        for i, (brand, kind, label) in enumerate(scene["nodes"]):
            top = cards_top + i * (card_h + gap)
            rounded(draw, (margin, top, width - margin, top + card_h), PANEL, PANEL_2, 24, 2)
            draw.rounded_rectangle((margin, top, margin + 11, top + card_h), radius=6, fill=accent)
            place_logo(image, brand, (margin + 28, top + 22, 100, 100), card=True)
            text_x = margin + 150
            draw.text((text_x, top + 29), kind, font=font(19, True), fill=accent)
            label_font = font(33 if len(label) < 15 else 27, True)
            label_lines = wrap(draw, label, label_font, width - margin - text_x - 35)
            yy = top + 59
            for line in label_lines[:2]:
                draw.text((text_x, yy), line, font=label_font, fill=TEXT)
                yy += 39
            if i < len(scene["nodes"]) - 1:
                cx = width // 2
                draw.line((cx, top + card_h, cx, top + card_h + gap - 3), fill=(87, 117, 157), width=3)

        if include_explanations:
            caption_y, caption_h = 1370, 358
            rounded(draw, (margin, caption_y, width - margin, caption_y + caption_h), (11, 24, 43), (42, 64, 94), 26, 2)
            draw.text((margin + 34, caption_y + 28), "WHAT HAPPENS", font=font(21, True), fill=accent)
            body_font = font(31)
            body_lines = wrap(draw, scene["caption"], body_font, width - 2 * margin - 68)
            y = caption_y + 78
            for line in body_lines[:5]:
                draw.text((margin + 34, y), line, font=body_font, fill=TEXT)
                y += 48
        draw.text((margin, height - 78), "CLOUD DEVOPS  ·  AWS  ·  KUBERNETES", font=font(18, True), fill=MUTED)
    else:
        margin = 100
        if index in (0, total - 1):
            draw_brand_lockup(image, margin, 24, vertical=False)
        else:
            draw.text((margin, 56), "IVOLVE  ×  NTI", font=font(28, True), fill=TEXT)
        draw.text((width - margin - 270, 64), f"STAGE {index + 1:02d} / {total:02d}", font=font(22, True), fill=accent)
        draw.text((margin, 190), scene["section"], font=font(25, True), fill=accent)
        title_font = font(64, True)
        title_lines = wrap(draw, scene["title"], title_font, width - 2 * margin)
        y = 242
        for line in title_lines[:2]:
            draw.text((margin, y), line, font=title_font, fill=TEXT)
            y += 77
        subtitle_y = y + 8
        draw.text((margin, subtitle_y), scene["subtitle"], font=font(29), fill=MUTED)

        # Four connected cards form an original, screenshot-free process graphic.
        card_y, card_h = 490, 210
        gap = 26
        card_w = (width - 2 * margin - 3 * gap) // 4
        for i, (brand, kind, label) in enumerate(scene["nodes"]):
            left = margin + i * (card_w + gap)
            rounded(draw, (left, card_y, left + card_w, card_y + card_h), PANEL, PANEL_2, 24, 2)
            draw.rounded_rectangle((left, card_y, left + card_w, card_y + 9), radius=5, fill=accent)
            place_logo(image, brand, (left + 22, card_y + 53, 102, 102), card=True)
            draw.text((left + 142, card_y + 44), kind, font=font(16, True), fill=accent)
            label_font = font(29 if len(label) < 15 else 23, True)
            lines = wrap(draw, label, label_font, card_w - 162)
            yy = card_y + 82
            for line in lines[:2]:
                draw.text((left + 142, yy), line, font=label_font, fill=TEXT)
                yy += 40
            if i < 3:
                cy = card_y + card_h // 2
                x1, x2 = left + card_w + 5, left + card_w + gap - 5
                draw.line((x1, cy, x2, cy), fill=accent, width=4)
                draw.polygon([(x2, cy), (x2 - 12, cy - 8), (x2 - 12, cy + 8)], fill=accent)

        # A process rail makes stage position clear without using screenshots.
        rail_y = 775
        draw.line((margin, rail_y, width - margin, rail_y), fill=(40, 60, 88), width=4)
        active_x = margin + int((width - 2 * margin) * ((index + 1) / total))
        draw.line((margin, rail_y, active_x, rail_y), fill=accent, width=5)
        draw.ellipse((active_x - 11, rail_y - 11, active_x + 11, rail_y + 11), fill=accent)

        if include_explanations:
            caption_box = (margin, 840, width - margin, 1000)
            rounded(draw, caption_box, (11, 24, 43), (42, 64, 94), 22, 2)
            draw.text((margin + 30, 860), "PROJECT WALKTHROUGH", font=font(18, True), fill=accent)
            body_font = font(27)
            lines = wrap(draw, scene["caption"], body_font, width - 2 * margin - 60)
            y = 900
            for line in lines[:2]:
                draw.text((margin + 30, y), line, font=body_font, fill=TEXT)
                y += 38
        draw.text((margin, height - 42), "TERRAFORM  ·  ANSIBLE  ·  JENKINS  ·  TRIVY  ·  EKS  ·  GITHUB ACTIONS", font=font(16, True), fill=MUTED)
    return image.convert("RGB")


def write_srt(path: Path, indices, duration: float, transition: float):
    def stamp(seconds):
        millis = round(seconds * 1000)
        h, millis = divmod(millis, 3_600_000)
        m, millis = divmod(millis, 60_000)
        s, millis = divmod(millis, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{millis:03d}"

    final_duration = duration * len(indices) - transition * (len(indices) - 1)
    rows = []
    for n, scene_index in enumerate(indices):
        start = n * (duration - transition)
        end = (n + 1) * (duration - transition) if n < len(indices) - 1 else final_duration
        rows.append(f"{n + 1}\n{stamp(start)} --> {stamp(end)}\n{SCENES[scene_index]['caption']}\n")
    path.write_text("\n".join(rows), encoding="utf-8")


def export(ffmpeg: str, output: Path, indices, duration, vertical=False, cover: Path | None = None, transition=0.45, include_explanations=True):
    width, height = (1080, 1920) if vertical else (1920, 1080)
    build_tmp = ROOT / ".codex-video-tmp"
    build_tmp.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ivolve-video-", dir=build_tmp) as tmp_name:
        tmp = Path(tmp_name)
        slides = []
        for n, scene_index in enumerate(indices):
            slide = tmp / f"slide-{n:02d}.png"
            draw_scene(SCENES[scene_index], n, len(indices), vertical, include_explanations).save(slide, optimize=True)
            slides.append(slide)
            if n == 0 and cover is not None:
                cover.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(slide, cover)

        filters = []
        for n in range(len(slides)):
            filters.append(f"[{n}:v]fps=24,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{n}]")
        active = "v0"
        for n in range(1, len(slides)):
            output_label = f"xf{n}"
            offset = n * (duration - transition)
            filters.append(
                f"[{active}][v{n}]xfade=transition=fade:duration={transition:.3f}:offset={offset:.3f}[{output_label}]"
            )
            active = output_label
        final_duration = duration * len(slides) - transition * (len(slides) - 1)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Keep resource use modest: the 11 slide images otherwise cause FFmpeg
        # to start many decoder and encoder threads on memory-limited machines.
        command = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-filter_complex_threads", "1"]
        for slide in slides:
            command.extend(["-threads", "1", "-loop", "1", "-framerate", "24", "-t", f"{duration:.3f}", "-i", str(slide)])
        command.extend([
            "-filter_complex", ";".join(filters), "-map", f"[{active}]", "-an", "-c:v", "libx264",
            "-threads", "1", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-t", f"{final_duration:.3f}", str(output),
        ])
        subprocess.run(command, check=True)
    if include_explanations:
        write_srt(output.with_suffix(".srt"), indices, duration, transition)
    print(f"Created {output} ({width}x{height}, {final_duration:.1f}s, logo-led, cross-fades, {'captions' if include_explanations else 'no subtitles'}, silent)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", required=True, help="Path to ffmpeg executable")
    parser.add_argument("--no-captions", action="store_true", help="Create clean versions without explanation panels or SRT files")
    args = parser.parse_args()
    if args.no_captions:
        export(
            args.ffmpeg,
            OUT / "ivolve-devops-explainer-no-captions.mp4",
            list(range(len(SCENES))),
            6.5,
            cover=OUT / "ivolve-devops-explainer-no-captions-cover.png",
            include_explanations=False,
        )
        export(
            args.ffmpeg,
            OUT / "ivolve-devops-linkedin-no-captions.mp4",
            list(range(len(SCENES))),
            5.4,
            vertical=True,
            cover=OUT / "ivolve-devops-linkedin-no-captions-cover.png",
            include_explanations=False,
        )
    else:
        export(
            args.ffmpeg,
            OUT / "ivolve-devops-explainer.mp4",
            list(range(len(SCENES))),
            6.5,
            cover=OUT / "ivolve-devops-explainer-cover.png",
        )
        export(
            args.ffmpeg,
            OUT / "ivolve-devops-linkedin.mp4",
            list(range(len(SCENES))),
            5.4,
            vertical=True,
            cover=OUT / "ivolve-devops-linkedin-cover.png",
        )


if __name__ == "__main__":
    main()
