"""Render the architecture SVG as a high-resolution PNG for LinkedIn and docs.

Requires Pillow. Run from the repository root with `python docs/images/render_architecture.py`.
The SVG remains the editable vector source; the PNG is the portable preview asset.
"""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "ivolve-platform-architecture.png"
SCALE = 2
W, H = 1800, 1160
FONT_REGULAR = Path("C:/Windows/Fonts/segoeui.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")
LOGO_ROOT = ROOT.parent / "demo" / "assets" / "logos"
APP_LOGOS = ROOT.parent.parent / "app" / "frontend" / "public" / "images"

BG1 = (8, 20, 38)
BG2 = (17, 29, 53)
LANE = (14, 26, 45)
CARD = (22, 36, 58)
CARD_ALT = (26, 45, 71)
STROKE = (56, 82, 113)
TEXT = (238, 244, 255)
BODY = (197, 210, 228)
MUTED = (159, 180, 206)
BLUE = (141, 184, 255)
GREEN = (113, 221, 176)

im = Image.new("RGB", (W * SCALE, H * SCALE), BG1)
pix = im.load()
for y in range(H * SCALE):
    t = y / max(1, H * SCALE - 1)
    color = tuple(round(BG1[i] * (1 - t) + BG2[i] * t) for i in range(3))
    for x in range(W * SCALE):
        pix[x, y] = color

d = ImageDraw.Draw(im)


def box(x, y, w, h, fill=CARD, outline=STROKE, radius=14, width=2):
    d.rounded_rectangle((x*SCALE, y*SCALE, (x+w)*SCALE, (y+h)*SCALE),
                        radius=radius*SCALE, fill=fill, outline=outline, width=width*SCALE)


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size*SCALE)


def label(x, y, value, size=15, color=BODY, bold=False):
    d.text((x*SCALE, y*SCALE), value, font=font(size, bold), fill=color)


def lines(x, y, values, size=15, color=BODY, gap=25):
    for i, value in enumerate(values):
        label(x, y+i*gap, value, size, color)


@lru_cache(maxsize=32)
def load_logo(name):
    if name.startswith("aws:"):
        path = LOGO_ROOT / "aws" / f"{name.split(':', 1)[1]}.png"
    elif name.startswith("brand:"):
        path = APP_LOGOS / f"{name.split(':', 1)[1]}-logo.png"
    else:
        path = LOGO_ROOT / "rasterized" / f"{name}.png"
    return Image.open(path).convert("RGBA")


def icon(name, x, y, size=30):
    """Draw a recognizable technology/service logo inside a light badge."""
    dark_mark = name in {"github", "ansible", "flask"}
    badge = (20, 35, 56) if dark_mark else (241, 246, 255)
    edge = (75, 103, 140) if dark_mark else (221, 232, 249)
    box(x, y, size, size, fill=badge, outline=edge, radius=7, width=1)
    mark = load_logo(name).copy()
    mark.thumbnail(((size-8)*SCALE, (size-8)*SCALE), Image.Resampling.LANCZOS)
    left = x*SCALE + (size*SCALE - mark.width)//2
    top = y*SCALE + (size*SCALE - mark.height)//2
    im.paste(mark, (left, top), mark)


