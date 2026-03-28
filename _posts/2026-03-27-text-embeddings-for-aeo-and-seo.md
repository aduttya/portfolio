---
layout: post
title: "Text Embeddings for AEO and SEO: A Practitioner's Guide"
description: "How embeddings power AI answer engines, where they fail, and how to run a two-stage content audit, embedding retrieval plus LLM verification for AEO."
---

**Text embeddings have become the connective tissue between content and AI answer engines.** Understanding how they work is now essential for any content team optimizing for visibility in ChatGPT, Perplexity, Google AI Overviews, and similar systems.

These engines retrieve content at the passage level using dense vector similarity — not keyword matching — then verify answer quality with large language models before generating cited responses.[^perplexity-arch] The practical implication: content must be optimized not just for topical relevance but for *extractability* as discrete, self-contained answer blocks.

This article covers:

- How embeddings encode meaning
- How AI engines use them internally
- How to build auditing workflows that simulate retrieval pipelines
- The critical failure modes that make naive embedding-based analysis unreliable

---

## How transformers turn text into searchable numbers

![Transformer encoding pipeline diagram](/assets/images/posts/transformer_encoding_pipeline.svg)

The encoding pipeline converts text into a vector through four deterministic stages:

1. **Tokenization** — A WordPiece tokenizer splits input into subword tokens, prepending a `[CLS]` token and appending `[SEP]`. Each token maps to a learnable 768-dimensional embedding, summed with positional and segment embeddings.
2. **Contextualization** — The token matrix passes through 12 stacked transformer layers (BERT-base). Multi-head self-attention lets every token attend to every other, producing fully contextual representations. "Bank" gets a different vector near "river" than near "account."
3. **Pooling** — The final layer outputs a `[sequence_length, 768]` matrix, one vector per token. This collapses to a single vector: BGE uses `[CLS]` token pooling; most sentence-transformer models use mean pooling across all tokens.
4. **L2 normalization** — The vector is normalized to unit length, making dot product and cosine similarity mathematically equivalent.

### Cosine similarity in practice

`sim(A, B) = Σ(Aᵢ × Bᵢ)` — scores range from -1 to +1:

- **+1** — identical direction in embedding space
- **0** — orthogonal (unrelated)
- **-1** — opposite direction

**Critical caveat:** absolute scores are not interpretable as relevance thresholds.[^jina-size] Contrastive training compresses the score distribution (BGE v1.0 pushed most scores into 0.6–1.0), so only *relative ordering* within a comparison set is meaningful. A fixed threshold like "cosine > 0.7 means relevant" is unreliable.

### How models learn: contrastive fine-tuning

Models are trained with InfoNCE loss on query–passage pairs:[^cpack]

- **Maximize** similarity between a query and its known positive passage
- **Minimize** similarity with "hard negatives" — topically related passages that don't actually answer the query
- **Training data:** millions to billions of pairs from MS MARCO, Natural Questions, and synthetically mined corpora

### Bi-encoders vs. cross-encoders

| | Bi-encoder | Cross-encoder |
|---|---|---|
| How it works | Encodes query and document independently | Processes query + document together |
| Speed | Millisecond retrieval via ANN search | O(n) cost per query |
| Ranking quality | Scalable, lower precision | ~18% better than bi-encoder[^pinecone-rerank] |
| Use case | Broad retrieval | Reranking small candidate sets |

This tradeoff drives the two-stage pipeline architecture discussed later.

---

## How Google, Perplexity, and ChatGPT retrieve content using embeddings

![AI engine retrieval pipeline diagram](/assets/images/posts/aeo_retrieval_pipeline.svg)

The common pattern across all major AI answer engines is a **multi-stage pipeline**: broad retrieval → reranking → generation. Here's how each system implements it.

### Google

Confirmed via DOJ antitrust trial testimony by VP of Search Pandu Nayak:[^google-doj]

- **Stage 1-BM25 index:** narrows trillions of documents to tens of thousands of candidates
- **Stage 2-RankEmbed** (deployed 2018): neural matching encodes queries and documents into a shared embedding space, adds semantically relevant results via ANN search[^google-rankembed]
- **Stage 3-DeepRank:** BERT-based cross-encoder scores only the top 20–30 documents, full cross-attention is too expensive for broader use
- **Passage-level ranking:** a separate system evaluates individual sections of pages, so a buried paragraph can surface even if the page overall isn't the best match

