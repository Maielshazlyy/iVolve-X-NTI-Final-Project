"""Render the project architecture as a high-resolution PNG. Requires Pillow."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ivolve-platform-architecture.png"
SCALE = 2
W, H = 1600, 1060
LOGOS = ROOT.parent / "demo" / "assets" / "logos" / "rasterized"
AWS_LOGOS = ROOT.parent / "demo" / "assets" / "logos" / "aws"
APP_LOGOS = ROOT.parent.parent / "app" / "frontend" / "public" / "images"
BG = (8, 17, 32)
PANEL = (16, 29, 49)
CARD = (23, 39, 63)
CARD2 = (27, 48, 76)
EDGE = (53, 79, 111)
WHITE = (239, 245, 255)
BODY = (191, 207, 228)
MUTED = (143, 165, 194)
BLUE = (117, 170, 255)
GREEN = (95, 218, 166)

im = Image.new("RGB", (W * SCALE, H * SCALE), BG)
d = ImageDraw.Draw(im)
regular = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18 * SCALE)
bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20 * SCALE)
large = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36 * SCALE)
small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15 * SCALE)


def rect(x, y, w, h, fill=CARD, edge=EDGE, radius=18):
    d.rounded_rectangle((x*SCALE, y*SCALE, (x+w)*SCALE, (y+h)*SCALE), radius=radius*SCALE, fill=fill, outline=edge, width=2*SCALE)


def text(x, y, value, font=regular, color=BODY):
    d.text((x*SCALE, y*SCALE), value, font=font, fill=color)


@lru_cache(maxsize=64)
def logo(name):
    if name.startswith("aws:"):
        path = AWS_LOGOS / f"{name.split(':', 1)[1]}.png"
    elif name.startswith("brand:"):
        path = APP_LOGOS / f"{name.split(':', 1)[1]}-logo.png"
    else:
        path = LOGOS / f"{name}.png"
    return Image.open(path).convert("RGBA")


def icon(name, x, y, size=38):
    badge = (20, 35, 56) if name == "github" else (241, 246, 255)
    edge = (75, 103, 140) if name == "github" else (221, 232, 249)
    d.rounded_rectangle((x*SCALE, y*SCALE, (x+size)*SCALE, (y+size)*SCALE), radius=8*SCALE, fill=badge, outline=edge, width=SCALE)
    mark = logo(name).copy()
    mark.thumbnail(((size-10)*SCALE, (size-10)*SCALE), Image.Resampling.LANCZOS)
    im.paste(mark, (x*SCALE+(size*SCALE-mark.width)//2, y*SCALE+(size*SCALE-mark.height)//2), mark)


def card(x, y, w, h, service_logo, heading, bullets, fill=CARD):
    rect(x, y, w, h, fill)
    icon(service_logo, x+22, y+22)
    text(x+72, y+26, heading, bold, WHITE)
    for i, bullet in enumerate(bullets):
        text(x+24, y+82+i*31, bullet, regular, BODY)


def arrow(x1, y1, x2, y2, color=BLUE, width=5):
    d.line((x1*SCALE, y1*SCALE, x2*SCALE, y2*SCALE), fill=color, width=width*SCALE)
    import math
    angle = math.atan2(y2-y1, x2-x1)
    size = 14*SCALE
    points = [(x2*SCALE, y2*SCALE),
              (x2*SCALE-size*math.cos(angle-0.45), y2*SCALE-size*math.sin(angle-0.45)),
              (x2*SCALE-size*math.cos(angle+0.45), y2*SCALE-size*math.sin(angle+0.45))]
    d.polygon(points, fill=color)


text(54, 34, "iVolve × NTI | Cloud DevOps Architecture", large, WHITE)
text(57, 88, "GitHub Actions owns CI · Argo CD owns CD · Terraform provisions AWS", regular, MUTED)

rect(42, 142, 1516, 314, PANEL, (44, 68, 98), 22)
text(70, 160, "SOURCE CONTROL & CONTINUOUS INTEGRATION", bold, BLUE)
card(76, 207, 300, 190, "github", "GitHub repository", ["Application source", "Kubernetes manifests", "main branch is desired state"])
card(434, 207, 330, 190, "github", "GitHub Actions · CI", ["Hosted runner builds services", "Trivy scans container images", "Commit SHA image tags"], CARD2)
card(822, 207, 300, 190, "aws:ecr", "Amazon ECR", ["Private repositories", "frontend · auth · roadmap", "Immutable image tags"])
card(1180, 207, 330, 190, "github", "Manifest update", ["CI commits image references", "Argo CD watches this branch", "No workflow kubectl deploy"])
arrow(376, 302, 423, 302)
arrow(764, 302, 811, 302)
arrow(1122, 302, 1169, 302)
text(390, 273, "push", small, MUTED)
text(776, 273, "scan + publish", small, MUTED)
text(1132, 273, "new SHA", small, MUTED)

rect(42, 490, 1516, 510, (20, 36, 59), (66, 97, 134), 22)
text(70, 510, "AWS CLOUD · eu-north-1", bold, BLUE)
card(76, 568, 330, 180, "terraform", "Terraform + S3", ["VPC · subnets · NAT · ACLs", "EKS · ECR · IAM", "Encrypted remote state"])
card(76, 766, 330, 178, "aws:ecr", "CI identity", ["Existing IAM user", "ECR push limited to project repos", "No EKS deployment access"])

rect(452, 550, 1068, 390, (12, 25, 42), (90, 121, 158), 20)
text(480, 570, "VPC · public/private subnets across two Availability Zones", bold, BLUE)
card(492, 628, 338, 230, "kubernetes", "Amazon EKS", ["ivolve-x-dev · 2 worker nodes", "Argo CD watches Git desired state", "Argo CD syncs the dev overlay", "Namespace: ivolve"], CARD2)
card(866, 628, 278, 230, "aws:elb", "Public ALB", ["AWS Load Balancer Controller", "Ingress sends HTTP to frontend", "Health checks on ready pods"])
card(1180, 628, 290, 230, "brand:ivolve", "Application", ["Frontend + Auth API", "Roadmap API + MySQL", "MySQL data on gp3 EBS"])
arrow(830, 744, 855, 744, GREEN)
arrow(1144, 744, 1169, 744, GREEN)
text(819, 718, "Ingress", small, MUTED)
text(1130, 718, "HTTP", small, MUTED)

arrow(1320, 397, 1320, 470, GREEN)
text(1334, 424, "Argo CD sync", small, GREEN)
arrow(406, 657, 438, 657, MUTED, 3)
arrow(406, 854, 438, 854, MUTED, 3)
text(58, 1022, "CODE CHANGE → BUILD + SCAN → ECR → GIT MANIFEST → ARGO CD SYNC → EKS", bold, WHITE)

im.resize((W, H), Image.Resampling.LANCZOS).save(OUT, optimize=True)
print(OUT)
