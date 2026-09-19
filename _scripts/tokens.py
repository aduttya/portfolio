#!/usr/bin/env python3
"""Read the site's design tokens straight from style-warm.css.

style-warm.css `:root` is the single source of truth for the design system.
Nothing here redefines a colour - this module just parses that block so image
generators (OG cards, social banners) render with the same values the site
uses. Change a token in style-warm.css and everything downstream follows.

    from tokens import rgb, stops, value

    rgb("--orange")          -> (250, 102, 20)
    value("--font")          -> "'Archivo', system-ui, ..."
"""
import os
import re

CSS = os.path.join(os.path.dirname(__file__), os.pardir, "style-warm.css")

_NAMED = {"black": "#000000", "white": "#ffffff", "transparent": "#00000000"}


def _load():
    with open(CSS, encoding="utf-8") as fh:
        css = fh.read()
    block = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    if not block:
        raise RuntimeError(f"no :root block found in {CSS}")
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block.group(1)))


_TOKENS = _load()


def value(name, _depth=0):
    """Resolved token value, with any nested var() references expanded."""
    if name not in _TOKENS:
        raise KeyError(f"{name} is not defined in style.css :root")
    raw = _TOKENS[name]
    if _depth > 10:
        return raw
    return re.sub(
        r"var\((--[\w-]+)\)",
        lambda m: value(m.group(1), _depth + 1) if m.group(1) in _TOKENS else m.group(0),
        raw,
    ).strip()


def hex_to_rgb(text):
    """'#f97316' or '#fff' -> (249, 115, 22). Also accepts rgb()/rgba()."""
    text = _NAMED.get(text.strip().lower(), text.strip())
    m = re.match(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)", text)
    if m:
        return tuple(round(float(g)) for g in m.groups())
    h = text.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) not in (6, 8):
        raise ValueError(f"cannot read a colour from {text!r}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb(name):
    """A colour token as an RGB tuple, ready for Pillow."""
    return hex_to_rgb(value(name))


def stops(name):
    """Gradient token -> [(position 0-1, rgb), ...] in declared order.

    Positions come from the CSS percentages. A stop without one is spread
    evenly between its neighbours, matching how browsers fill the gaps.
    """
    text = value(name)
    inner = text[text.index("(") + 1:text.rindex(")")]

    # Split on commas that aren't inside a nested function call.
    parts, depth, buf = [], 0, ""
    for ch in inner:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)

    out = []
    for part in parts:
        part = part.strip()
        m = re.match(r"(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\))\s*([\d.]+)?%?", part)
        if not m:
            continue  # geometry prefix, e.g. "120% 85% at 50% 0%" or "160deg"
        pos = float(m.group(2)) / 100 if m.group(2) is not None else None
        out.append([pos, hex_to_rgb(m.group(1))])

    if not out:
        raise ValueError(f"{name} has no colour stops")

    # Fill implicit positions: ends anchor to 0 and 1, gaps divide evenly.
    if out[0][0] is None:
        out[0][0] = 0.0
    if out[-1][0] is None:
        out[-1][0] = 1.0
    i = 0
    while i < len(out):
        if out[i][0] is None:
            j = i
            while out[j][0] is None:
                j += 1
            lo, hi = out[i - 1][0], out[j][0]
            for k in range(i, j):
                out[k][0] = lo + (hi - lo) * (k - i + 1) / (j - i + 1)
            i = j
        i += 1

    return [(p, c) for p, c in out]


def font_stack(name):
    """Font token -> list of family names, quotes stripped."""
    return [f.strip().strip("'\"") for f in value(name).split(",")]


def all_tokens():
    """Every token name mapped to its resolved value."""
    return {k: value(k) for k in _TOKENS}


if __name__ == "__main__":
    for k, v in all_tokens().items():
        print(f"{k:22} {v}")
