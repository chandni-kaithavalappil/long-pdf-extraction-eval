# Pipeline Overview

This folder contains shared code plus three clearly separated methods.

## Method folders

```text
pipeline/
  full_context_dump/
    run.py
    README.md

  hybrid_retrieval_flat_chunks/
    run.py
    retrieve.py
    extract.py
    README.md

  hierarchical_retrieval_parent_expansion/
    run.py
    README.md
```

## Shared modules

```text
pipeline/
  parse.py        # pypdf layout extraction
  chunk.py        # ~900-token chunks + parent_section_id metadata
  index.py        # BM25 + TF-IDF index build
  bm25.py         # local BM25 implementation
  eval.py         # scoring helper
  config.py       # defaults
  util.py         # JSON/path helpers
```

## Method names

Use these names consistently:

- Full-Context Dump
- Hybrid Retrieval (Flat Chunks)
- Hierarchical Retrieval with Parent Expansion

## Run examples

Full-Context Dump:

```bash
python3 pipeline/full_context_dump/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name full_context_dump_2026
```

Hybrid Retrieval (Flat Chunks):

```bash
python3 pipeline/hybrid_retrieval_flat_chunks/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name hybrid_retrieval_flat_chunks_2026
```

Hierarchical Retrieval with Parent Expansion:

```bash
python3 pipeline/hierarchical_retrieval_parent_expansion/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name hierarchical_retrieval_parent_expansion_2026
```

Outputs are written under `output/` by default and are ignored by git.
