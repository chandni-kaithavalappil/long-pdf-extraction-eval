# Long PDF Extraction Eval

Reference implementation and evaluation dashboard for comparing extraction approaches on long structured PDFs such as annual reports, government budgets, and regulatory filings.

The repo is organized around three shortlisted methods. They are intentionally separated so users can try each architecture on their own PDF and compare failure modes.

## Methods

1. `pipeline/full_context_dump/` — Full-Context Dump. A control method that sends the extracted document text directly to the model.
2. `pipeline/hybrid_retrieval_flat_chunks/` — Hybrid Retrieval (Flat Chunks). A standard RAG baseline using BM25 plus local TF-IDF retrieval over flat chunks.
3. `pipeline/hierarchical_retrieval_parent_expansion/` — Hierarchical Retrieval with Parent Expansion. A small-to-big retrieval method that expands retrieved chunks to parent sections and neighboring pages.

## Trying your own PDF

1. Copy your PDF into `pdfs/`.
2. Create a config file in `configs/` with `pdf_path`, `eval_path`, `output_dir`, `run_name`, and `openai_model`.
3. Edit `eval/ground_truth.json` with questions for your document.
4. Run each method with a distinct `--run-name`.
5. Compare JSON results in `output/` and inspect which failure mode each method exposes.

Start here for detailed instructions:

- `pipeline/README.md`
- `pipeline/full_context_dump/README.md`
- `pipeline/hybrid_retrieval_flat_chunks/README.md`
- `pipeline/hierarchical_retrieval_parent_expansion/README.md`

## Dashboard

Public dashboard:

```text
https://chandni-kaithavalappil.github.io/long-pdf-extraction-eval/dashboard/dashboard.html
```

Local dashboard:

```text
dashboard/dashboard.html
```

## Notes

Source PDFs and generated outputs are ignored by git. A fresh clone should provide its own PDFs or recreate generated run artifacts locally.
