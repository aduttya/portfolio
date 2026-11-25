---
layout: post
title: "What If We Could See What an AI Almost Said?"
seo_title: "What Are Logits? Logit Monitoring and Evaluation Awareness Explained"
description: "Exploring logits, evaluation awareness, and a different way of thinking about human-AI interaction safety."
date: 2026-11-25 00:00:01
series: ai-safety
og_image: /assets/images/posts/og-logits-evaluation-awareness.png
og_image_alt: "What If We Could See What an AI Almost Said?"
---

When we interact with an AI model, we usually judge it by what it tells us. We write a prompt, receive an answer, and decide whether the answer is useful, accurate, or safe.

An AI model doesn't simply retrieve an answer and display it. It processes tokens, calculates probabilities, and generates a response one token at a time. At every step, there are multiple possible continuations, each with a different probability.

We see the continuation the model generates. We rarely think about the alternatives. That question led me to a concept I hadn't explored before, logits.

## First, what are logits?

Imagine asking an AI, *"What is the capital of France?"*

Before generating its answer, the model calculates numerical scores for possible next tokens. For simplicity, imagine its probabilities across four candidates look something like this.

| Next token | Probability |
|---|---:|
| Paris | 80.2% |
| London | 10.8% |
| Berlin | 6.6% |
| Rome | 2.4% |

These probabilities come from **logits**, which are the raw scores produced by the model before they are converted into probabilities. The model selects a token and repeats the process using the updated context.

What interested me wasn't just how this works. It was what researchers could do with these probabilities. Instead of observing only what a model generates, could we investigate what it considers likely to generate, even when it never actually produces those words?

I built two small interactive explainers for both halves of that idea. The first shows how a model generates text. The second shows how a researcher can score a sentence the model never writes.

{% include viz/explainer-cards.html %}

## A research paper that made this interesting

I came across a LessWrong post by Santiago Aranguri, [Logits as a New Monitor for Evaluation Awareness](https://www.lesswrong.com/posts/PK7ZvFZxrgpYtrpF4/logits-as-a-new-monitor-for-evaluation-awareness-1), published on 4 June 2026.

The research explores a problem called **evaluation awareness**. Imagine testing an AI model for safety. You give it a set of potentially harmful requests and observe whether it follows safety instructions. But what if the model recognises that it's being tested?

It might behave differently because it recognises the evaluation environment. This creates a problem. Are we measuring how the model behaves in real-world situations, or how it behaves when it knows it's being evaluated?

Researchers have traditionally looked for explicit signs of this awareness in the model's generated reasoning. Aranguri explores a different approach. Instead of waiting for the model to say something like *"The user might be testing"*, the researchers measure the probability that it would produce that sentence. This is what makes the approach interesting.

The model doesn't need to generate the sentence. Researchers can inspect its probability using the logits available during inference.

## What happens when we monitor what the model doesn't say?

The researchers built a logit monitor that tracks the probability of a predefined evaluation-aware sentence.

They tested it using Kimi K2.5 and Qwen 3 32B, comparing evaluation prompts from Fortress and Petri against real-world conversations from WildChat.

One result caught my attention. On the Fortress versus WildChat comparison, the logit monitor achieved an AUROC of 0.79 using a single rollout. The verbalization-based monitor reached 0.75 even with 100 rollouts. In other words, the logit-based approach could distinguish evaluation prompts from deployment prompts with considerably fewer model generations.

There was another finding I found particularly interesting. Whether an individual rollout explicitly verbalized evaluation awareness explained just 0.4% of the variation in the logit monitor's score. However, whether the prompt ever produced a rollout that verbalized evaluation awareness explained 24.9%.

This suggests that the prompt itself carries substantial information about evaluation awareness, even before the model explicitly expresses it.

The researchers also found that the signal was present at the beginning of the chain-of-thought, before any reasoning had been generated.

I found this fascinating because it changes what we can investigate. We don't necessarily have to wait for a model to reveal something in its generated text before looking for signals associated with it.

## But what exactly are we measuring?

I think this is where it is important to be careful. The experiment doesn't prove that the model has a hidden intention or that it is deliberately deceiving the evaluator. It measures the probability of a predefined sentence, given the model's current context. That is a useful signal, but it isn't a direct measurement of intent.

There is also a methodological question worth asking. The researchers distinguish Fortress prompts from WildChat prompts. Could some of the difference come from the datasets' writing styles, structures, or subject matter rather than evaluation awareness itself?

The authors acknowledge a related concern in their appendix. The Petri prompts include a system prompt, while WildChat prompts do not, which could inflate separability.

I would want to see further experiments that control for these differences and test whether the monitor generalises to new datasets. This is one of the things I find interesting about AI research. A promising result is not the end of the investigation. It gives us a better question to ask next.

## Where my curiosity went next, human-AI interaction

While exploring this research, I started thinking about a different problem. Most safety evaluations focus on how a model responds to a given prompt. But people don't interact with AI in the same way.

Consider three people asking for help with the same technical task.

- **A beginner** might describe the problem vaguely, without knowing the right terminology.
- **An experienced user** might provide more context and refine the request over several interactions.
- **An expert** might know exactly how to structure the request to obtain a specific outcome.

Even if their underlying objective is similar, their interactions with the model can look very different, and those differences might influence model behaviour.

So I started thinking. What if we studied AI safety not just at the model level, but at the level of human-AI interaction?

I am particularly interested in understanding whether different levels of user expertise, prompting strategies, and interaction patterns can influence the safety of model outputs.

Could we use generated responses alongside logit-level signals to identify potential risks that aren't immediately visible in the final answer? For example, imagine a model initially refusing a request, but gradually providing increasingly sensitive information as the user reframes the question across multiple turns.

Could changes in predefined risk-related token probabilities help us identify emerging risks before they appear in the final response? This is a hypothesis I would like to investigate, not something I assume logits can already detect.

## What would I investigate?

One experiment I am planning to explore is relatively straightforward.

Give participants with different levels of technical expertise the same underlying task. Observe how they formulate prompts, refine requests, and interact with the same model.

Then examine three things.

1. **Observable behaviour.** What responses does the model generate? Does it refuse, comply, or change its behaviour over multiple turns?
2. **Logit signals.** How do probabilities of predefined risk-related sequences change during these interactions?
3. **Interaction patterns.** Are certain prompting strategies or conversation trajectories associated with greater safety risks?

An important part of the experiment would be separating user expertise from user intent. A technically experienced user is not necessarily malicious, and a novice is not necessarily harmless.

I would also need to establish whether logit signals actually predict safety-relevant outcomes, rather than simply reflecting differences in wording or prompt complexity.

The objective would be to understand whether internal model signals can complement conventional safety evaluations and help identify risks emerging through human-AI interactions.

## What I am still looking for

I started by trying to understand what logits are and how a model chooses its next token. That led me to evaluation awareness, and eventually to a broader question about how people and AI systems influence each other's behaviour.

We spend a lot of time asking whether an AI model is safe. But perhaps we should also ask a second question. Does an AI system remain safe across different kinds of people, intentions, and interaction patterns?

I don't have an answer yet. But I think this is a worthwhile direction to investigate.
