#!/usr/bin/env python3
"""Card rendering engine: one layout, many output formats.

Colours come from style-warm.css :root (via tokens.py) and type is the same
Archivo variable font the site loads, vendored in assets/fonts. Nothing about
the design is defined here except geometry - so a card can never drift from
the site's palette or typography.

To add a social format, add an entry to FORMATS. Every value is explicit
rather than derived, so you can nudge one size without side effects.
"""
import os

from PIL import Image, ImageDraw, ImageFont

from tokens import rgb

FONT_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "assets", "fonts", "Archivo-Variable.ttf"
)

# Weight name -> (wght, wdth) axis values, matching the variation-settings
# the site itself uses for the equivalent role (e.g. .display is 780/122,
# .meta is 500/92). Keeps card type on the same footing as CSS type.
_AXES = {
    "bold": (780, 118),      # eyebrow, title, domain - display-weight text
    "semibold": (700, 108),  # unused today, kept for future formats
    "regular": (420, 100),   # subtitle - matches .lede's body weight
}


def font(weight, size):
    """A variable-font instance set to the axis values for `weight`."""
    f = ImageFont.truetype(FONT_PATH, size)
    wght, wdth = _AXES[weight]
    f.set_variation_by_axes([wght, wdth])
    return f


def mix(c1, c2, t):
    """Blend c1 -> c2 by t (0-1). Stands in for a CSS `opacity` value,
    which only makes sense against a known solid background once flattened
    into a PNG."""
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ── Formats ──────────────────────────────────────────────────────────────
# size          canvas in px
# margin        left/right text inset
# eyebrow_y     baseline-ish top of the orange kicker
# top           where the title block starts
# footer_space  px reserved at the bottom for the rule + domain
# titles        title sizes tried largest-first until the block fits
# max_lines     title line cap
# sub / sub_lh  subtitle size and line height
# max_sub       subtitle line cap

FORMATS = {
    "og": dict(
        size=(1200, 630), margin=90, eyebrow=23, eyebrow_y=86, track_eyebrow=3.2,
        top=188, footer_space=150, gap=22, titles=(74, 68, 62, 56, 50, 45, 40),
        max_lines=3, sub=27, sub_lh=38, max_sub=2,
        rule=(74, 4, 108), domain=24, domain_y=82, track_domain=1.6,
    ),
    "linkedin": dict(
        size=(1200, 627), margin=90, eyebrow=23, eyebrow_y=86, track_eyebrow=3.2,
        top=188, footer_space=150, gap=22, titles=(74, 68, 62, 56, 50, 45, 40),
        max_lines=3, sub=27, sub_lh=38, max_sub=2,
        rule=(74, 4, 108), domain=24, domain_y=82, track_domain=1.6,
    ),
    "square": dict(
        size=(1080, 1080), margin=88, eyebrow=25, eyebrow_y=130, track_eyebrow=3.4,
        top=280, footer_space=190, gap=28, titles=(88, 80, 72, 64, 58, 52, 46),
        max_lines=4, sub=30, sub_lh=44, max_sub=3,
        rule=(84, 5, 138), domain=26, domain_y=104, track_domain=1.8,
    ),
    "story": dict(
        size=(1080, 1920), margin=96, eyebrow=30, eyebrow_y=430, track_eyebrow=4.0,
        top=600, footer_space=420, gap=36, titles=(104, 96, 88, 80, 72, 64, 56),
        max_lines=5, sub=36, sub_lh=54, max_sub=4,
        rule=(96, 6, 360), domain=30, domain_y=318, track_domain=2.0,
    ),
    "x_header": dict(
        size=(1500, 500), margin=96, eyebrow=22, eyebrow_y=84, track_eyebrow=3.0,
        top=158, footer_space=126, gap=18, titles=(66, 60, 54, 48, 44, 40),
        max_lines=2, sub=25, sub_lh=34, max_sub=1,
        rule=(66, 4, 92), domain=22, domain_y=70, track_domain=1.6,
    ),
}

DOMAIN = "aduttya.com"


def panel_background(size, ink, orange):
    """Flat --ink panel with one soft orange circle bleeding off the top
    corner, echoing the site's .panel + .shape.circle.sh-orange texture -
    the warm system has no gradient tokens, so cards stay flat like the
    panels they're modelled on."""
    w, h = size
    img = Image.new("RGB", size, ink)

    d = 1.15 * max(w, h)
    veil = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(veil).ellipse(
        [w - d * 0.46, -d * 0.58, w - d * 0.46 + d, -d * 0.58 + d],
        fill=orange + (28,),
    )
    return Image.alpha_composite(img.convert("RGBA"), veil).convert("RGB")


def track(draw, xy, text, f, fill, spacing):
    """Draw letter-spaced text, returning the width consumed."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + spacing
    return x - xy[0]


def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render(fmt, eyebrow, title, subtitle):
    """Compose one card and return the image."""
    s = FORMATS[fmt]
    w, h = s["size"]
    ink, bone, orange = rgb("--ink"), rgb("--bone"), rgb("--orange")
    dim = mix(ink, bone, 0.62)  # subtitle/domain - stands in for opacity:.7

    img = panel_background(s["size"], ink, orange)
    d = ImageDraw.Draw(img)
    m = s["margin"]
    max_w = w - 2 * m

    # Eyebrow: bold, uppercase, letter-spaced, orange - matching the site's
    # .meta kicker treatment paired with an orange accent.
    track(d, (m, s["eyebrow_y"]), eyebrow.upper(),
          font("bold", s["eyebrow"]), orange, s["track_eyebrow"])

    # The text block runs from `top` down to the footer. Shrink the title
    # until title + subtitle actually fit, rather than only capping the line
    # count - a full-size title at max lines otherwise overruns the footer.
    footer_top = h - s["footer_space"]
    f_sub = font("regular", s["sub"])
    sub_lines = wrap(d, subtitle, f_sub, max_w)[:s["max_sub"]]
    sub_h = len(sub_lines) * s["sub_lh"]

    for size in s["titles"]:
        f_title = font("bold", size)
        lines = wrap(d, title, f_title, max_w)
        lh = int(size * 1.22)
        if (len(lines) <= s["max_lines"]
                and len(lines) * lh + s["gap"] + sub_h <= footer_top - s["top"]):
            break

    y = s["top"]
    for ln in lines:
        d.text((m, y), ln, font=f_title, fill=bone)
        y += lh

    y += s["gap"]
    for ln in sub_lines:
        d.text((m, y), ln, font=f_sub, fill=dim)
        y += s["sub_lh"]

    # Footer rule + domain, anchored to the bottom edge.
    rule_w, rule_h, rule_up = s["rule"]
    d.rectangle([m, h - rule_up, m + rule_w, h - rule_up + rule_h], fill=orange)
    track(d, (m, h - s["domain_y"]), DOMAIN,
          font("bold", s["domain"]), dim, s["track_domain"])

    return img


def save(img, out_dir, name):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".png")
    img.save(path, "PNG", optimize=True)
    print(f"{path:52} {os.path.getsize(path) // 1024}KB")
    return path
