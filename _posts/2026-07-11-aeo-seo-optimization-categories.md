---
layout: post
title: "The AEO/SEO Optimization Categories I Actually Check Before I Trust an AI Recommendation"
description: "Nine categories cover almost every AEO/SEO fix. Here's why I still run every AI-generated recommendation through them by hand — including a story about 150 internal-link suggestions, only 20 of which held up."
---

**You've probably seen the pattern by now.** Feed Claude your GSC data, ask it to churn through the numbers, get back a list of recommendations, apply them. It's become a default workflow for a lot of AEO/SEO work, and on the surface it looks fantastic. My experience running that workflow has been consistent enough that I want to share it before getting into what I actually check for.

---

## What happened when I cross-questioned it

I asked Claude to analyze a full website pages, content, structure and come back with sections where internal links should go, written so they'd read naturally rather than stuffed in. It came back with 150 recommendations. I asked if it was sure. It said it had full confidence.

I spent the next couple of days manually checking every one. **20 were decent enough to use.** I went back with that feedback, and it agreed called it overconfidence on its own part.

A separate case, same pattern: I wanted to work a keyword into a page, and asked for a recommendation. It suggested adding a new section, again with confidence. I opened a fresh session, gave it the same page, and asked a different question: does this section actually make sense for what the page is trying to do? Same model. It said no, and explained why.

I caught both of these because I already knew what right and wrong looked like — years of doing this manually before any of these tools existed. Now picture the same workflow running through an agent or a skill, unsupervised, at the scale of an entire site, with nobody in the loop who'd know a bad recommendation on sight.

That's the actual state of AEO tools that generate content recommendations and strategy right now: **they still have a long way to go, and the guardrail has to be a person who already knows the answer, not blind trust in the model's confidence.**

---

## The categories that actually cover AEO/SEO work

What that guardrail looks like in practice is a checklist a set of categories I run any recommendation through, whether it came from Claude, from an AEO tool's "content recommendations" feature, or from my own first instinct. Almost everything I do falls into one of nine categories, at three different scopes.

### Single-page fixes

**Rewrite the opening to lead with a direct answer.** Push the actual answer into the first few sentences instead of easing into it with throat-clearing. Both featured snippets and LLM extraction pull from the top of the content, not from context you set up three paragraphs in.

**Fix intent mismatch.** Check what query GSC actually associates the page with, and see if the content matches what that query implies. A comparison page reading as a how-to needs correcting toward the intent not more keywords layered on top.

**Expand thin topical coverage.** Add real depth where a page is superficial on something it should own. This is exactly where the keyword-and-new-section story above happened an AI recommendation to "expand" a page can just as easily mean adding a section that serves a keyword instead of the page's actual objective. Check the objective before you check the keyword.

**Add a structural FAQ section.** Not for the schema markup benefit alone FAQs earn their place when they answer questions people are genuinely asking, adjacent to the page's core topic. Manufactured questions built to hit a keyword don't count, no matter how confidently a tool suggests them.

### Page-boundary fixes

**Split a page serving two different intents.** When a page tries to answer both "what is X" and "how do I do X" at once and satisfies neither well, the fix isn't more content on the same page it's two pages.

**Merge pages that cannibalize each other.** Multiple pages competing for the same query dilute authority instead of concentrating it. Merge into whichever is the stronger asset.

**Create a dedicated page for a high-value topic buried in a broader page.** A subtopic pulling real demand on its own deserves its own page instead of staying a paragraph inside something else.

### Site-level structure

**Build a content cluster.** Connect a set of pages around a topic so they read as one coherent entity to Google, rather than shipping isolated pages. I've written about [how this played out at Flozi](/blog/aeo-tracking-verification-not-decisions/) in more detail.

**Strengthen internal linking.** The connective tissue that actually turns a set of pages into a cluster. This is also the category from the opening story 150 recommended links, 20 that held up. Internal linking is exactly where AI-generated recommendations sound most confident and need the most scrutiny, because "does this link make sense here" is a judgment call, not a lookup.

---

## Why the categories matter more than the tool

The value of having this list isn't that it replaces judgment it's that it gives you something concrete to interrogate a recommendation against. Before applying anything, whether it came from a model or a colleague: which category is this actually solving, and does the recommendation genuinely serve it, or does it just look like it does?

That question is the guardrail. Confidence from the tool isn't evidence. Checking against the category is.
