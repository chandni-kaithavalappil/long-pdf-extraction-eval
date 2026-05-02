# Long PDF Extraction Eval

Reference implementation and evaluation dashboard for comparing long-PDF extraction approaches on structured budget PDFs.

Core pieces:

- `pipeline/` — parsing, chunking, indexing, retrieval, extraction, and eval scripts
- `pipeline/method3_parent_expansion.py` — hierarchical retrieval with parent expansion
- `pipeline/method3/README.md` — developer notes for Method 3
- `eval/ground_truth.json` — evaluation questions
- `dashboard/dashboard.html` — self-contained comparison dashboard
- `configs/` — example run configs

PDF inputs and generated outputs are intentionally ignored by git. Place PDFs under `pdfs/` locally before running.
