# Pipeline Overview

This folder contains shared code plus three intentionally separated extraction methods. The goal is not just to run one pipeline; it is to let users compare three shortlisted architectures against their own long structured PDFs.

## The three shortlisted methods

### 1. Full-Context Dump

This is the control method. It extracts all readable PDF text and gives the model the whole document context. It is simple and useful for sanity checks, but it is not a robust architecture for very long structured PDFs. It can fail because the model ignores distant evidence, misreads tables, or cannot fit the full document into context.

Folder: `pipeline/full_context_dump/`

### 2. Hybrid Retrieval (Flat Chunks)

This is the standard RAG baseline. It parses the PDF, creates chunks, indexes them with BM25 plus a local dense surrogate, retrieves relevant flat chunks, and generates cited answers from those chunks. It is more scalable and auditable than Full-Context Dump, but it can miss evidence when a table row and its explanatory prose are split across neighboring chunks.

Folder: `pipeline/hybrid_retrieval_flat_chunks/`

### 3. Hierarchical Retrieval with Parent Expansion

This is the recommended architecture from the budget experiment. It retrieves precise small chunks first, then expands each hit to its parent section and nearby sibling pages. It targets table-prose interleaving: cases where the name of a scheme appears in prose but the allocation value appears in a nearby table.

Folder: `pipeline/hierarchical_retrieval_parent_expansion/`

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
  chunk.py        # small chunks plus parent_section_id metadata
  index.py        # BM25 plus TF-IDF index build
  bm25.py         # local BM25 implementation
  eval.py         # scoring helper
  config.py       # defaults
  util.py         # JSON/path helpers
```

## How to try your own PDF

1. Put the PDF under `pdfs/`.

```bash
mkdir -p pdfs
cp /path/to/your-document.pdf pdfs/my_document.pdf
```

2. Create a config file under `configs/`.

```yaml
pdf_path: pdfs/my_document.pdf
eval_path: eval/ground_truth.json
output_dir: output
run_name: my_document_experiment
openai_model: gpt-5.5
```

3. Edit `eval/ground_truth.json` for your use case. Start with a small but revealing eval set:

- direct prose lookup
- numeric table lookup
- table/prose interleaving question
- cross-reference question
- negative question that should refuse

4. Run all three methods with different run names.

```bash
python3 pipeline/full_context_dump/run.py \
  --config configs/my_document.yaml \
  --run-name full_context_dump_my_document

python3 pipeline/hybrid_retrieval_flat_chunks/run.py \
  --config configs/my_document.yaml \
  --run-name hybrid_retrieval_flat_chunks_my_document

python3 pipeline/hierarchical_retrieval_parent_expansion/run.py \
  --config configs/my_document.yaml \
  --run-name hierarchical_retrieval_parent_expansion_my_document
```

5. Compare outputs in `output/`.

```text
output/results_full_context_dump_my_document.json
output/results_hybrid_retrieval_flat_chunks_my_document.json
output/results_hierarchical_retrieval_parent_expansion_my_document.json
```

6. Choose the architecture based on failure mode, not just average score:

- If the PDF is short and mostly prose, Full-Context Dump may be enough.
- If answers are usually contained in one retrieved passage, Hybrid Retrieval (Flat Chunks) is a good baseline.
- If names, definitions, tables, and footnotes are split across neighboring layout regions, try Hierarchical Retrieval with Parent Expansion.

## Included budget run examples

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
