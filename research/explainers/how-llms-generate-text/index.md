---
layout: explainer
title: "What Are Logits? How LLMs Choose the Next Token"
short: "What are logits?"
seo_title: "What Are Logits? How LLMs Choose the Next Token (Interactive)"
description: "An interactive explainer on how a large language model picks its next token. Step through tokens, raw logits, softmax and temperature with worked numbers."
eyebrow: "Interactive explainer · 1 of 2"
lede: "A language model writes one token at a time. Step through a single prediction, from the prompt to the raw scores to the token it picks."
teaches: "What logits are, how softmax turns them into probabilities, and how a model selects its next token"
date: 2026-11-25
og_image: /assets/images/og/explainer-llm-generation.png
og_image_alt: "What are logits? How LLMs choose the next token"
next_url: /research/explainers/logit-monitoring/
next_title: "What is logit monitoring? Scoring what an LLM never says"
post_url: /blog/logit-monitoring-evaluation-awareness/
post_title: "What If We Could See What an AI Almost Said?"
---

When you ask a model *"What is the capital of France?"*, it doesn't look up an answer. It gives a score to every token it could write next, turns those scores into probabilities, and picks one. Then it does the same thing again with that token added to the context.

{% include viz/logit-explainer.html part="gen" %}

## How an LLM turns logits into the next token

1. **Tokens.** The prompt is split into tokens, the units the model reads and writes. Real tokenizers often split words into smaller pieces.
2. **Logits.** The model produces one raw score per candidate token. Logits are not probabilities. They can be negative, and only their relative size matters.
3. **Softmax.** Softmax turns the logits into probabilities that add up to 100%. With logits of 3.0, 1.0, 0.5 and −0.5, Paris ends up at 80.2%.
4. **Selection.** One token is chosen and added to the context, and the loop repeats until the model produces an end token.

## Why logits matter for AI safety research

The part that matters for safety research is step 3. The model assigns a probability to **every** possible continuation, not only to the one it ends up writing. That means you can ask how likely any particular sentence is, even one the model never writes. The next explainer shows how researchers do that.
