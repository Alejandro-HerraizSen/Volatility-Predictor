from pathlib import Path

TORCH_IMPORT_ERROR = None

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
except (ImportError, OSError) as exc:
    torch = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None
    TORCH_IMPORT_ERROR = exc

import pandas as pd

# ========================
# 1. LOAD FINBERT (Alex's code)
# ========================
MODEL_NAME = "ProsusAI/finbert"
LOCAL_MODEL_DIR = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--ProsusAI--finbert"
    / "snapshots"
    / "4556d13015211d73dccd3fdd39d39232506f3e43"
)

tokenizer = None
model = None


def load_finbert():
    global tokenizer, model

    if TORCH_IMPORT_ERROR is not None:
        raise RuntimeError(
            "PyTorch/Transformers could not be loaded. "
            "Fix the local torch installation before running FinBERT."
        ) from TORCH_IMPORT_ERROR

    if tokenizer is None or model is None:
        print("Loading FinBERT...")
        model_source = LOCAL_MODEL_DIR if LOCAL_MODEL_DIR.exists() else MODEL_NAME
        local_only = LOCAL_MODEL_DIR.exists()

        tokenizer = AutoTokenizer.from_pretrained(model_source, local_files_only=local_only)
        model = AutoModelForSequenceClassification.from_pretrained(model_source, local_files_only=local_only)
        model.eval()


# ========================
# 2. SENTIMENT FUNCTION (Alex's code)
# ========================
def score_text(text):
    load_finbert()

    inputs = tokenizer(
        str(text),
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    )

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1).squeeze().tolist()

    # FinBERT order: positive, negative, neutral
    positive, negative, neutral = probs

    sent_score = positive - negative

    return positive, neutral, negative, sent_score


# ========================
# 3. APPLY TO CSV (YOU write this)
# ========================
def process_csv(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    if "text" not in df.columns:
        raise ValueError("Input CSV must contain a 'text' column.")

    print(f"Processing {input_path}...")

    results = df["text"].apply(score_text)

    df[["sent_pos", "sent_neu", "sent_neg", "sent_score"]] = pd.DataFrame(
        results.tolist(),
        index=df.index
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")


# ========================
# 4. RUN SCRIPT
# ========================
if __name__ == "__main__":
    input_file = "data/raw/sample_transcript_scored.csv"
    output_file = "data/processed/sample_transcript_scored.csv"

    process_csv(input_file, output_file)
