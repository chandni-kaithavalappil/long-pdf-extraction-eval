# Hierarchical Retrieval with Parent Expansion

## What this is

Hierarchical Retrieval with Parent Expansion retrieves small chunks first, then expands each hit to the larger parent section before answer generation. This is the same family of patterns as small-to-big retrieval, LangChain's Parent Document Retriever, and LlamaIndex's auto-merging retriever.

This implementation is a reference method for the table-prose interleaving failure observed in this repo. It is not a new architecture.

## Why this exists

The Hybrid Retrieval (Flat Chunks) run often found the prose section defining a scheme but missed the nearby table row containing the BE allocation. That failure showed up clearly on Q1, Q2, Q5, and Q7:

- Q1: VB-G RAM G
- Q2: PMAY-Urban
- Q5: PMVBRY
- Q7: NSAP

In these cases, entity names and explanatory prose were close to, but not always inside, the exact same chunk as the numeric value. Parent expansion tries to keep the precise retrieval behavior of small chunks while restoring the neighboring table/prose context needed for grounded extraction.

## Architecture

```mermaid
flowchart TD
  A[Input PDF] --> B[Parser\nparse.py / pypdf layout text]
  B --> C[Page Objects\npage text + ministry + demand + section metadata]
  C --> D[Chunker\nchunk.py / ~900-token small chunks]
  D --> E[Parent Metadata\nparent_section_id = ministry + demand + nearest scheme/section]
  D --> F[Index\nBM25 + local TF-IDF dense surrogate]
  F --> G[Small-Chunk Retrieval\nTOP_K=18, RERANK_K=8]
  G --> H[Parent Expansion\nfetch chunks/pages sharing parent_section_id\nplus nearby sibling pages]
  H --> I[Expanded Context\ntypically 1-3 pages around the hit]
  I --> J[Generation\nforced citation schema]
  J --> K{Grounded?}
  K -- yes --> L[Answer claims\n{answer, page, quote}]
  K -- no --> M[Refusal\nrefusal_reason]
  L --> N[Eval JSON]
  M --> N
```

## Component choices

Parser: uses the existing `parse.py` with `pypdf` layout extraction. Docling, Unstructured, Marker, and OCR were not used because this method isolates retrieval behavior rather than parser quality.

Chunking: uses the same ~900-token chunks as the flat pipeline. Each chunk also records `parent_section_id`, derived from ministry, demand, and nearest scheme or section heading. We rejected retrieving only large sections because that loses small-chunk precision.

Indexing: uses the existing local hybrid index: BM25 plus TF-IDF from scikit-learn. No hosted embedding model is required. This keeps the experiment runnable offline and comparable to the flat pipeline.

Retrieval: retrieves top small chunks first (`TOP_K = 18`, `RERANK_K = 8`), then expands each hit to its parent section and neighboring pages. This is the core difference from Hybrid Retrieval (Flat Chunks).

Generation: keeps the same forced-citation contract: every claim must include `{answer, page, quote}`. If grounding is not found, the method returns `refusal_reason`.

## Files

- `run.py` — end-to-end runner for this method
- `README.md` — this document

Shared repo files used by this method:

- `pipeline/parse.py`
- `pipeline/chunk.py`
- `pipeline/index.py`
- `pipeline/hybrid_retrieval_flat_chunks/retrieve.py`
- `pipeline/eval.py`

## How to run

From repo root:

```bash
python3 pipeline/hierarchical_retrieval_parent_expansion/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name hierarchical_retrieval_parent_expansion_2026
```

The output is written to:

```bash
output/results_hierarchical_retrieval_parent_expansion_2026.json
```

## What it will not handle

Name disambiguation is still weak. Q5 improved but remained imperfect because similarly named employment schemes and table/prose variants can confuse selection.

Cross-document references were not tested. This method expands within one PDF only.

Image-heavy or scanned PDFs are not handled well because `pypdf` is text-only.

Aggregation queries spanning many sections remain hard. Q8 is the stress case: it requires collecting multiple rows, not simply expanding one parent.

Schema drift across years is only partly addressed. The 2025 run showed mixed results when section structure and scheme availability changed.

Page alignment can remain imperfect because extracted PDF page indices and eval page references may not match exactly.

## Extension points

- Swap `parse.py` for Docling or another table-aware parser.
- Add a name-disambiguation reranker for Q5-class failures.
- Add aggregation logic for Q8-class questions: retrieve multiple parent sections, extract rows, then filter/sort by numeric allocation.
