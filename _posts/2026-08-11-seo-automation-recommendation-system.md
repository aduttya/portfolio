---
layout: post
title: "SEO Automation That Doesn't Hallucinate: How to Build a Recommendation System You Can Trust"
description: "Most SEO automation generates plausible recommendations, not grounded ones. The architecture I use to tell them apart and why the language model gets exactly one job."
og_image: /assets/images/posts/og-seo-automation.png
og_image_alt: "Matrix of five growth questions against three data sources, showing that your own behaviour data structurally cannot answer the whitespace question"
---

**Most SEO automation generates recommendations. The hard part is knowing which ones are grounded in something real.**

Every AI SEO tool demo looks the same. You paste a URL and 10 seconds later you get 20 recommendations like Add an FAQ section, improve your internal linking, target these long-tail keywords, and rewrite this meta description.

Every one of them is plausible and that's the problem.

Plausible is what a language model is optimised to produce. If you ask a model to look at a page and suggest improvements, it will always suggest improvements for a perfect page, for a page it could not fetch, for a page that does not exist. There is no input for which the honest answer "I cannot tell you anything useful about this from what I can see" is a likely output, so you get twenty recommendations whether or not there are twenty problems, and nothing in the output tells you which ones came from evidence and which ones came from the model's sense of what SEO advice sounds like.

I have spent the last stretch building systems that produce SEO and AEO recommendations at scale. Most of the engineering effort did not go into generating recommendations. Generating them is trivial. It went into the machinery that decides which recommendations are allowed to exist.

This post is the architecture. Not the code, not the scoring weights, the design rules that make the difference between a system whose output you can hand to a client and a system that produces confident nonsense.

---

## Why do AI SEO tools produce untrustworthy recommendations?

The following three failure modes cover them:

### The model is doing the scoring

Ask an LLM to rank fifty pages by opportunity and it will hand you fifty numbers. Those numbers are not a calculation. They are a plausible-looking distribution. You cannot audit them, you cannot reproduce them, and if you rerun the same input tomorrow you will get a different order. Ranking is arithmetic and arithmetic does not belong in a language model.

### The system is shaped like its data source, not like the question

Most tools are built as "a Search Console tool" or "a rank-tracker tool," so every problem gets bent into the shape of the data they hold. This is the failure people notice last, because within the boundaries of that one source everything works. The boundary is where it breaks and Search Console has a hard one I will come back to in a minute.

### The output is a label, not a fix

"Intent mismatch on 14 pages." "CTR gap detected." Fine, but now a human has to open each page, work out what the actual problem is, and write the actual replacement. The tool has moved the work around rather than doing it. A category name is not a deliverable.

Fixing all three is mostly a matter of deciding, up front, which parts of the system are allowed to be judgment and which parts have to be arithmetic and then never letting those two mix.

---

## Start with growth questions, not with the data you happen to have

The first design decision is what the system is organised around. Almost everyone organises around data sources. I organise around questions, and let each question route to whatever source can actually answer it for this particular site.

There are five questions, and between them they cover essentially every reason organic performance is not where it should be:

1. **Whitespace:** Is there real search demand we are not capturing at all?
2. **Winnability:** Of that demand, what can we realistically rank for, given who currently holds those results?
3. **Positioning:** Of what we already have, is it aimed at the demand that actually exists?
4. **Click and conversion:** When we do show up, do people click, and when they click, do they do the thing the business needs?
5. **Technical:** Is anything mechanically blocking all of the above?

The value of framing it this way shows up immediately, in a place most tools get wrong.

**Search Console cannot answer question one. Not with better access, not with a longer date range, not ever.** It reports queries where your site already earned impressions. Demand you have never shown up for produces no impressions, so it produces no rows. A topic your entire category ranks for and you have never touched is, from Search Console's point of view, indistinguishable from a topic nobody searches for, both are absent.

This is a structural blind spot, not a data-volume problem, and it is why "we have great Search Console data" is not the same as "we know where our growth is." Answering the whitespace question requires a market-visibility lens, keyword databases, competitor visibility data, at minimum the free demand signals in autocomplete and People Also Ask. If your system is built as a Search Console tool, it will never ask the question, and its silence will look like an answer.

![Matrix of five growth questions against three data sources, showing that your own behaviour data structurally cannot answer the whitespace question](/assets/images/posts/diagram-1-which-source-answers-which-question.svg)
<p class="img-caption">Each growth question routes to whatever source can actually answer it. Your own behaviour data is the best source for three of the five questions — and completely blind to the first one.</p>