def arrow(points, color=BLUE, width=3, head=10, dash=False):
    pts = [(x*SCALE, y*SCALE) for x, y in points]
    if dash:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            dx, dy = x2-x1, y2-y1
            length = (dx*dx+dy*dy)**0.5
            if length == 0:
                continue
            ux, uy = dx/length, dy/length
            pos = 0
            while pos < length:
                end = min(pos+9*SCALE, length)
                if (pos//(14*SCALE)) % 2 == 0:
                    d.line((x1+ux*pos, y1+uy*pos, x1+ux*end, y1+uy*end), fill=color, width=width*SCALE)
                pos += 14*SCALE
    else:
        d.line(pts, fill=color, width=width*SCALE, joint="curve")
    x2, y2 = pts[-1]
    x1, y1 = pts[-2]
    import math
    angle = math.atan2(y2-y1, x2-x1)
    back = head*SCALE
    side = back*0.58
    p1 = (x2, y2)
    p2 = (x2-back*math.cos(angle)+side*math.sin(angle), y2-back*math.sin(angle)-side*math.cos(angle))
    p3 = (x2-back*math.cos(angle)-side*math.sin(angle), y2-back*math.sin(angle)+side*math.cos(angle))
    d.polygon((p1, p2, p3), fill=color)


# Top source/CI lane
box(48, 122, 1704, 300, fill=LANE, outline=(45, 69, 100), radius=18)
label(74, 140, "SOURCE CONTROL & CONTINUOUS INTEGRATION", 16, BLUE, True)

box(78, 190, 260, 155)
icon("github", 104, 199)
label(144, 208, "GitHub repository", 20, TEXT, True)
lines(104, 244, ["Application source", "Kubernetes manifests", "Jenkinsfiles + workflows"], 15, BODY, 24)
box(104, 318, 106, 20, fill=(121, 170, 255), outline=(121, 170, 255), radius=10, width=1)
label(116, 318, "main branch", 12, (7, 20, 38), True)

box(424, 190, 300, 155, fill=CARD_ALT, outline=(80, 117, 165))
icon("jenkins", 450, 199)
label(490, 208, "Jenkins CI", 20, TEXT, True)
lines(450, 244, ["Controller on AWS EC2", "Three service pipelines", "Trusted Groovy Shared Library"], 15, BODY, 24)
label(450, 318, "Ansible configures Jenkins LTS", 13, MUTED)

box(802, 190, 300, 155)
icon("docker", 828, 199)
label(868, 208, "Docker build agent", 20, TEXT, True)
label(868, 244, "Docker Desktop container", 15, BODY)
icon("trivy", 828, 256, 20)
label(854, 268, "Trivy scan · AWS CLI", 15, BODY)
label(868, 292, "Builds and scans each service", 15, BODY)
label(868, 318, "Inbound WebSocket to Jenkins EC2", 13, MUTED)

box(1180, 190, 245, 155, fill=CARD_ALT, outline=(80, 117, 165))
icon("aws:ecr", 1206, 199)
label(1246, 208, "Amazon ECR", 20, TEXT, True)
lines(1206, 244, ["Private service repos", "frontend · auth · roadmap", "Scan-on-push"], 15, BODY, 24)
label(1206, 318, "Build-number image references", 13, MUTED)

arrow([(338, 260), (414, 260)], BLUE)
label(341, 238, "SCM checkout", 13, MUTED)
arrow([(724, 260), (792, 260)], BLUE)
label(727, 238, "remote build", 13, MUTED)
arrow([(1102, 260), (1170, 260)], BLUE)
label(1104, 238, "scan + push", 13, MUTED)
arrow([(574, 345), (574, 385), (208, 385), (208, 354)], BLUE)
label(298, 362, "Commit updated service manifest", 13, MUTED)

# AWS boundary and services
box(48, 452, 1704, 650, fill=(24, 40, 66), outline=(84, 115, 155), radius=18, width=2)
label(76, 466, "AWS CLOUD · eu-north-1", 16, BLUE, True)

box(80, 524, 280, 148)
icon("terraform", 106, 532)
label(146, 542, "Terraform + S3 state", 20, TEXT, True)
lines(106, 578, ["VPC · subnets · NAT · ACLs", "EKS · ECR · Jenkins · IAM"], 15, BODY, 24)
label(106, 638, "Encrypted, versioned remote state", 13, MUTED)

box(80, 714, 280, 142)
icon("ansible", 106, 722)
label(146, 732, "Ansible control host", 20, TEXT, True)
lines(106, 768, ["Dynamic EC2 inventory", "Installs Java · Docker · Trivy"], 15, BODY, 24)
label(106, 828, "Configures Jenkins over SSH", 13, MUTED)

box(424, 524, 1275, 525, fill=(14, 27, 44), outline=(110, 140, 175), radius=20, width=2)
label(450, 536, "VPC 10.40.0.0/16 · public and private subnets across two AZs", 16, BLUE, True)

box(450, 584, 365, 372, fill=CARD_ALT, outline=(80, 117, 165))
icon("aws:ec2", 476, 592)
label(516, 602, "Jenkins EC2 host", 20, TEXT, True)
lines(476, 640, ["Jenkins controller :8080", "Dedicated ECR instance role"], 15, BODY, 25)
d.line((476*SCALE, 700*SCALE, 790*SCALE, 700*SCALE), fill=(62, 88, 120), width=2*SCALE)
icon("github", 476, 714, 26)
label(512, 724, "GitHub Actions runner", 18, TEXT, True)
lines(476, 758, ["Self-hosted Linux x64 service", "AWS CLI · kubectl · VPC access"], 15, BODY, 25)
label(476, 824, "Deploys to private EKS API", 13, MUTED)
label(476, 888, "Admin SSH/UI restricted by CIDR", 13, MUTED)

box(862, 584, 300, 372)
icon("kubernetes", 888, 592)
label(928, 602, "Amazon EKS", 20, TEXT, True)
lines(888, 640, ["Control plane: ivolve-x-dev", "Private managed node group", "Two Ready t3.small workers"], 15, BODY, 25)
d.line((888*SCALE, 724*SCALE, 1136*SCALE, 724*SCALE), fill=(62, 88, 120), width=2*SCALE)
label(888, 744, "Application + storage", 18, TEXT, True)
icon("nodedotjs", 888, 769, 20)
label(914, 780, "Frontend pod", 15, BODY)
icon("flask", 888, 794, 20)
label(914, 805, "Auth API pod", 15, BODY)
icon("springboot", 888, 819, 20)
label(914, 830, "Roadmap API pod", 15, BODY)
icon("mysql", 888, 844, 20)
label(914, 855, "MySQL StatefulSet", 15, BODY)
icon("aws:ebs", 888, 869, 20)
label(914, 880, "gp3 EBS volume", 15, BODY)
label(888, 920, "All namespaced workloads: ivolve", 13, MUTED)

box(1208, 584, 455, 152, fill=CARD_ALT, outline=(80, 117, 165))
icon("aws:elb", 1234, 592)
label(1274, 602, "Public subnet · Application Load Balancer", 19, TEXT, True)
lines(1234, 640, ["AWS Load Balancer Controller + Ingress", "HTTP :80 → frontend ClusterIP Service"], 15, BODY, 26)
label(1234, 704, "Health checks route to ready frontend pods", 13, MUTED)

box(1208, 804, 455, 152)
icon("brand:ivolve", 1234, 812, 28)
label(1272, 822, "Browser / project user", 20, TEXT, True)
lines(1234, 860, ["Open current ALB DNS address over HTTP", "Sign up → login → view roadmap"], 15, BODY, 26)
label(1234, 924, "Frontend calls Auth + Roadmap internally", 13, MUTED)

# Provisioning and runtime paths
arrow([(220, 672), (220, 684), (400, 684), (400, 540), (424, 540)], MUTED, 2, dash=True)
arrow([(360, 784), (410, 784), (410, 650), (450, 650)], MUTED, 2, dash=True)
arrow([(338, 320), (386, 320), (386, 800), (450, 800)], GREEN)
label(391, 750, "manifest push trigger", 12, GREEN)
arrow([(815, 875), (850, 875)], GREEN)
label(817, 850, "kubectl apply -k", 12, GREEN)
arrow([(1162, 665), (1198, 665)], BLUE)
label(1165, 643, "Ingress", 12, MUTED)
arrow([(1208, 855), (1180, 855), (1180, 704), (1200, 704)], BLUE)
label(1164, 824, "HTTP :80", 12, MUTED)

box(78, 1000, 1580, 48, fill=(10, 20, 36), outline=(38, 60, 89), radius=12, width=1)
d.ellipse((100*SCALE, 1017*SCALE, 116*SCALE, 1033*SCALE), fill=BLUE)
label(124, 1011, "CI / source", 13, MUTED)
d.ellipse((282*SCALE, 1017*SCALE, 298*SCALE, 1033*SCALE), fill=GREEN)
label(306, 1011, "deployment", 13, MUTED)
d.ellipse((464*SCALE, 1017*SCALE, 480*SCALE, 1033*SCALE), fill=MUTED)
label(488, 1011, "infrastructure provisioning/configuration", 13, MUTED)
label(1090, 1011, "EKS · NAT · EC2 · ALB · EBS may incur AWS charges", 13, MUTED)

im = im.resize((W, H), Image.Resampling.LANCZOS)
im.save(OUTPUT, "PNG", optimize=True)
print(f"Rendered {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