Google AI Overviews adds query fan-out, breaking complex queries into subtopics and issuing multiple searches. Key stats:

- **40–54%** of AI Overview citations overlap with top-10 organic results[^aio-overlap]
- **#1 ranked page** has a ~33% probability of being cited in an AI Overview[^xseek]

### Perplexity AI

Published architecture documentation (September 2025):[^perplexity-arch]

- **Index:** over 200 billion unique URLs
- **Retrieval:** simultaneous hybrid search, BM25 + dense vector embedding via the Vespa backend[^vespa]
- **Reranking:** multi-stage, fast embedding scorers early, cross-encoder models late
- **Granularity:** sub-document retrieval, emphasizing "surfacing the most atomic units possible"[^perplexity-api]

### ChatGPT

- **Browsing mode:** uses the Bing Search API, reformulates queries, fetches pages, extracts passages, injects as context with citation tracking
- **Custom GPTs:** traditional RAG pipeline, documents chunked, embedded, stored in a vector database, retrieved via semantic similarity at query time

### What this means for AEO

The unit of optimization shifts from **entire pages** to **individual passages**. The matching mechanism shifts from **keywords and backlinks** to **semantic embedding similarity**. The success metric shifts from **ranking position** to **being selected as a cited source**.

---

## BAAI/bge-base-en-v1.5: best open-source size-to-performance ratio

The BGE base model is a **109M parameter, 12-layer BERT encoder** producing 768-dimensional embeddings. MIT-licensed, free for commercial use.[^bge-card]

| Property | Value |
|---|---|
| Architecture | BERT-base (encoder-only) |
| Parameters | ~109M |
| Embedding dimensions | 768 |
| Max sequence length | 512 tokens |
| Pooling | [CLS] token |
| MTEB average score | ~63.55 |
| Model size on disk | 438 MB |
| License | MIT |

### Training pipeline (C-Pack paper, Xiao et al., 2023)[^cpack]

1. **RetroMAE pre-training**: masked auto-encoder: encoder produces embeddings from corrupted input, lightweight decoder reconstructs the original, teaching the model to compress semantic information into dense vectors
2. **Contrastive fine-tuning**: over 1 billion text pairs, InfoNCE loss with temperature τ=0.01, hard negatives mined via BM25 and model self-distillation
3. **v1.5 update** (September 2023): addressed score distribution compression from v1.0; removed the requirement for the instruction prefix on queries[^bge-card]

### How it compares

| Model | MTEB score | Notes |
|---|---|---|
| BGE-base-en-v1.5 | 63.55 | 438 MB, runs on CPU |
| BGE-large-en-v1.5 | 64.23 | 3× larger |
| OpenAI text-embedding-3-large | 64.6 | API cost per token |
| Cohere embed-v4 | 65.2 | API cost per token |
| Qwen-3-Embedding | 70.7 | Newer, higher cost |

BGE-base remains the **de facto default for open-source semantic search**: inference speed, native support in LangChain, LlamaIndex, ChromaDB, and zero API costs.

**Limitations:** English-only, 512-token context window. For multilingual or long-document needs, use BGE-M3 (8,192 tokens, 568M parameters).

---

## Where embeddings fail: four critical traps for content teams

![Four embedding failure modes diagram](/assets/images/posts/embedding_failure_modes.svg)

### 1. Semantic similarity ≠ the content answers the question

This is the most important failure mode. A section can score high on embedding similarity because it discusses the same topic, while completely failing to provide the answer.

**LlamaIndex's Great Gatsby experiment:** asked "Who was driving the car that hit Myrtle?" the top two results described the crash in detail but never named the driver. Only the third result contained the actual answer (Daisy).[^llamaindex]

Why this happens structurally:

- Bi-encoders encode query and document independently
- They cannot perform the token-level cross-attention needed to verify a passage contains the *specific* information requested
- A passage about "error codes in API integrations" scores highly against "What does error code TS-999 mean?" even if TS-999 is never mentioned

