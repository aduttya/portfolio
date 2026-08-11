#!/usr/bin/env python3
"""Generate 1200x630 Open Graph cards matching the site's dark theme.

Background reproduces --grad-studio from style.css:
  radial-gradient(120% 85% at 50% 0%, #8a4b12 0%, #4a2606 40%, #170b00 72%, #0d0d0d 100%)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = "assets/images/og"

ORANGE = (249, 115, 22)      # --orange  #f97316
TEXT = (245, 241, 234)       # --text    #f5f1ea
MUTED = (156, 148, 136)      # --muted   #9c9488

F = "/usr/share/fonts/truetype/dejavu/"
FONT_BOLD = F + "DejaVuSans-Bold.ttf"
FONT_REG = F + "DejaVuSans.ttf"
FONT_MONO = F + "DejaVuSansMono-Bold.ttf"

# --grad-studio colour stops: (position 0-1, rgb)
STOPS = [(0.00, (138, 75, 18)), (0.40, (74, 38, 6)),
         (0.72, (23, 11, 0)), (1.00, (13, 13, 13))]


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def grad_colour(t):
    """Sample the studio gradient at normalised radius t."""
    t = max(0.0, min(1.0, t))
    for i in range(len(STOPS) - 1):
        p0, c0 = STOPS[i]
        p1, c1 = STOPS[i + 1]
        if p0 <= t <= p1:
            return lerp(c0, c1, (t - p0) / (p1 - p0))
    return STOPS[-1][1]


def studio_background():
    """Radial gradient: ellipse 120% x 85% centred at 50% 0%."""
    # Render at quarter scale then upscale - the gradient is smooth, so this
    # is visually identical and ~16x faster than per-pixel at full size.
    sw, sh = W // 4, H // 4
    img = Image.new("RGB", (sw, sh))
    px = img.load()
    cx, cy = sw / 2, 0.0
    rx, ry = 1.20 * sw, 0.85 * sh
    for y in range(sh):
        dy = (y - cy) / ry
        for x in range(sw):
            dx = (x - cx) / rx
            px[x, y] = grad_colour((dx * dx + dy * dy) ** 0.5)
    return img.resize((W, H), Image.LANCZOS)


def track(draw, xy, text, font, fill, spacing):
    """Draw letter-spaced text, returning the width consumed."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing
    return x - xy[0]


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build(name, eyebrow, title, subtitle):
    img = studio_background()
    d = ImageDraw.Draw(img)

    M = 90                      # margin
    max_w = W - 2 * M

    # Eyebrow: mono, uppercase, letter-spaced, orange
    f_eyebrow = ImageFont.truetype(FONT_MONO, 23)
    track(d, (M, 86), eyebrow.upper(), f_eyebrow, ORANGE, 3.2)

    # Text block runs from TOP down to FOOTER_TOP; the footer owns everything
    # below that. Shrink the title until title + subtitle actually fit, rather
    # than only capping the line count - a 3-line title at full size overruns
    # the footer.
    TOP, FOOTER_TOP, GAP, SUB_LH = 188, H - 150, 22, 38
    f_sub = ImageFont.truetype(FONT_REG, 27)
    sub_lines = wrap(d, subtitle, f_sub, max_w)[:2]
    sub_h = len(sub_lines) * SUB_LH

    for size in (74, 68, 62, 56, 50, 45, 40):
        f_title = ImageFont.truetype(FONT_BOLD, size)
        lines = wrap(d, title, f_title, max_w)
        lh = int(size * 1.22)
        if len(lines) <= 3 and len(lines) * lh + GAP + sub_h <= FOOTER_TOP - TOP:
            break

    y = TOP
    for ln in lines:
        d.text((M, y), ln, font=f_title, fill=TEXT)
        y += lh

    y += GAP
    for ln in sub_lines:
        d.text((M, y), ln, font=f_sub, fill=MUTED)
        y += SUB_LH

    # Footer rule + domain, anchored to the bottom
    d.rectangle([M, H - 108, M + 74, H - 104], fill=ORANGE)
    f_domain = ImageFont.truetype(FONT_MONO, 24)
    track(d, (M, H - 82), "aduttya.com", f_domain, MUTED, 1.6)

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".png")
    img.save(path, "PNG", optimize=True)
    print(f"{path:38} {os.path.getsize(path) // 1024}KB")


CARDS = [
    ("home", "AI Search / SEO / AEO", "Ajay Yadav",
     "Product & Technical Lead working on AI search systems, SEO/AEO "
     "frameworks, and how LLMs retrieve and cite web content."),
    ("blog", "Blog", "Writing on AI Search & Answer Engines",
     "Experiments and field notes on AI search, SEO, AEO, and LLM "
     "citation patterns."),
    ("work", "Work", "AI Search Projects, Research & Experiments",
     "Projects and experiments in AI search visibility, retrievability, "
     "and answer engine optimization."),
    ("research", "Research Paper", "Beyond Rankings",
     "Measuring vendor visibility in AI-driven discovery. Introducing "
     "ISIC: Inclusion, Stability, Influence, Coverage."),
    ("about", "About", "From Blockchain to AI Search",
     "Ajay Yadav's background, and current work as Product & Technical "
     "Lead at Flozi and SEO/AEO Lead at Neue World."),
]

if __name__ == "__main__":
    for c in CARDS:
        build(*c)
