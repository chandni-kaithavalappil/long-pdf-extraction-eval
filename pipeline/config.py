
from pathlib import Path

# Swap years by changing only these two values.
PDF_PATH = Path("../pdfs/budget_2026_27.pdf")
RUN_NAME = "budget_2026_27_working_class"

TOPIC = "schemes and allocations that directly affect India's working class: employment, rural livelihoods, housing, social assistance, labour, skilling, agriculture credit, tribal welfare, footwear/leather jobs"

SCHEMA = {
    "type": "object",
    "required": ["claims"],
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["answer", "page", "quote"],
                "properties": {
                    "answer": {"type": "string"},
                    "page": {"type": ["integer", "null"]},
                    "quote": {"type": ["string", "null"]}
                }
            }
        },
        "refusal_reason": {"type": ["string", "null"]}
    }
}

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
EVAL_PATH = Path("../eval/ground_truth.json")
CHUNK_TOKENS_APPROX = 900
CHUNK_OVERLAP_CHARS = 1200
TOP_K = 18
RERANK_K = 8
OPENAI_MODEL = "gpt-5.5"
EMBEDDING_BACKEND = "tfidf"  # local deterministic default; replace with hosted embeddings later.