### 2. Chunk size creates a precision-context tradeoff

| Chunk size | Problem |
|---|---|
| Too large | Important details "washed out" into a muddy centroid, somewhat similar to many queries, strongly similar to none |
| Too small | Matches on surface features but lacks surrounding context needed to serve as an answer |

NVIDIA's empirical findings:[^nvidia-chunk]
- **Factoid queries** → best with 256–512 token chunks
- **Complex analytical queries** → best with 1,024 tokens or page-level

Jina AI (April 2025) also documented a **systematic length bias**: longer texts produce higher average similarity scores regardless of relevance, because their embeddings spread across more semantic space.[^jina-size]

### 3. Keyword stuffing creates false positives

Microsoft Research demonstrated at SIGIR 2024 that content densely packed with topically relevant keywords inflates relevance scores even when it doesn't genuinely answer queries.[^ms-stuffing] Dense keyword co-occurrence maps to cluster proximity in embedding space, generating **retrieval false positives** that:

- Waste LLM context windows
- Degrade answer quality
- Make your content rank highly in retrieval but never get cited

### 4. Absolute similarity scores cannot determine relevance

You cannot set a universal cosine similarity threshold.[^jina-size] The contrastive training process, score distribution compression, and length bias all make absolute scores unreliable:

- A score of 0.82 might indicate strong relevance in one corpus and weak relevance in another
- Only **rank ordering within a single comparison set** is meaningful
- "Comparing embedding vectors can only tell you about *relative* similarity, not relevance"

---

## How to chunk content for AEO

Five strategies exist on a spectrum from simple to sophisticated:

| Strategy | How it works | Best for |
|---|---|---|
| Fixed-size | Split every N tokens | Simple pipelines, consistent chunk sizes |
| Recursive | Split by paragraph → sentence → token | General use, 30–50% better precision than fixed |
| Semantic | Split at meaning transitions via embedding similarity | Variable-length natural splits |
| Heading-aware | Split at H1/H2/H3 boundaries | **AEO — most critical strategy** |
| Hierarchical | Multi-level: section → subsection → paragraph | Both broad and precise retrieval |

### Practical AEO recommendations

Based on NVIDIA's empirical benchmarks across five diverse datasets:[^nvidia-chunk]

