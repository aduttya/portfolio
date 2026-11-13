---
layout: post
title: "AEO Needs to Move Beyond Queries"
seo_title: "AEO Needs to Move Beyond Queries"
description: "AI search turned searching into a conversation, but AEO still tracks queries like blue links. Why I'm moving from queries to conversational touchpoints."
og_image: /assets/images/posts/og-aeo-beyond-queries.png
og_image_alt: "AEO Needs to Move Beyond Queries"
---

**AI search turned searching into a conversation. Most of how we do AEO still treats it like a list of queries.**

Think about how Google used to work. You asked something, and it gave you websites. Some were blogs, some were forums, some were Reddit threads or Quora discussions, and you went from one to the next to piece the answer together.

AI mode puts all of that under one roof. The information you used to get from blogs, the back and forth you used to get from forums, the opinions you used to get from Reddit, all of it now sits inside one interface, and you get to it by having a conversation.

That changes more than the interface. It changes what we're actually optimizing for.

---

## Discovery and conversion

I split AI search work into two parts.

1. **Discovery** is showing up in AI answers in the first place
2. **Conversion** is turning that presence into leads

This post is about discovery. Conversion deserves its own post, and I'll get to it separately.

---

## How discovery used to work

For classic search, the discovery loop was clear.

1. Open Google Search Console
2. Find the queries you're getting impressions for, or should be
3. Optimize the existing page for them, or create a new page where one is missing
4. Watch the page climb

It worked because the end goal was simple. Get the page to rank for the query. And the query in GSC was, more or less, what a person had actually typed.

---

## What changes in a conversation

In a conversation, the user doesn't write the search queries anymore. The model does.

The user types a message, the model reads it alongside everything said earlier, and then it [fans out into its own searches](/blog/aeo-tracking-verification-not-decisions/) to find sources. Those searches are shaped heavily by the context of the conversation, and that context varies a lot.

Here's an example of how that plays out.

1. Someone says they're moving their site to Webflow
2. They ask how to keep their rankings during the move
3. Then they ask "does it handle redirects?"

That last message has no keyword in it. But the search the model runs carries everything from before it, something like *webflow 301 redirects site migration SEO*. The user never typed that.

And it isn't stable. The same person, on a different day, starting from a different first question, ends up generating totally different searches for the same need.

---

## Tracking hasn't caught up

Now look at how AEO is tracked today. GSC, Bing Webmaster Tools' AI reporting, and most third party AEO tools all report on queries. They're longer and more intent shaped than classic keywords, but they're still queries, and they're presented the way blue links were.

So the objective quietly stays the same as before. Show up for the query. Except in a conversation, the query is something the end user never searched.

I've argued before that [GSC and Bing should be the decision layer](/blog/aeo-tracking-verification-not-decisions/), not prompt tracking tools. I still think that's right for search. What I've come to see is that it doesn't tell me where I'm missing inside a conversation, and that's the gap I keep running into.

---

## Prompt tracking isn't the answer either

The obvious reaction is to track prompts instead of queries. I don't think that works, for the reasons I gave in [the GEO/AEO strategy post](/blog/geo-aeo-strategy-shift/). Prompts are infinite, you can't observe real ones, and every answer is a single sample from a generative system.

Dan Petrovic at DEJAN published [a clear piece on this](https://dejan.ai/blog/prompt-tracking/) that lands in the same place. Their view is that prompts are endless variations of a canonical core intent, and that you can't reproduce real multi turn context or personalization from the outside. So instead of tracking prompts, they track the core entity, something like "running shoes". They send it to Google, OpenAI and Anthropic models with one fixed probe and sample it many times. Because the wording never changes, any movement in a brand's share comes from the model or from the web results it retrieved.

I agree with the diagnosis, and one line from that piece stuck with me.

> The fanout queries bring the grounding context to the model, and the prompt does not.

Where I land differently is on what problem we're each solving. A canonical entity probe is a measurement instrument, and they're upfront that it isn't how people search or what chat sessions look like. It's very good at telling you whether an experiment moved the model.

My problem sits before measurement. I need to find *where in a conversation* a site should show up and isn't. Collapsing the conversation into one entity removes the very thing I'm trying to understand.

---

## Conversational optimization

So for now I'm calling this **conversational optimization**. It means optimizing for the points in a conversation where the model goes to the web and picks sources, rather than for individual queries or individual prompts.

I call those points **touchpoints**. A touchpoint is a stage of a conversation, about a particular topic, where retrieval happens and someone's page gets selected.

The work breaks into three problems.

1. **Find the touchpoints** where a site needs to show up
2. **Fix the pages** that should be showing up at those touchpoints and aren't
3. **Track progress** in a way that reflects conversations, not blue links

None of these are solved. Here's how I'm approaching them.

---

## How I'm approaching it

**1. Map conversation paths, not prompts.** Instead of a list of standalone prompts, I write out the paths a real person moves through. Orientation first, then options, then comparison, then specifics. You can't reproduce someone's history, location or personalization. But you *can* reproduce what was said earlier in the conversation, and that's the context that shapes the fanouts.

**2. Capture the fanouts at every turn.** Some models expose the searches they ran and the sources they used. Running a scripted path turn by turn shows what gets searched at each stage. Each path gets run more than once, because one answer is one sample.

**3. Group fanouts into touchpoints.** This is the part I most want to test. My hypothesis is that the wording of fanouts changes on every run, but at each stage of a conversation they settle on a stable set of intents and topics. If that holds, touchpoints are trackable even though prompts aren't.

**4. Map page coverage per touchpoint.** For each touchpoint, the site falls into one of three states.
- There's no page for it
- There's a page, but it isn't selected
- The page is selected

These need very different work. The first is a content gap. The second is a page that exists but isn't good enough, clear enough or trusted enough to be picked over whoever is winning that touchpoint.

**5. Track over time with fixed paths.** Rerun the same conversation scripts on a schedule, borrowing the fixed wording principle from DEJAN's approach but applying it to conversations instead of single entities. Then check the results against what Bing and GSC show happening in the real world.

This also explains why [connected libraries](/blog/aeo-tracking-verification-not-decisions/) have worked better for me than single keyword pages. A single page catches one moment in a conversation. A library can be there across the whole path.

---

## Where I'm testing it

I'm running this on [Apex Insights](/blog/gt3-knowledge-base-seo-apex-insights/), the GT3 knowledge base I've been building. It suits this well because it's built around connected entities like championships, teams, drivers, cars and manufacturers, and a fan's conversation naturally moves between them. Someone asks what GT3 is, then which series to follow, then about a team, then who drives for them.

I'll share what comes out of it once there's enough to say something real.

---

## What I don't know yet

- Whether touchpoints are stable enough to track, or whether they shift as much as prompts do
- How many conversation paths it takes to cover a topic properly
- How touchpoints connect to conversion, which is where the next post picks up

What I am sure of is that the conversation is now the unit of search, and query level tracking is describing a world that's fading. I'd rather work out how to measure the new one, even roughly, than keep optimizing for searches nobody typed.