One more thing the question framing gets you is the right running order, which is not fixed. For a site with years of history, positioning and conversion fixes come first because they are evidenced, cheap, and fast. For a new site with nothing to fix, whitespace and winnability come first, because the question is what to build at all. Same five questions, different sequence, and a system that hard-codes one order is wrong for half the sites it sees.

---

## Give the model exactly one job

In a well-built recommendation system, the language model does far less than people expect.

Here is the split I use:

### Mechanical: no model involved

- Aggregating performance data
- Ranking pages against the site's own distribution
- Computing benchmarks
- Flagging gaps
- Comparing expected intent against observed intent
- Scoring opportunity
- Merging findings into one record per page

All of it is arithmetic and lookups. All of it is reproducible, auditable, and free.

### Model, narrowly scoped

One genuine judgment call, plus drafting.

The judgment call is this: *does this page's content actually mean what its incoming queries suggest it means?* That is a semantic question about meaning and audience. No formula can answer it. A page can be well-written, fast, and well-linked, and still be built for an audience entirely different from the one arriving on it and if that is true, every other optimisation is polishing the wrong thing, so it gets checked first, before anything else is scored.

The drafting job is the second one: once a mechanical process has already established that a specific page has a specific grounded problem, the model writes the actual replacement text. Not "improve the title" and then the title.

Notice what is missing. The model does not decide which pages matter, does not rank anything, and does not decide that an opportunity exists. That constraint is doing enormous work: the system cannot invent an opportunity out of nothing, because the only path to a recommendation runs through a number that came from real data.

![Six-stage recommendation pipeline where only two stages use the language model, followed by a grounding check that either emits a concrete fix or emits nothing](/assets/images/posts/diagram-2-where-the-model-is-allowed-in.svg)
<p class="img-caption">The model touches two of six stages. Everything that decides what matters happens before it, and the grounding check after it can throw the output away.</p>

This is where most implementations quietly cheat. Comparing two pieces of content, is our page thinner than the competitor's? tempts you to ask the model. Do not: use mechanical proxies like heading count and distinct subtopics covered. Cruder, but "the model thought their page was more thorough" is not a finding you can put in front of a client who disagrees.

---

## Tag every finding with where it came from

This is the single highest-leverage design decision in the whole architecture, and almost nothing on the market does it.

Every finding the system emits carries a provenance tag, and the tag is visible in the final output:

| Tag | What it means | Example |
|---|---|---|
| **Observed** | Real, first-party measured behaviour | Actual clicks, impressions, conversions from your own properties |
| **Modeled** | A third party's estimate of a real quantity | Search volume, estimated difficulty, rank-tracker position |
| **Structural** | A mechanically verified fact about the page | A duplicate title exists; the H1 is missing; a live check confirms an AI Overview is present for this query right now |
| **Hypothesis** | The model's read, unconfirmed against real behaviour | "This page's content reads as informational, but its incoming queries read as transactional" |

The reason this matters is that these four things get treated as interchangeable everywhere else in the industry, and they are not remotely equivalent. Observed behaviour is what actually happened. A modeled search volume is a vendor's estimate with error bars nobody shows you. A hypothesis is a plausible story.

So **first-party observed behaviour is always the final word on whether a real problem exists.** Third-party data never gets that authority. It has exactly three legitimate jobs:

1. Finding things your own data structurally cannot see.
2. Sanity-checking whether a guessed explanation is even plausible.
3. Providing a directional competitive benchmark when nothing better exists.

Directional. Never definitive.

There is a fifth category I had to add after testing, and it is worth flagging because it will bite anyone building for AEO. Text pulled out of a live AI Overview is not observed behaviour and not a vendor estimate. It is other websites' unverified marketing claims, laundered through a generative summary into something that reads like a neutral source. It is legitimate to record that the text was shown. It is not legitimate to treat it as guidance about what is true or what you should say. I keep it as a structural fact at most.

The practical consequence: **never blend provenance tiers into one number.** A modeled whitespace opportunity and an observed conversion leak are not comparable on a single score, and forcing them onto one is false precision that hides exactly the information the user needs. Segment the output instead, into content opportunities, repositioning fixes, conversion fixes, and technical blockers. Each list internally comparable, each line carrying its tier.

---

## Every output is a fix, not a label

The rule I hold hardest: the system never hands back a category and leaves the human to work out what to do about it. What that looks like in practice:

