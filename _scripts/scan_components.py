#!/usr/bin/env python3
"""Derive a component catalogue from the site's own CSS and built HTML.

Nothing here is hand-typed. It reads every class the stylesheet defines
(grouped by the file's own `/* ── Section ── */` comments), then scans the
*built* HTML for the first real element that uses each class and lifts its
exact source markup - so the catalogue can never list a component that
doesn't actually exist, and never show a class with invented example markup.

Porting this to another project: point CSS_PATH at that project's token
stylesheet and HTML_GLOB at its built output (this file has no other
Jekyll- or project-specific assumptions - it only needs class="..."
attributes and CSS rules that open with `.classname {`).

    from scan_components import discover
    discover(css_path, html_glob)  ->  [{"section", "cls", "html"}, ...]
"""
import glob
import os
import re
from html.parser import HTMLParser

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

# A component's markup should be small enough to actually copy into another
# project. Past this, a class is describing a whole page section (real hero
# copy, a full nav, a bio paragraph) rather than a reusable piece.
MAX_SNIPPET_CHARS = 400

# Pure layout plumbing - grid-span utilities and a generic grid wrapper -
# rather than anything you'd recognize or reuse as "a component".
SKIP_CLASSES = {"sheet", "c-4", "c-5", "c-6", "c-7", "c-8", "c-12", "settle"}

SECTION_RE = re.compile(r"/\*\s*──+\s*(.+?)\s*──+\s*\*/")
RULE_RE = re.compile(r"([^{}]+)\{")
CLASS_RE = re.compile(r"\.([A-Za-z][\w-]*)")


def classes_by_section(css_text):
    """[(section, class_name), ...] in the order the stylesheet defines
    them, deduped to each class's first appearance."""
    sections = [(m.start(), m.group(1).strip()) for m in SECTION_RE.finditer(css_text)]

    def section_at(pos):
        name = None
        for start, sec in sections:
            if start <= pos:
                name = sec
            else:
                break
        return name

    def section_for(m):
        # RULE_RE's `[^{}]+` happily spans a section comment sitting between
        # the previous rule's `}` and this one's selector - so the nearest
        # comment *inside* this match wins over whatever preceded the match.
        embedded = [s for s in sections if m.start() <= s[0] < m.end()]
        return embedded[-1][1] if embedded else section_at(m.start())

    ordered, seen = [], set()
    for m in RULE_RE.finditer(css_text):
        selector = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
        sec = section_for(m)
        for cm in CLASS_RE.finditer(selector):
            cls = cm.group(1)
            if cls in seen:
                continue
            seen.add(cls)
            ordered.append((sec, cls))
    return ordered


class SnippetFinder(HTMLParser):
    """One pass over a document, lifting the first real element for every
    wanted class still outstanding. Classes are matched by the document's
    open/close nesting depth, not by regex, so a snippet always closes on
    the tag that actually closes it - including when several wanted
    classes share one element (`class="btn btn-quiet"`)."""

    def __init__(self, source, wanted):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.wanted = set(wanted)
        self.found = {}
        self._line_offsets = self._compute_line_offsets(source)
        self._depth = 0
        self._active = {}       # depth -> [class, ...] captured starting there
        self._active_start = {}  # depth -> start char offset

    @staticmethod
    def _compute_line_offsets(text):
        offsets, pos = [0], 0
        for line in text.splitlines(keepends=True):
            pos += len(line)
            offsets.append(pos)
        return offsets

    def _offset(self):
        line, col = self.getpos()
        return self._line_offsets[line - 1] + col

    def _pending_classes(self):
        pending = set()
        for cs in self._active.values():
            pending.update(cs)
        return pending

    def _begin(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        remaining = self.wanted - self.found.keys() - self._pending_classes()
        hits = remaining.intersection(classes)
        if hits:
            self._active.setdefault(self._depth, []).extend(hits)
            self._active_start[self._depth] = self._offset()

    def handle_starttag(self, tag, attrs):
        self._begin(tag, attrs)
        if tag not in VOID:
            self._depth += 1

    def handle_startendtag(self, tag, attrs):
        # explicit self-close, e.g. <img ... />
        depth_before = self._depth
        self._begin(tag, attrs)
        if depth_before in self._active and depth_before in self._active_start:
            start = self._active_start.pop(depth_before)
            end = start + len(self.get_starttag_text())
            for cls in self._active.pop(depth_before):
                self.found.setdefault(cls, self.source[start:end])

    def handle_endtag(self, tag):
        if tag not in VOID:
            self._depth -= 1
        if self._depth in self._active:
            start = self._active_start.pop(self._depth)
            close = self.source.index(">", self._offset()) + 1
            for cls in self._active.pop(self._depth):
                self.found.setdefault(cls, self.source[start:close])


def discover(css_path, html_glob, exclude=()):
    """Every (section, class, snippet) the stylesheet + built HTML agree on.

    `exclude` filters built-output paths that aren't real design-system
    pages (a generated directory index, an internal notes page, ...).
    """
    with open(css_path, encoding="utf-8") as fh:
        wanted = [(sec, cls) for sec, cls in classes_by_section(fh.read())
                  if cls not in SKIP_CLASSES]

    files = sorted(
        f for f in glob.glob(html_glob, recursive=True)
        if not any(ex in f for ex in exclude)
    )

    snippets = {}
    remaining = {cls for _, cls in wanted}
    for path in files:
        if not remaining:
            break
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        finder = SnippetFinder(source, remaining)
        finder.feed(source)
        for cls, html in finder.found.items():
            if len(html) <= MAX_SNIPPET_CHARS:
                snippets[cls] = {"html": html, "source": os.path.relpath(path)}
        remaining -= finder.found.keys()

    return [
        {"section": sec, "cls": cls, **snippets[cls]}
        for sec, cls in wanted
        if cls in snippets
    ]


if __name__ == "__main__":
    root = os.path.join(os.path.dirname(__file__), os.pardir)
    results = discover(
        os.path.join(root, "style-warm.css"),
        os.path.join(root, "_site", "**", "*.html"),
        exclude=("/IDEAS/", "/assets/"),
    )
    by_section = {}
    for r in results:
        by_section.setdefault(r["section"], []).append(r["cls"])
    for sec, classes in by_section.items():
        print(f"{sec or '(none)'}: {', '.join(classes)}")
    print(f"\n{len(results)} components found")
