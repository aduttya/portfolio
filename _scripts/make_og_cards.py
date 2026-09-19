#!/usr/bin/env python3
"""Generate share cards for every page and post, in every social format.

This file holds the *content*; _scripts/cards.py holds the layout engine and
style-warm.css holds the design. To change a colour edit style-warm.css, to
change a layout edit FORMATS in cards.py, to change what a card says edit the
lists below.

    python3 _scripts/make_og_cards.py                 # og only (default)
    python3 _scripts/make_og_cards.py --format all    # every format
    python3 _scripts/make_og_cards.py --format square,story
    python3 _scripts/make_og_cards.py --list          # show formats

Open Graph cards keep their existing paths because posts reference them in
front matter. Everything else lands in assets/images/social/<format>/.
"""
import argparse
import os
import sys

from cards import FORMATS, render, save

OG_OUT = "assets/images/og"
POST_OUT = "assets/images/posts"
SOCIAL_OUT = "assets/images/social"

# (name, eyebrow, title, subtitle)
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

POST_CARDS = [
    ("og-why-ai-wont-cite", "AEO Series · 1/8",
     "Why AI Won't Cite Your Content (And What to Fix)",
     "Your page can rank and still never appear in AI answers. Why AI "
     "retrieves but doesn't cite, and what actually fixes it."),
    ("og-text-embeddings", "AEO Series · 2/8",
     "Text Embeddings for AEO and SEO",
     "A practitioner's guide to how embeddings power AI answer engines, "
     "where they fail, and how to audit for it."),
    ("og-geo-aeo-strategy-shift", "AEO Series · 3/8",
     "GEO / AEO Strategy Shift",
     "Why renaming SEO metrics won't work: prompt volume, AI visibility, "
     "and attribution are all weaker signals than they look."),
    ("og-six-months-aeo-experiments", "AEO Series · 4/8",
     "Six Months of AEO Experiments",
     "What actually gets you cited in ChatGPT, AI Overviews, and "
     "Perplexity, versus what the AEO industry says you should do."),
    ("og-aeo-tracking-verification", "AEO Series · 5/8",
     "AEO Tracking Tells You If You're Winning, Not How to Win",
     "Most AEO tracking optimizes against unknown demand. Why GSC and "
     "Bing are the decision layer, and AEO tracking only verifies."),
    ("og-aeo-optimization-categories", "AEO Series · 6/8",
     "Categories I Check Before Trusting an AI Recommendation",
     "Nine categories cover almost every AEO/SEO fix. Why I still run "
     "every AI recommendation through them by hand."),
    ("og-seo-automation", "AEO Series · 7/8",
     "SEO Automation That Doesn't Hallucinate",
     "Most SEO automation generates plausible recommendations, not grounded "
     "ones. The architecture I use to tell them apart."),
    ("og-apex-insights-gt3", "AEO Series · 8/8",
     "I Tried to Make GT3 Easier to Understand, Then Google "
     "Started Finding Apex Insights",
     "A GT3 knowledge base with no backlinks started showing up across "
     "teams, championships, and races within weeks."),
]


def out_dir_for(fmt, is_post):
    """OG keeps its published paths; other formats get their own folder."""
    if fmt == "og":
        return POST_OUT if is_post else OG_OUT
    return os.path.join(SOCIAL_OUT, fmt)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--format", default="og",
                    help="comma-separated format names, or 'all' (default: og)")
    ap.add_argument("--list", action="store_true", help="list formats and exit")
    args = ap.parse_args()

    if args.list:
        for name, spec in FORMATS.items():
            w, h = spec["size"]
            print(f"{name:10} {w}x{h}")
        return 0

    names = list(FORMATS) if args.format == "all" else args.format.split(",")
    unknown = [n for n in names if n not in FORMATS]
    if unknown:
        print(f"unknown format(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"available: {', '.join(FORMATS)}", file=sys.stderr)
        return 1

    for fmt in names:
        for card in CARDS:
            save(render(fmt, *card[1:]), out_dir_for(fmt, False), card[0])
        for card in POST_CARDS:
            save(render(fmt, *card[1:]), out_dir_for(fmt, True), card[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
