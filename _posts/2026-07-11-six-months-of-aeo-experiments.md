---
layout: post
title: "Six Months of AEO Experiments: What Actually Gets You Cited"
description: "Six months of hands-on AEO testing at Flozi. What works, what doesn't, and why most advice skips the one variable that determines everything: whether you can win the gap at all."
---

**From the last six months I have been doing** testing what actually gets a page cited in ChatGPT, Google AI Overviews, and Perplexity, versus what the AEO industry insists you should be doing. The two lists don't overlap much.

**The tactics getting sold right now:**

- Answer-first paragraphs
- FAQ schema
- Tables
- Question-phrased headings

**What you should actually be looking for:**

- Can the page get indexed?
- Does it match the intent Google thinks it should serve?
- Is there actually room to win the topic at all?

Get those wrong and no amount of schema saves you.

---

## Fundamentals aren't the ranking factor anymore, they're the eligibility filter

Technical SEO used to be a ranking lever. It still matters, but its job has changed: it's no longer what pushes you up, it's what determines whether you're in the pool at all. If a page isn't indexed, it doesn't exist for an AI engine either there's nothing for retrieval to find.

You can verify this yourself in about ten seconds:

> Take a URL that isn't indexed. Put it in ChatGPT, with web search on tell it to use this page only to answer and ask a question.

It won't be able to, because there's nothing to retrieve. AI answer engines aren't a parallel discovery system with their own crawl and their own judgment of your site. Most of them are still downstream of the same index Google and Bing already built. Skip the fundamentals and you've disqualified yourself before any AEO tactic gets a chance to matter.

---

## Once you're indexed, check what Google thinks the page is *for*

Getting indexed isn't the finish line, it's where the real diagnostic starts. The next question is whether Google's understanding of the page matches the intent you wrote it for.

This can be directly checked in Google Search Console: look at the queries a given page is actually getting impressions for. If you wrote a comparison page and GSC shows it ranking for how-to queries, that's not a fluke, it's Google telling you it read the page differently than you intended.

At that point you have two options, and which one is right depends on the data:

- **Wait**: sometimes Google needs more signal (more time, more links, more content maturity) to re-classify a page correctly.
- **Change the page**: if the mismatch is structural (the content genuinely reads like a how-to even though you meant it as a comparison), no amount of waiting fixes it. You have to rewrite toward the intent you want recognized.

Guessing which one applies without checking GSC first is how people waste months "waiting" on a page that was never going to reclassify itself.

---

## Competition decides whether you can win at all and this is the part most AEO advice skips

Here's the variable that actually explains most of the variance in my results: how much competition exists for the gap you're trying to fill.

Two examples from the same six months, same fundamentals discipline applied to both:

**Webflow, via Flozi.** I found a Webflow-related topic with essentially no real competition in Bing Webmaster Tools terms low-authority pages, thin content, nobody had built a proper cluster around it. I published against that gap. It ranked in both Google AI Overviews and ChatGPT within a week, and it's still holding.

**AEO itself.** Same process gap analysis, content cluster, fundamentals solid applied to AEO as a topic. No traction yet. Not because the content or the fundamentals were weaker, but because everyone doing AEO work right now is writing about AEO. It's the most contested topic in its own niche.

Same playbook, opposite outcomes, because the one input that changed was competitive density. If the gap isn't there, execution quality doesn't buy you a win it just makes you the best-written entry in a pile nobody's citing yet.

---

## What actually worked

Strip it down and the pattern across six months is consistent:

1. **Identify a real gap**, not "low competition" as a vibe, but check thin or absent content, low-authority incumbents, a query cluster nobody's built for.
2. **Build a content cluster around it**, not a single page hoping to win alone.
3. **Make the content genuinely good**, on top of fundamentals that are already solid (indexed, correctly classified, matching intent).

None of that is a formatting trick. It's selection and execution, in that order.

---

## What didn't move anything on its own

These are the tactics that dominate AEO advice right now:

- Putting the answer in the first block
- Schema markup and FAQ blocks
- Tables and lists
- Chunking content into discrete sections
- Headings phrased as questions

I tested all of them. None of them got a page cited that wasn't already winnable on fundamentals and competition. They're not useless, they're **multipliers on content that's already good, sitting on a gap that's already winnable.** Applied to weak content in an already-contested niche, they do nothing, because they were never the bottleneck.

The AEO advice industry has a structural incentive to sell these. They're:

- Concrete
- Easy to productize
- Easy to check off

"Add FAQ schema" is a task. "Find a topic with no real competition and build a cluster around it" is judgment, and it's a lot harder to sell as a checklist.

---

## The actual order of operations

If I had to conclude my experience into one sequence:

1. Indexed?
2. Intent-matched?
3. Is there a winnable gap?
4. Build the cluster
5. Then worry about formatting

Most AEO content skips straight to the last step. That's backwards. Formatting is real, but it's the smallest lever in that chain and it's the only one getting sold as the whole strategy.
