# Architecture

This document explains how the pieces of the project fit together, and why they're structured this way.

## Overview

The project follows a simple pipeline: documents go in, get broken into searchable pieces, and two independent checks are run against them — one comparing a vendor's documents to regulations, and one comparing a vendor's documents to each other. Both checks share the same underlying retrieval and reasoning engine.

```
Documents (contracts, policies, regulations)
        │
        ▼
   Ingest & embed  (chunk text, store as searchable vectors)
        │
   ┌────┴────┐
   ▼         ▼
Gap        Contradiction
Coverage    Check
   │         │
   └────┬────┘
        ▼
LLM reasoning (cites exact source sentences + confidence)
        │
        ▼
  Risk dashboard
```

## Why this shape

Gap coverage and contradiction checking are conceptually different — one compares a document against an external rule, the other compares two documents against each other — but they both need the exact same underlying capability: find the most relevant piece of text, then ask a language model to reason over it and explain why. Rather than building two separate pipelines, both features are built as thin layers on top of one shared retrieval-and-reasoning core. This keeps the two features consistent (same citation style, same confidence handling, same output shape) and means an improvement to the core (better chunking, a stronger model, better prompting) benefits both features at once.

## Components

### `src/ingest.py` — loading and chunking

Takes a document (plain text, PDF, or a public Google Doc link) and turns it into a list of overlapping text chunks. Documents are chunked rather than processed whole because:
- Language models have limited context, and long documents need to be broken down to be searched effectively
- Smaller chunks let the retrieval step return *just* the relevant paragraph, rather than an entire document, which keeps the reasoning step focused

Chunking is currently done by a fixed character count with overlap between consecutive chunks, so a sentence sitting near a chunk boundary still appears whole in at least one chunk. See [Known Limitations](README.md#known-limitations) for the trade-offs of this approach.

### `src/embed.py` — storage and retrieval

Wraps [ChromaDB](https://www.trychroma.com/), a local vector database. Two responsibilities:
- **Storing** — each chunk is converted into an embedding (a numeric representation of its meaning) and saved, along with metadata recording which document it came from
- **Searching** — given a query (which can itself be a full sentence, not just a keyword), returns the stored chunks that are closest in *meaning*, not just in wording

Documents are grouped into named "collections" — one per vendor, one per regulation set — so a search never accidentally mixes one vendor's documents with another's.

### `src/reasoning.py` — the model call

A thin wrapper around a locally-running [Ollama](https://ollama.com) model (Llama 3.2, 3B parameters by default). Every call includes a system prompt establishing the model's role and ground rules (only state a problem if it's backed by the text, don't guess, don't invent citations). This is the only component in the project that does actual reasoning — everything else is retrieval or formatting.

### `src/models.py` — shared result structure

Defines a single `Flag` data structure that both gap coverage and contradiction checking return. Every `Flag` carries the same fields regardless of which feature produced it: a topic, a severity level, a verdict, the exact quoted sentences involved, a plain-language explanation, and the full raw model response for reference. This is what lets the dashboard display both kinds of findings identically, without needing separate rendering logic for each.

`models.py` deliberately has no dependency on either feature file — it sits *underneath* both of them, defining a shape they conform to, not logic they call into. (Early in development, a circular import happened here when this rule was briefly violated — worth keeping in mind if extending this file.)

### `src/gap_coverage.py` — vendor vs. regulation

For every chunk of a regulation, searches the vendor's documents for the most relevant excerpt, then asks the model whether that excerpt actually satisfies the regulation's requirement. A regulation chunk with no good match in the vendor's documents is itself a meaningful finding — silence on a required topic is treated as a gap, not ignored.

### `src/contradiction_check.py` — vendor vs. vendor

Groups a vendor's stored chunks by which original document they came from, then compares each pair of documents against each other (contract vs. privacy policy, contract vs. SOC2 report, etc.), asking the model whether they make consistent claims about the same topic.

### `app/dashboard.py` — the interface

A [Streamlit](https://streamlit.io) app that ties everything together: lets a user upload documents (or provide Google Doc links), runs both checks, and displays the results as structured cards — topic, severity, verdict, the exact quoted sentences, and a plain-language explanation, with the full surrounding text available on demand.

## Data flow for a single finding

Tracing one gap-coverage finding end to end:

1. A regulation chunk (e.g. "must acknowledge complaints within 15 days") is pulled from the regulation collection
2. `search()` looks up the vendor's collection for the chunk most semantically similar to that regulation text
3. Both texts are placed into a structured prompt asking the model to judge whether the vendor's text satisfies the regulation, and to quote the specific sentence responsible for its verdict
4. The model's response is parsed into a `Flag` — topic, severity, verdict, both quoted sentences, and a plain-language explanation
5. The dashboard renders that `Flag` as a card, with the quoted sentences highlighted within their surrounding context if you expand it

Every step is traceable — the final card can always be traced back to the two specific source sentences that produced it.

## Design principles

- **Every verdict must be backed by a quote.** A compliance tool that says "gap found" without showing the exact text it's based on isn't trustworthy enough to act on.
- **Shared core, independent features.** Gap coverage and contradiction checking are separate concerns but share one retrieval-and-reasoning engine, so improvements apply to both.
- **Fail safe, not silent.** Where a quote can't be matched exactly back to its source text, the interface falls back to showing the full excerpt rather than failing or showing nothing.
- **Runs entirely locally.** No API costs, no data leaves the machine — appropriate for a project handling documents that would, in a real scenario, be sensitive.