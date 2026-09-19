#!/usr/bin/env python3
"""Build _scripts/preview.html - the whole design system on one page.

Colour, type, components and every generated card, read live from
style-warm.css, the built site, and the assets folder. Nothing is
hand-listed: the component gallery is lifted from real markup the site
actually ships (see scan_components.py), so the page cannot drift from
what is actually in the repo, and a class stops appearing here the moment
nothing in the site uses it anymore.

    python3 _scripts/make_preview.py && open _scripts/preview.html

Lives under _scripts/ so Jekyll never publishes it (underscore folders are
excluded from the build) - this is a workbench, not a site page.
"""
import glob
import html as htmlmod
import os
import re
import subprocess

from cards import FORMATS
from scan_components import discover
from tokens import all_tokens, value

ROOT = os.path.join(os.path.dirname(__file__), os.pardir)
OUT = os.path.join(os.path.dirname(__file__), "preview.html")
CSS_PATH = os.path.join(ROOT, "style-warm.css")
SITE_GLOB = os.path.join(ROOT, "_site", "**", "*.html")
SITE_EXCLUDE = ("/IDEAS/", "/assets/")  # built output that isn't a design-system page

SOCIAL = "assets/images/social"
OG_DIRS = [("og", "assets/images/og"), ("og", "assets/images/posts")]


def rebuild_site():
    """Best-effort `jekyll build` so the component scan sees current markup.
    Non-fatal - if Jekyll isn't set up, the scan just falls back to
    whatever _site/ already has on disk."""
    try:
        subprocess.run(
            ["bundle", "exec", "jekyll", "build", "--quiet"],
            cwd=ROOT, check=False, timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        print("  (skipped `jekyll build` - bundle/jekyll not available)")


def is_colour(v):
    return v.startswith("#") or v.startswith("rgb")


def is_gradient(v):
    return "gradient(" in v


def swatches(tokens):
    rows = []
    for name, val in tokens.items():
        if not is_colour(val):
            continue
        rows.append(
            f'<div class="sw"><div class="chip" style="background:{val}"></div>'
            f'<code>{name}</code><span>{val}</span></div>'
        )
    return "\n".join(rows)


def gradients(tokens):
    rows = []
    for name, val in tokens.items():
        if not is_gradient(val):
            continue
        rows.append(
            f'<div class="grad"><div class="band" style="background:{val}"></div>'
            f'<code>{name}</code></div>'
        )
    return "\n".join(rows)


def other(tokens):
    rows = []
    for name, val in tokens.items():
        if is_colour(val) or is_gradient(val):
            continue
        rows.append(f"<tr><td><code>{name}</code></td><td>{val}</td></tr>")
    return "\n".join(rows)


def localize(snippet):
    """Root-relative src/href ("/assets/...") resolve against the real site's
    domain root, not against _scripts/ - rewrite them to climb back up to
    the repo root so images actually load when this file is opened
    directly. The copyable source is left untouched: paste it into a real
    page and the original root-relative paths are exactly what you want."""
    return re.sub(r'(src|href)="/(?!/)', r'\1="../', snippet)


def components_section(items):
    if not items:
        return ""
    order, by_section = [], {}
    for it in items:
        sec = it["section"] or "Other"
        by_section.setdefault(sec, []).append(it)
        if sec not in order:
            order.append(sec)

    out = []
    for sec in order:
        cards = []
        for it in by_section[sec]:
            escaped = htmlmod.escape(it["html"])
            cards.append(f"""
<div class="comp">
  <div class="comp-head">
    <code>.{it['cls']}</code>
    <button class="copy" type="button" data-copy>Copy</button>
  </div>
  <div class="comp-live">{localize(it['html'])}</div>
  <pre class="comp-src"><code>{escaped}</code></pre>
  <textarea class="comp-raw" hidden>{escaped}</textarea>
</div>""")
        out.append(f'<h3>{sec}</h3><div class="comp-grid">{"".join(cards)}</div>')
    return "\n".join(out)


def cards_section():
    out = []
    for fmt in FORMATS:
        w, h = FORMATS[fmt]["size"]
        dirs = [d for f, d in OG_DIRS if f == fmt] or [os.path.join(SOCIAL, fmt)]
        files = []
        for d in dirs:
            pat = os.path.join(ROOT, d, "og-*.png" if "posts" in d else "*.png")
            files += sorted(glob.glob(pat))
        if not files:
            continue
        # Story is 16:9 tall - give it a narrower column so the grid stays sane.
        col = 190 if h > w else 300
        thumbs = "\n".join(
            f'<figure><img src="../{os.path.relpath(f, ROOT)}" loading="lazy">'
            f'<figcaption>{os.path.basename(f)}</figcaption></figure>'
            for f in files
        )
        out.append(
            f'<h3>{fmt} <span class="dim">{w}×{h} · {len(files)} cards</span></h3>'
            f'<div class="grid" style="--col:{col}px">{thumbs}</div>'
        )
    return "\n".join(out)


def main():
    print("Rebuilding site for the component scan...")
    rebuild_site()
    components = discover(CSS_PATH, SITE_GLOB, exclude=SITE_EXCLUDE)

    tokens = all_tokens()
    grad_rows = gradients(tokens)
    grad_section = f"""
<h2>Gradients</h2>
<div class="grads">
{grad_rows}
</div>
""" if grad_rows else ""

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Design system — aduttya.com</title>
<link rel="stylesheet" href="../style-warm.css">
<style>
  @font-face {{ font-family:'Archivo'; src:url('../assets/fonts/Archivo-Variable.ttf');
                font-weight:100 900; font-stretch:62% 125%; }}
  :root {{ color-scheme: light; }}
  body {{ padding:48px 40px 96px; }} /* base margin/colour/font come from style-warm.css itself */
  h1,h2,h3 {{ letter-spacing:.01em; font-weight:800; }}
  h1 {{ font-size:28px; margin:0 0 4px; }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.18em;
        color:{value('--orange')}; margin:56px 0 18px;
        border-bottom:1px solid {value('--bone-rule')}; padding-bottom:10px; }}
  h3 {{ font-size:14px; text-transform:uppercase; letter-spacing:.14em;
        margin:32px 0 12px; font-weight:700; }}
  .dim {{ opacity:.6; font-weight:400; letter-spacing:.06em; }}
  .lead {{ opacity:.7; margin:0 0 8px; font-size:14px; }}
  .sws {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:10px; }}
  .sw {{ display:flex; align-items:center; gap:10px; background:{value('--panel')};
         border:1px solid {value('--ink-veil')}; padding:8px 10px; border-radius:8px; }}
  .chip {{ width:34px; height:34px; flex:none; border-radius:6px;
           border:1px solid {value('--ink-veil')}; }}
  .sw code {{ font-size:12px; }}
  .sw span {{ margin-left:auto; font-size:11px; opacity:.6; }}
  .grads {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
  .band {{ height:64px; border:1px solid {value('--ink-veil')}; margin-bottom:6px; border-radius:8px; }}
  .grad code {{ font-size:12px; opacity:.6; }}
  table {{ border-collapse:collapse; font-size:13px; }}
  td {{ padding:6px 18px 6px 0; border-bottom:1px solid {value('--ink-veil')}; opacity:.75; }}
  td code {{ opacity:1; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(var(--col),1fr)); gap:16px; }}
  figure {{ margin:0; }}
  figure img {{ width:100%; display:block; border:1px solid {value('--ink-veil')}; border-radius:8px; }}
  figcaption {{ font-size:11px; opacity:.6; margin-top:6px; word-break:break-all; }}
  .type-row {{ margin:0 0 14px; }}
  .type-row span {{ display:block; font-size:11px; opacity:.6;
                    letter-spacing:.14em; text-transform:uppercase; margin-bottom:2px; }}
  .comp-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
                gap:{value('--gutter')}; margin-bottom:28px; }}
  .comp {{ border:1px solid {value('--ink-veil')}; border-radius:12px; overflow:hidden;
           background:{value('--bone')}; display:flex; flex-direction:column; }}
  .comp-head {{ display:flex; align-items:center; justify-content:space-between;
                padding:8px 12px; border-bottom:1px solid {value('--ink-veil')}; }}
  .comp-head code {{ font-size:12px; color:{value('--rust')}; }}
  .copy {{ font:inherit; font-size:11px; letter-spacing:.04em; cursor:pointer;
           background:{value('--panel')}; color:{value('--ink')}; border:0;
           border-radius:999px; padding:4px 10px; transition:background .2s {value('--ease')}; }}
  .copy:hover {{ background:{value('--orange')}; }}
  .comp-live {{ padding:22px; display:flex; align-items:center; justify-content:center;
                min-height:64px; max-height:320px; overflow:auto; }}
  .comp-src {{ margin:0; padding:12px 14px; background:{value('--ink')}; color:{value('--bone')};
               font-size:11px; line-height:1.6; overflow-x:auto; max-height:140px; overflow-y:auto; }}
  .comp-src code {{ font-family:'SF Mono','Fira Code',monospace; }}
