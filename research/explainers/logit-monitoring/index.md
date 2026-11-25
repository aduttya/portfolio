---
layout: explainer
title: "What Is Logit Monitoring? Scoring What an LLM Never Says"
short: "What is logit monitoring?"
seo_title: "What Is Logit Monitoring? Scoring What an LLM Never Says (Interactive)"
description: "An interactive explainer on logit monitoring. See how researchers score a predefined sentence against a model's context without generating it, and how this is used to study evaluation awareness."
eyebrow: "Interactive explainer · 2 of 2"
lede: "Generation shows what a model wrote. Logit monitoring measures how likely it was to write something else. Score a sentence the model never writes, one token at a time."
teaches: "How the probability of a predefined token sequence is computed with teacher forcing, and how logit monitoring is used to study evaluation awareness"
date: 2026-11-25
og_image: /assets/images/og/explainer-logit-monitoring.png
og_image_alt: "What is logit monitoring? Scoring what an LLM never says"
next_url: /research/explainers/how-llms-generate-text/
next_label: "Start from the basics"
next_title: "What are logits? How LLMs choose the next token"
post_url: /blog/logit-monitoring-evaluation-awareness/
post_title: "What If We Could See What an AI Almost Said?"
---

In the [first explainer](/research/explainers/how-llms-generate-text/) the model picked a token from a probability distribution. Researchers can use that same distribution differently. Instead of letting the model choose, they **choose a sentence themselves** and ask how likely the model was to produce it.

Below, the model has been reasoning about a conversation. A researcher wants to know how likely it is to continue with *"the user is testing me"*. Score the sentence, then compare it with what the model actually wrote.

{% include viz/logit-explainer.html part="mon" %}

## How logit monitoring is used to study evaluation awareness

{% include viz/logit-explainer.html part="res" %}

## The research behind it

The approach comes from Santiago Aranguri's [Logits as a New Monitor for Evaluation Awareness](https://www.lesswrong.com/posts/PK7ZvFZxrgpYtrpF4/logits-as-a-new-monitor-for-evaluation-awareness-1) (June 2026). His logit monitor tracked the probability of *"The user might be testing"* across a model's chain of thought. It separated evaluation prompts from real-world prompts better than reading the model's written reasoning, and with far fewer rollouts. I go through the results, and the questions I'd still want answered, in the [full essay](/blog/logit-monitoring-evaluation-awareness/).
