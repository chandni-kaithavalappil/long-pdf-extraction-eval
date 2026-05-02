# Full-Context Dump

## What this method does

Full-Context Dump extracts text from the PDF with `pypdf`, concatenates the entire document into one prompt, and asks the model to answer each eval question directly. It is the control method for this repo.

This method has no retrieval index, no chunk ranking, and no parent expansion. It is useful as a baseline because failures are easy to interpret: if the answer is wrong, the model either lost the relevant context, misread table text, or hallucinated from a long prompt.

## Files

- `run.py` — end-to-end runner for this method
- `README.md` — this document

Shared repo files used by this method:

- `pipeline/config.py`
- `pipeline/util.py`
- `eval/ground_truth.json`

## How to run

From repo root:

```bash
python3 pipeline/full_context_dump/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name full_context_dump_2026
```

For another PDF, put it in `pdfs/`, update or create a config file, and run with a new `--run-name`.

## Known limitations from this experiment

- It answered negative questions instead of refusing.
- It frequently missed table values when the question entity and number were separated.
- It has poor auditability because the retrieved evidence is just whatever the model selected from a large prompt.
