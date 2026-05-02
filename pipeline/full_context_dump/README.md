# Full-Context Dump

## What this architecture means

Full-Context Dump is the simplest control architecture: extract all readable text from the PDF, concatenate it into one large context, and ask the model to answer each evaluation question directly from that full text.

It is intentionally not optimized. There is no retrieval index, no chunk ranking, and no parent expansion. That makes it useful as a baseline: it answers the question, "What happens if I give the model everything and hope it finds the right evidence?"

Use this method when you want a sanity check before building a retrieval pipeline. If Full-Context Dump performs well, your PDF may be short, mostly prose, and structurally easy. If it performs poorly, the failure often points to long-context degradation, table extraction issues, or unsupported citation grounding.

## How to try this with your own PDF

1. Put your PDF in the repo, usually under `pdfs/`:

```bash
mkdir -p pdfs
cp /path/to/your-document.pdf pdfs/my_document.pdf
```

2. Create a config file under `configs/`, for example `configs/my_document.yaml`:

```yaml
pdf_path: pdfs/my_document.pdf
eval_path: eval/ground_truth.json
output_dir: output
run_name: full_context_dump_my_document
openai_model: gpt-5.5
```

3. Update `eval/ground_truth.json` with questions that matter for your PDF. Keep the questions topic-specific and include expected answers, pages, and quotes when you know them. For early exploration, start with 5-10 questions: direct lookup, table lookup, cross-reference, and negative/refusal cases.

4. Run the method:

```bash
python3 pipeline/full_context_dump/run.py \
  --config configs/my_document.yaml \
  --run-name full_context_dump_my_document
```

5. Review the output:

```bash
output/results_full_context_dump_my_document.json
```

6. Interpret results carefully. A good score here does not prove the architecture is scalable. A bad score is still useful because it tells you that full-context prompting is not enough for your document.

## Files

- `run.py` — end-to-end runner for this method
- `README.md` — this document

Shared repo files used by this method:

- `pipeline/config.py`
- `pipeline/util.py`
- `eval/ground_truth.json`

## How to run the included budget example

From repo root:

```bash
python3 pipeline/full_context_dump/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name full_context_dump_2026
```

## Known limitations from this experiment

- It frequently misses or misreads table values when entity names and numbers are separated.
- It has weak auditability because there is no explicit retrieval trace.
- It can over-answer when the correct behavior is refusal.
- It becomes expensive or impossible when the PDF text exceeds the model context window.
