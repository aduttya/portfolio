---
layout: post
title: "Text Embeddings for AEO and SEO: A Practitioner's Guide"
description: "How embeddings power AI answer engines, where they fail, and how to run a two-stage content audit — embedding retrieval plus LLM verification — for AEO."
---

**Text embeddings have become the connective tissue between content and AI answer engines**, and understanding how they work is now essential for any content team optimizing for visibility in ChatGPT, Perplexity, Google AI Overviews, and similar systems. These engines retrieve content at the passage level using dense vector similarity — not keyword matching — then verify answer quality with large language models before generating cited responses. The practical implication is stark: content must be optimized not just for topical relevance but for *extractability* as discrete, self-contained answer blocks. This report covers the full technical stack — from how embeddings encode meaning, to how AI engines use them internally, to how content teams can build auditing workflows that simulate these retrieval pipelines — along with the critical failure modes that make naive embedding-based analysis unreliable.

---

## How transformers compress meaning into 768-dimensional vectors

The encoding pipeline that converts text into an embedding vector follows a deterministic sequence. First, a **WordPiece tokenizer** splits input into subword tokens, prepending a `[CLS]` token and appending `[SEP]`. Each token maps to a learnable embedding vector (768 dimensions for base-sized models), which is summed with positional and segment embeddings. This representation matrix then passes through **12 stacked transformer layers** (for BERT-base architectures), where multi-head self-attention allows every token to attend to every other token, creating fully contextualized representations. The word "bank" gets a different vector depending on whether it appears near "river" or "account."

After the final transformer layer, the model produces a matrix of shape `[sequence_length, 768]` — one vector per token. This must be collapsed into a single fixed-size vector through **pooling**. BGE models use `[CLS]` token pooling (taking the first token's output), while many sentence-transformer models use mean pooling across all tokens. The resulting vector is then **L2-normalized** to unit length, so that dot product and cosine similarity become mathematically equivalent.

**Cosine similarity** between two unit vectors reduces to their dot product: `sim(A, B) = Σ(Aᵢ × Bᵢ)`. The score ranges from -1 to +1, where +1 indicates identical direction in the embedding space and 0 indicates orthogonality. A critical caveat for practitioners: **absolute similarity scores are not interpretable as relevance thresholds**. Contrastive training compresses the score distribution — BGE v1.0 pushed most scores into the 0.6–1.0 range — so only *relative ordering* of scores is meaningful. Setting a fixed threshold like "cosine > 0.7 means relevant" is unreliable.

Modern embedding models learn these representations through **contrastive fine-tuning** using InfoNCE loss. Given a query and its known positive passage, the model is trained to maximize their similarity while minimizing similarity with "hard negatives" — passages that are topically related but not actually relevant. This hard-negative mining is what teaches the model to distinguish between "related to the topic" and "actually answers the question," though this distinction remains imperfect. The training uses millions to billions of text pairs from web corpora, academic datasets like MS MARCO and Natural Questions, and synthetically mined pairs.

The key architectural distinction for practitioners is between **bi-encoders** and **cross-encoders**. Bi-encoders (like BGE) encode query and document independently into separate vectors, enabling pre-computation of document embeddings and millisecond-scale retrieval via approximate nearest neighbor search. Cross-encoders process query and document *together* through the full transformer, allowing token-level cross-attention that yields roughly **18% better ranking quality** — but at O(n) cost per query, making them usable only for reranking small candidate sets. This tradeoff drives the two-stage pipeline architecture discussed later.

![Transformer encoding pipeline — from raw text through tokenization, positional embeddings, stacked transformer layers, pooling, and L2 normalization to a final embedding vector](/assets/images/posts/transformer_encoding_pipeline.svg)

---

## How Google, Perplexity, and ChatGPT retrieve content using embeddings

Google's search pipeline, as revealed during DOJ antitrust trial testimony by VP of Search Pandu Nayak, operates through a confirmed multi-stage architecture. The foundation remains an **inverted index with BM25-style scoring** that narrows trillions of documents to tens of thousands of candidates. The system called **RankEmbed** (Google's neural matching, deployed 2018) then adds semantically relevant documents by encoding queries and documents into a shared embedding space and performing approximate nearest neighbor search. Finally, **DeepRank** — a BERT-based cross-encoder — performs deep relevance scoring on only the **top 20–30 documents**, because full cross-attention is too expensive for broader application. Google also confirmed **passage-level ranking** as a distinct system that evaluates individual sections of web pages, meaning a deeply buried paragraph can surface even if the page overall isn't the best match.

