# Hybrid Retrieval (Flat Chunks)

## What this method does

Hybrid Retrieval (Flat Chunks) is the original Hybrid Retrieval (Flat Chunks) pipeline. It parses the PDF, chunks extracted text, indexes the chunks with BM25 plus a local TF-IDF dense surrogate, retrieves top chunks, and generates schema-targeted answers with citations.

This method retrieves and generates from flat chunks. It does not expand retrieved hits to the full parent section.

## Architecture

```mermaid
flowchart TD
  A["Input PDF"] --> B["Parse PDF<br/>pipeline/parse.py<br/>pypdf layout text"]
  B --> C["Flat chunks<br/>pipeline/chunk.py<br/>about 900 tokens plus metadata"]
  C --> D["Hybrid index<br/>pipeline/index.py<br/>BM25 plus TF-IDF"]
  D --> E["Flat-chunk retrieval<br/>retrieve.py<br/>top-k chunks plus rerank"]
  E --> F["Schema-targeted extraction<br/>extract.py<br/>citations required"]
  F --> G{"Grounded quote found?"}
  G -- "yes" --> H["Answer claims<br/>answer, page, quote"]
  G -- "no" --> I["Refusal<br/>refusal_reason"]
  H --> J["Eval output JSON"]
  I --> J
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
