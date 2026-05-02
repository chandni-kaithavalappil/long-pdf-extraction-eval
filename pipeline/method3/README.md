# Hierarchical Retrieval with Parent Expansion

## 1. WHAT THIS IS

This is a reference implementation of hierarchical retrieval for long PDFs: retrieve small chunks first, then expand each hit to a larger parent section before generation. This is a known pattern, not a novel architecture: LangChain calls related approaches “Parent Document Retriever” or small-to-big retrieval, and LlamaIndex has related “auto-merging retriever” patterns.

The implementation here is intentionally narrow. It was built to test whether parent expansion fixes one observed failure mode in budget-style PDFs.

## 2. WHY

The target failure mode is table-prose interleaving in long structured documents. In these PDFs, the scheme name often appears in a prose/notes chunk, while the actual BE allocation sits in a neighboring table chunk. Flat retrieval can find the prose definition and still miss the sibling table row that contains the number.

That exact pattern showed up in the first two methods in this experiment: the Full-Context Dump and Hybrid Retrieval (Flat Chunks) runs failed or partially failed Q1, Q2, Q5, and Q7. Those questions involve VB-G RAM G, PMAY-Urban, PMVBRY, and NSAP — all cases where the entity/definition and allocation/value were split across nearby table/prose regions.

## 3. ARCHITECTURE

Parser: this uses the existing `parse.py`, based on `pypdf` layout text extraction. We kept it unchanged to isolate the retrieval change. We rejected swapping in Docling, Unstructured, Marker, or OCR here because that would confound the experiment: better table parsing might improve results for reasons unrelated to parent expansion.

Chunking: this reuses the existing chunker with about `CHUNK_TOKENS_APPROX = 900` tokens, plus metadata. Method 3 adds `parent_section_id`, derived from ministry, demand, and nearest scheme/section heading. We rejected very large chunks because they reduce retrieval precision and recreate the “stuff too much context” problem.

Indexing: the implementation uses the existing hybrid local index: BM25 plus a TF-IDF dense surrogate from scikit-learn. No hosted embedding model is used in this repo by default. The config has `EMBEDDING_BACKEND = "tfidf"`. We rejected adding a hosted embedding dependency because the point was to keep the repo runnable offline and preserve comparability with the previous flat-chunk run.

Retrieval: retrieve top small chunks first using the existing retriever (`TOP_K = 18`, `RERANK_K = 8`), then expand each hit to its parent section and nearby pages, usually a 1-3 page window. We do not retrieve parents directly because parent sections are larger and noisier; retrieving small chunks first keeps lexical precision, then expansion restores missing sibling table/prose context.

Generation: output stays the same forced-citation schema: each claim must include `{answer, page, quote}` plus `refusal_reason`. If grounding is not found, the method must refuse. This is unchanged from the original agentic pipeline so the comparison isolates retrieval context construction.

## 4. HOW TO RUN ON YOUR OWN PDF

Put your PDF in:

```bash
./pdfs/your_document.pdf
```

Edit `pipeline/config.py`:

```python
PDF_PATH = Path("../pdfs/your_document.pdf")
RUN_NAME = "your_document_method3"
TOPIC = "your topic of interest"
```

Then run:

```bash
python3 pipeline/method3_parent_expansion.py \
  --config configs/budget_2026_27.yaml \
  --run-name method3_custom
```

For a new config, create a simple YAML file like:

```yaml
pdf_path: pdfs/your_document.pdf
eval_path: eval/ground_truth.json
output_dir: output
run_name: method3_custom
openai_model: gpt-5.5
```

The output is written to:

```bash
./output/results_<run-name>.json
```

Each result contains the question, prediction, score, retrieved chunks, expanded parent contexts, and claims in this shape:

```json
{
  "claims": [{"answer": "...", "page": 123, "quote": "..."}],
  "refusal_reason": null
}
```

## 5. WHAT IT WON'T HANDLE

Name disambiguation is still weak. Q5 showed that even with parent expansion, similarly named employment schemes and prose/table variants can confuse retrieval and answer selection.

Cross-document references were not tested. This method only expands within one parsed PDF.

Image-heavy or scanned PDFs are not handled well. The parser is text-only `pypdf`; OCR/table-native parsing is outside this method.

Aggregation queries spanning many sections remain hard. Q8 is the stress case: it requires collecting multiple qualifying schemes, not just expanding one parent section.

Schema drift across years is only partly addressed. The 2025 run showed mixed results. If the document reorganizes sections substantially, parent IDs based on nearby headings can drift.

Page alignment is also imperfect. Some answers found the right value but failed expected-page checks because extracted PDF page numbers and eval page references did not always line up.

## 6. FORK + EXTEND

Good extension points:

1. Swap `parse.py` for Docling or another table-aware parser so table rows become structured records instead of flattened text.

2. Add a name-disambiguation reranker for Q5-class failures, using exact scheme aliases and ministry/demand constraints.

3. Add aggregation logic for Q8-class questions: retrieve multiple parent sections, extract candidate rows, then filter/sort by numeric allocation.