- Use **H2/H3 headings** as primary chunk boundaries
- Target **256–512 tokens** per chunk (matches typical answer engine citation length)
- Add **10–20% overlap** between adjacent chunks (15% performed best in NVIDIA's testing)
- Prepend heading hierarchy (H1 > H2 > H3) as metadata to each chunk
- Keep chunk sizes within a narrow range to avoid length bias distortion

### Contextual Retrieval (Anthropic)[^anthropic-cr]

Before embedding each chunk, an LLM generates a 50–100 token context description situating the chunk within the overall document:

- Reduced top-20 retrieval failure rates by **35%**
- Combined with BM25 and reranking: **67% failure reduction**
- Cost: ~$1.02 per million document tokens

---

## The two-stage pipeline: embed first, then verify with an LLM

![Two-stage AEO audit workflow diagram](/assets/images/posts/two_stage_aeo_audit_workflow.svg)

The most reliable AEO auditing workflow mirrors production answer engines: use embeddings for fast candidate retrieval, then use an LLM to verify whether candidates actually answer the query.[^llamaindex]

### Stage 1: Embedding retrieval

- Embed target queries (the questions your audience asks) and content chunks (sections split by headings)
- Compute cosine similarity to identify the top 10–50 candidate chunks per query
- Runs in milliseconds, prioritizes **recall**, casting a wide net
- Tools: Screaming Frog v22 integrates this directly connect to an embedding API, crawl your site, find pages with highest semantic similarity on a 0–100 scale

### Stage 2: LLM verification

Pass each candidate chunk and query to an LLM with a structured prompt:

> *Given this content section and this user query, rate 0–3: (0) unrelated, (1) topically related but doesn't answer, (2) partial answer but unclear or incomplete, (3) directly and clearly answers the query. Identify what specific information is missing to fully answer the query.*

### Reading the diagnostic gap

| Stage 1 score | Stage 2 score | What it means | Action |
|---|---|---|---|
| High | High | Strong citation candidate | Keep |
| High | Low | Topically close, doesn't answer | **Priority rewrite** |
| Low | Low | Not relevant | New content needed |
| Low | High | Rare — check chunking | Review chunk boundaries |

### Real-world results

- **Anthropic contextual retrieval** (top-150 → rerank to top-20): **67% reduction** in retrieval failures[^anthropic-cr]
- **Cost:** cross-encoder rerankers (BGE Reranker, Cohere Rerank) are **75× cheaper** than LLM-based evaluation[^nvidia-chunk]
- LlamaIndex's `LLMRerank` postprocessor: retrieve top-K via embeddings, then LLM reorders — returned a single correct result vs. three partially-relevant ones in the Great Gatsby test[^llamaindex]

---

## Conclusion: embeddings are necessary but not sufficient

**Embeddings solve the retrieval problem but not the answer problem.** They efficiently identify which content sections live in the same semantic neighborhood as target queries — an essential first step no manual audit can replicate at scale. But semantic proximity is not answer quality.

The actionable framework is three layers:

1. **Structure for extractability**: heading-aware sections of 256–512 tokens, each self-contained enough to serve as a standalone answer
2. **Embed for candidate identification**: map which sections are likely retrieval candidates for which queries, and where gaps exist
3. **Verify with an LLM**: distinguish "topically close" from "actually answers the question," and prioritize rewrites where the gap is largest

This pipeline: structure, retrieve, verify directly simulates what Perplexity, Google AI Overviews, and ChatGPT do when deciding which content to cite.

---

## References

[^perplexity-arch]: Perplexity AI: [Architecting and Evaluating an AI-First Search API](https://research.perplexity.ai/articles/architecting-and-evaluating-an-ai-first-search-api)
[^vespa]: Vespa.ai: [How Perplexity uses Vespa](https://vespa.ai/perplexity/)
[^perplexity-api]: Perplexity AI: [Introducing the Perplexity Search API](https://www.perplexity.ai/hub/blog/introducing-the-perplexity-search-api)
[^google-doj]: Keywords People Use: [How Google Search Works](https://keywordspeopleuse.com/seo/guides/how-google-search-works)
[^google-rankembed]: Natzir Turrado: [How Google Works](https://natzir.com/en/posicionamiento-buscadores/how-google-works-working-algorithms/)
[^aio-overlap]: Search Engine Journal / BrightEdge: [Google AI Overviews Overlaps Organic Search by 54%](https://www.searchenginejournal.com/google-ai-overviews-overlaps-organic-search-by-54/557317/)
[^xseek]: xSeek: [Do Top Google Rankings Drive More AI Overview Citations?](https://www.xseek.io/learnings/do-top-google-rankings-drive-more-ai-overview-citations)
[^bge-card]: BAAI: [bge-base-en-v1.5 Model Card](https://huggingface.co/BAAI/bge-base-en-v1.5)
[^cpack]: Xiao et al., 2023: [C-Pack: Packed Resources for General Chinese Embeddings](https://arxiv.org/pdf/2309.07597)
[^jina-size]: Jina AI: [On the Size Bias of Text Embeddings and Its Impact in Search](https://jina.ai/news/on-the-size-bias-of-text-embeddings-and-its-impact-in-search/)
[^pinecone-rerank]: Pinecone: [Rerankers and Two-Stage Retrieval](https://www.pinecone.io/learn/series/rag/rerankers/)
[^anthropic-cr]: Anthropic: [Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
[^nvidia-chunk]: NVIDIA Developer Blog: [Finding the Best Chunking Strategy for Accurate AI Responses](https://developer.nvidia.com/blog/finding-the-best-chunking-strategy-for-accurate-ai-responses/)
[^ms-stuffing]: Microsoft Research / SIGIR 2024: [LLMs can be Fooled into Labelling a Document as Relevant](https://www.microsoft.com/en-us/research/wp-content/uploads/2024/10/SIGIRAP24_keyword_stuffing__camera_ready_.pdf)
[^llamaindex]: LlamaIndex: [Using LLMs for Retrieval and Reranking](https://www.llamaindex.ai/blog/using-llms-for-retrieval-and-reranking-23cf2d3a14b6)
