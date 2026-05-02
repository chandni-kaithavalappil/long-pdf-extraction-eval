# Long PDF Extraction Eval

Reference implementation and evaluation dashboard for comparing long-PDF extraction approaches on structured budget PDFs.

## Method folders

The three evaluated methods are intentionally separated under `pipeline/`:

- `pipeline/full_context_dump/` — Full-Context Dump baseline
- `pipeline/hybrid_retrieval_flat_chunks/` — Hybrid Retrieval (Flat Chunks)
- `pipeline/hierarchical_retrieval_parent_expansion/` — Hierarchical Retrieval with Parent Expansion

Each folder has its own `README.md` and runnable `run.py`.

## Shared pipeline modules

The method folders reuse shared components in `pipeline/`:

- `parse.py` — text extraction from PDFs
- `chunk.py` — chunking and parent-section metadata
- `index.py` / `bm25.py` — local indexing
- `eval.py` — scoring helper
- `config.py` — default configuration

## Other repo contents

- `eval/ground_truth.json` — evaluation questions
- `dashboard/dashboard.html` — self-contained comparison dashboard
- `configs/` — example run configs

PDF inputs and generated outputs are intentionally ignored by git. Place PDFs under `pdfs/` locally before running.