Google AI Overviews uses retrieval-augmented generation with query fan-out — breaking complex queries into subtopics and issuing multiple searches. Research shows **~85% of AI Overview citations come from top-10 organic results**, though this percentage is declining as Google diversifies sources. Roughly **38% of citations now come from outside the traditional top 10**, signaling that embedding-based semantic relevance is increasingly competing with traditional ranking signals.

**Perplexity AI** published detailed architecture documentation in September 2025. Their index tracks **over 200 billion unique URLs**. Retrieval uses simultaneous **hybrid search** — BM25 lexical matching and dense vector embedding search via the Vespa search backend — merging results into a combined candidate set. Multi-stage reranking follows: early stages use fast embedding-based scorers, while later stages apply **cross-encoder reranker models** for precision. Critically, Perplexity retrieves at **sub-document granularity**, emphasizing "surfacing the most atomic units possible" for optimal LLM context. An AI-driven module dynamically generates parsing rulesets to extract semantically meaningful content from diverse website structures.

**ChatGPT's browsing mode** uses the Bing Search API as its retrieval backend. When browsing is enabled, the system reformulates user queries into search queries, retrieves results from Bing, fetches relevant pages, extracts passages, and injects them as context for generation with citation tracking. Custom GPTs with document uploads use a more traditional RAG pipeline: documents are chunked, embedded, stored in a vector database, and retrieved via semantic similarity at query time.

The common pattern across all these systems is a **multi-stage pipeline**: broad retrieval (embeddings + BM25) → reranking (cross-encoders) → generation (LLM with grounding). This architecture is what makes Answer Engine Optimization fundamentally different from traditional SEO. The unit of optimization shifts from **entire pages** to **individual passages**; the matching mechanism shifts from **keywords and backlinks** to **semantic embedding similarity**; and the success metric shifts from **ranking position** to **being selected as a cited source**.

![AI engine retrieval pipeline — showing how Google, Perplexity, and ChatGPT move from broad index retrieval through embedding + BM25 hybrid search, cross-encoder reranking, and LLM generation with citation](/assets/images/posts/aeo_retrieval_pipeline.svg)

---

## BAAI/bge-base-en-v1.5 offers the best open-source size-to-performance ratio

The BGE (BAAI General Embedding) base model is a **109-million parameter, 12-layer BERT encoder** that produces **768-dimensional embeddings** with a maximum input length of 512 tokens. It uses `[CLS]` token pooling with L2 normalization, MIT-licensed for unrestricted commercial use.

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

Training follows a three-stage pipeline documented in the C-Pack paper (Xiao et al., 2023). First, **RetroMAE pre-training** — a masked auto-encoder approach where the encoder produces sentence embeddings from corrupted input while a lightweight decoder reconstructs the original text, teaching the model to compress semantic information into dense vectors. Second, **contrastive fine-tuning** on over a billion text pairs using InfoNCE loss with temperature τ=0.01, incorporating hard negatives mined via BM25 and model self-distillation. Third, the **v1.5 update** (September 2023) specifically addressed similarity distribution compression — v1.0 squished most scores into the 0.6–1.0 range, making discrimination difficult. The v1.5 release also improved retrieval without requiring the instruction prefix `"Represent this sentence for searching relevant passages: "` that v1.0 needed on queries.

BGE-base-en-v1.5 scored approximately **63.55 on MTEB** (Massive Text Embedding Benchmark), only 2–4% behind the 3× larger BGE-large (64.23) and competitive with proprietary models like OpenAI's text-embedding-3-large (64.6) and Cohere embed-v4 (65.2). Newer models like Qwen-3-Embedding (70.7) have surpassed it, but BGE-base remains the **de facto default for open-source semantic search** due to its inference speed (runs on CPU), ecosystem integration (native support in LangChain, LlamaIndex, ChromaDB, and all major vector databases), and zero per-token API costs. Its primary limitations are English-only support and the 512-token context window — for multilingual or long-document needs, BGE-M3 (8,192 tokens, 568M parameters) is the appropriate alternative.

For content teams building AEO auditing pipelines, BGE-base-en-v1.5 is a strong default choice: fast enough for real-time workflows, accurate enough for production, and free to run locally without API dependencies.

---