- **A page has a click-through gap.** The output is the proposed title and meta description text, grounded in the page's actual current title, actual current meta, and the actual phrasing of the query it is meant to win.
- **A page is close to the first page but not on it.** The output names the specific subtopics its current content does not cover, and the specific internal links to add, with anchor text.
- **Pages are competing with each other.** The output names which page survives, and what unique material to preserve from the others before merging.

Underneath that sits the grounding constraint, which is what stops the whole thing collapsing back into plausible nonsense: **every fix must quote the fetched facts it is revising.** The real title, the real queries, verbatim. If those facts could not be fetched, whether because the crawl failed or because the query data was too thin, the system is required to say *not computable from available data* and produce nothing.

That last part is the expensive one to build and the whole reason the output is worth anything. A model asked to write a better title with no page content will write one. It will read fine. It will be about a page that does not exist. The only defence is a hard structural rule that no fix is emitted unless its grounding facts are present.

An honest "not computable" beats a guessed recommendation every time. It is also the most reliable way to tell a real system from a demo: ask it about a page it cannot access, and see whether it admits it.

---

## Degrade gracefully, upgrade automatically

Real sites have ragged data. A new site has no meaningful search history, a website owner will not always have analytics wired up, and some engagements have a budget for paid data and some do not. The wrong response is a tool that only works on well-instrumented sites. The right response is capability detection: before anything runs, establish what actually exists for this site, and route each of the five questions to the best available source for *this* run.

Every question still produces an answer: a weaker answer, correctly labelled as weaker, but never a blank. And because provenance is already tagged, the upgrade path is free: when better data arrives, observed values override modeled ones on the next run and the confidence tier rises by itself. No redesign. The same five questions just get better inputs over time.

The one place this genuinely strains is winnability. Assessing competitive strength across a large keyword set without paid data does not scale the way the other four fall back. You can spot-check a handful of results by hand, but you cannot do it for a thousand. It is worth naming that honestly rather than pretending the fallback is equivalent. Every architecture has one load-bearing dependency; that is mine.

---

## The practitioner's layer: how it actually runs

For anyone building SEO automation of their own, the three parts that took the longest to get right:

### Assign expected purpose per page, before looking at performance data

What a page is *for* does not depend on which queries happen to land on it this month, so it is never recomputed. Obvious cases go by URL pattern; ambiguous ones get a single batched model call. This is what makes the later mismatch check a plain comparison instead of another judgment call.

### Take thresholds from the site's own distribution, never a constant

Which pages count as high-priority, and what a normal click-through rate looks like at a given position, are both computed from this site's own data, segmented by position and page purpose. An industry-average benchmark carried in from another project is worse than no benchmark, because it produces confident findings about problems that do not exist. Keep an absolute floor underneath so a page cannot look important purely by being the tallest thing in an empty room.

### Gate the expensive steps behind the cheap ones

The model call and the paid data call are the only parts that cost real money per page. So everything mechanical runs first, and only pages that clear a volume-and-symptom threshold get either: flagged pages only, never a sitewide sweep, and data already fetched for one purpose gets reused rather than re-fetched. One model call per page rather than a batch keeps the reasoning focused on a single page's evidence and makes the run resumable when something fails halfway through. This is not housekeeping: cost discipline is what decides whether the system is economically viable to run every month, and a system you can only afford to run once is a consulting deliverable, not automation.

---

## The test

Here is the question I would ask of any AI SEO tool, including mine.

**If you removed the language model entirely, would anything be left?**

If the answer is no, if the model is what finds the opportunities, ranks them, and decides they are worth doing, then what you have is a system that generates plausible SEO-shaped text, and its accuracy is not something you or anyone else can measure.

If the answer is yes, if underneath there is a set of grounded findings, computed mechanically, tagged with where they came from, and the model's job is the narrow interpretive work and the writing, then you have a system whose recommendations can be checked, argued with, and proven wrong. Which is the only kind worth acting on.

The AI is not the product. The grounding is the product. The AI is how you get from a grounded finding to something a person can actually go and do on Monday.

---

*Related: [The AEO/SEO optimization categories I actually check before I trust an AI recommendation](/blog/aeo-seo-optimization-categories/) · [AEO tracking tells you if you're winning, not how to win](/blog/aeo-tracking-verification-not-decisions/) · [Six months of AEO experiments: what actually gets you cited](/blog/six-months-of-aeo-experiments/)*