</style></head><body>

<h1>Design system</h1>
<p class="lead">Generated from <code>style-warm.css</code> and the built site.
Rebuild with <code>python3 _scripts/make_preview.py</code>.</p>

<h2>Colour</h2>
<div class="sws">
{swatches(tokens)}
</div>
{grad_section}
<h2>Type</h2>
<div class="type-row"><span>--font · Archivo (variable, wdth/wght)</span>
  <div style="font-variation-settings:'wdth' 122,'wght' 780;font-size:34px">
    Headings, labels, nav, card eyebrows</div></div>
<div class="type-row"><span>--font · Archivo, regular weight</span>
  <div style="font-variation-settings:'wdth' 100,'wght' 420;font-size:19px">
    Body copy, post prose, subtitles and descriptions</div></div>

<h2>Components</h2>
<p class="lead">Every class below is lifted from real markup the built site currently
ships (see <code>_scripts/scan_components.py</code>) — nothing here is hand-typed, so a
class disappears from this page the moment nothing on the site uses it anymore. Hit
Copy for the exact source.</p>
{components_section(components)}

<h2>Other tokens</h2>
<table>{other(tokens)}</table>

<h2>Share cards</h2>
{cards_section()}

<script>
document.querySelectorAll('[data-copy]').forEach(function (btn) {{
  btn.addEventListener('click', function () {{
    var ta = btn.closest('.comp').querySelector('.comp-raw');
    navigator.clipboard.writeText(ta.value).then(function () {{
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () {{ btn.textContent = old; }}, 1200);
    }});
  }});
}});
</script>

</body></html>
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    n = len(tokens)
    print(f"{OUT}  ({n} tokens, {len(FORMATS)} formats)")


if __name__ == "__main__":
    main()