## Where embeddings fail: four critical traps for content teams

### Semantic similarity does not mean the content answers the question

This is the single most important failure mode. A content section can score high on embedding similarity because it discusses the same topic as a query, while completely failing to provide the answer. **LlamaIndex demonstrated this with a Great Gatsby experiment**: when asked "Who was driving the car that hit Myrtle?", the top two embedding retrieval results described the car crash in detail but never identified the driver. Only the third-ranked result contained the actual answer (Daisy). The embeddings correctly identified crash-related passages but could not distinguish "describes the event" from "answers the specific question."

This failure is structural, not incidental. Bi-encoders encode query and document independently — they cannot perform the token-level cross-attention needed to verify that a passage contains the specific information a question requests. A passage about "error codes in API integrations" will score highly against the query "What does error code TS-999 mean?" even if it never mentions TS-999. Similarly, a section titled "Revenue Growth Trends" may embed close to "What was ACME Corp's Q2 2023 revenue growth?" without containing any ACME-specific data.

### Chunk granularity creates a precision-context tradeoff

Chunk size directly determines embedding quality. **Too-large chunks dilute the signal**: when an embedding model compresses a multi-topic section into a single 768-dimensional vector, important details get "washed out" into a muddy centroid that is somewhat similar to many queries but strongly similar to none. **Too-small chunks lose context**: a 20-word fragment may match a query on surface features but lack the surrounding information needed to actually serve as an answer. NVIDIA's empirical testing across diverse datasets found that **factoid queries perform best with 256–512 token chunks**, while complex analytical queries benefit from **1,024 tokens or page-level chunking**.

Jina AI's research (April 2025) documented a **systematic length bias**: longer texts produce higher average similarity scores regardless of actual content relevance, because their embeddings spread across more semantic space, reducing the angle with any given query vector. Mixing drastically different chunk sizes in the same corpus — some 50 tokens, others 1,000 — introduces systematic retrieval distortion.

### Keyword stuffing creates false positives in embedding retrieval

Microsoft Research demonstrated that content densely packed with topically relevant keywords can inflate relevance scores even when the content doesn't genuinely answer queries. This extends beyond traditional keyword stuffing: any content that repeatedly uses terminology associated with a query domain — even naturally — can create embedding proximity without answer quality. Dense keyword co-occurrence maps to cluster proximity in embedding space, generating **retrieval false positives** that waste LLM context windows and degrade answer quality.

### Absolute similarity scores cannot determine relevance

You cannot set a universal cosine similarity threshold to determine relevance. As Jina AI's research confirmed, "comparing embedding vectors can only tell you about *relative* similarity, not relevance." The contrastive training process, score distribution compression, and length bias all conspire to make absolute scores unreliable. A score of 0.82 might indicate strong relevance in one corpus and weak relevance in another, depending on the distribution of all scores in that collection. Only rank ordering within a single comparison set is meaningful.

![Four embedding failure modes — semantic similarity without answer quality, chunk granularity tradeoff, keyword stuffing false positives, and unreliable absolute similarity scores](/assets/images/posts/embedding_failure_modes.svg)

---

## How to chunk content for AEO: heading-aware strategies outperform fixed splits

For AEO content optimization, the chunking strategy determines whether your pipeline accurately identifies which content sections AI engines will retrieve. Five strategies exist on a spectrum from simple to sophisticated.

**Fixed-size chunking** (split every N tokens) is fast and consistent but splits mid-sentence and ignores document structure. **Recursive chunking** — splitting by paragraphs first, then sentences, then tokens — preserves natural boundaries and delivers **30–50% higher retrieval precision** over naive fixed splits according to practitioner benchmarks. **Semantic chunking** groups content by embedding similarity, splitting at meaning transitions using tools like LlamaIndex's `SemanticSplitterNodeParser`, but produces variable chunk sizes. **Heading-aware chunking** uses H1/H2/H3 boundaries as natural split points — this is the most critical strategy for AEO because answer engines extract content under specific headings. **Hierarchical chunking** creates multi-level representations (section → subsection → paragraph), enabling both broad and precise retrieval.

NVIDIA's empirical benchmarks across five diverse datasets found that **page-level chunking** achieved the highest average RAG accuracy (**0.648**) with the lowest variance, while token-based chunking ranged from 0.603 to 0.645. A **15% overlap** between chunks performed best in their testing. For AEO-specific workflows, the practical recommendation is:

- Use H2/H3 headings as primary chunk boundaries
- Target **256–512 tokens** per chunk (matching typical answer engine citation length)
- Add **10–20% overlap** between adjacent chunks
- Prepend heading hierarchy (H1 > H2 > H3) as metadata to each chunk
- Keep chunk sizes within a narrow range to avoid length bias distortion

Anthropic's **Contextual Retrieval** approach takes this further: before embedding each chunk, an LLM generates a short context description (50–100 tokens) situating the chunk within the overall document. This single addition reduced top-20 retrieval failure rates by **35%**. Combined with BM25 and reranking, the failure reduction reached **67%** at a cost of roughly $1.02 per million document tokens.

---

## The two-stage pipeline: embed first, then verify with an LLM

The most reliable AEO content auditing workflow mirrors the architecture of production answer engines: use embeddings for fast candidate retrieval, then use an LLM to verify whether candidates actually answer the target query. This two-stage approach addresses the fundamental limitation that embeddings measure topical proximity, not answer quality.

**Stage 1 — Embedding retrieval**: Embed your target queries (the questions your audience asks) and your content chunks (sections split by headings). Compute cosine similarity to identify the top 10–50 candidate chunks per query. This runs in milliseconds and prioritizes **recall** — casting a wide net. Tools like Screaming Frog v22 now integrate this directly: connect to an embedding API, crawl your site, and enter any query to find pages with highest semantic similarity on a 0–100 scale.

**Stage 2 — LLM verification**: Pass each candidate chunk and the original query to an LLM (Claude, GPT-4, or similar) with a structured evaluation prompt. A practical prompt template:

> *Given this content section and this user query, rate 0–3: (0) unrelated, (1) topically related but doesn't answer, (2) partial answer but unclear or incomplete, (3) directly and clearly answers the query. Identify what specific information is missing to fully answer the query.*

**The diagnostic gap between stages is the most actionable output.** A section that scores high on embedding similarity (Stage 1) but low on LLM answer verification (Stage 2) is topically relevant but fails to deliver the answer — this is your highest-priority rewrite target. A section that scores low on both stages represents a content gap requiring new content creation.

LlamaIndex's `LLMRerank` postprocessor implements this pattern directly: retrieve top-K via embeddings, then have an LLM assess relevance and reorder. In their Great Gatsby test, this pipeline returned a single, correct result instead of three partially-relevant ones. For content optimization at scale, cross-encoder rerankers (like BGE Reranker or Cohere Rerank) offer a middle ground — **75× cheaper than LLM-based evaluation** according to NVIDIA benchmarks, while still capturing query-document interaction through cross-attention.

Real-world results validate this architecture: Anthropic's contextual retrieval pipeline (top-150 retrieval → rerank to top-20) achieved a **67% reduction** in retrieval failures. Chatbase reports **40% improvement in mean reciprocal rank** and **25% reduction in off-topic responses** from adding the reranking stage. The cost is minimal — cross-encoder reranking adds sub-second latency and negligible compute compared to the downstream LLM generation step.

![Two-stage AEO audit workflow — embedding retrieval for candidate identification followed by LLM verification to distinguish topically close content from content that actually answers the query](/assets/images/posts/two_stage_aeo_audit_workflow.svg)

---

## Conclusion: embeddings are necessary but not sufficient

The core insight for content teams is that **embeddings solve the retrieval problem but not the answer problem**. They efficiently identify which of your content sections live in the same semantic neighborhood as target queries — an essential first step that no manual audit can replicate at scale. But semantic proximity is not answer quality, and treating high cosine similarity as proof that content will satisfy an AI answer engine is the most common and costly mistake in AEO workflows.

The actionable framework is a three-layer strategy. First, **structure content for extractability**: heading-aware sections of 256–512 tokens, each self-contained enough to serve as a standalone answer. Second, **use embeddings for scalable candidate identification**: embed target queries against your content corpus to map which sections are likely retrieval candidates for which queries, and where gaps exist. Third, **verify with an LLM**: run the highest-similarity candidates through a language model to distinguish "topically close" from "actually answers the question," and prioritize rewrites where the gap between retrieval score and answer quality is largest. This three-layer pipeline — structure, retrieve, verify — directly simulates what Perplexity, Google AI Overviews, and ChatGPT do when deciding which content to cite, making it the most architecturally honest approach to AEO available today.
