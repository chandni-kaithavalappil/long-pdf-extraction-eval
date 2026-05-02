# Hybrid Retrieval (Flat Chunks)

## What this method does

Hybrid Retrieval (Flat Chunks) is the original Hybrid Retrieval (Flat Chunks) pipeline. It parses the PDF, chunks extracted text, indexes the chunks with BM25 plus a local TF-IDF dense surrogate, retrieves top chunks, and generates schema-targeted answers with citations.

This method retrieves and generates from flat chunks. It does not expand retrieved hits to the full parent section.

## Architecture

```mermaid
flowchart TD
  A[PDF] --> B[parse.py\npypdf layout text]
  B --> C[chunk.py\n~900-token chunks + metadata]
  C --> D[index.py\nBM25 + TF-IDF]
  D --> E[retrieve.py\ntop-k flat chunks + rerank]
  E --> F[extract.py\nforced {answer,page,quote}]
  F --> G[eval output JSON]
```

## Files

- `run.py` — end-to-end runner for this method
- `retrieve.py` — hybrid retrieval over flat chunks
- `extract.py` — schema-targeted extraction from retrieved chunks
- `README.md` — this document

Shared repo files used by this method:

- `pipeline/parse.py`
- `pipeline/chunk.py`
- `pipeline/index.py`
- `pipeline/eval.py`
- `pipeline/config.py`

## How to run

From repo root:

```bash
python3 pipeline/hybrid_retrieval_flat_chunks/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name hybrid_retrieval_flat_chunks_2026
```

## Known limitations from this experiment

The dominant failure mode was table-prose interleaving: the retriever found prose defining a scheme but missed the sibling table row containing the allocation. This showed up in Q1, Q2, Q5, and Q7.
