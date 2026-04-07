import re
import pandas as pd
from pathlib import Path
from sentiment_score import analyze_sentiment

CONFIDENCE_WORDS = [
    "confident", "confidence", "optimistic", "strong", "growth",
    "improved", "raise guidance", "raising guidance", "momentum",
    "stable demand", "opportunity", "well positioned"
]

RISK_WORDS = [
    "risk", "risks", "uncertainty", "uncertain", "pressure",
    "headwind", "headwinds", "decline", "challenging", "challenge",
    "volatile", "macroeconomic", "inflation", "supply chain"
]


def read_transcript(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_lines(text):
    lines = text.strip().splitlines()
    return [line.strip() for line in lines if line.strip()]


def extract_speaker_and_text(line):
    match = re.match(r"^([A-Za-z]+):\s*(.*)", line)
    if match:
        speaker = match.group(1)
        content = match.group(2)
    else:
        speaker = "Unknown"
        content = line
    return speaker, content


def count_keywords(text, keywords):
    text_lower = text.lower()
    count = 0
    for word in keywords:
        if word in text_lower:
            count += 1
    return count


def process_transcript(file_path):
    text = read_transcript(file_path)
    lines = split_lines(text)

    results = []

    for i, line in enumerate(lines, start=1):
        speaker, content = extract_speaker_and_text(line)

        if not content.strip():
            continue

        sentiment, confidence, _ = analyze_sentiment(content)

        confidence_count = count_keywords(content, CONFIDENCE_WORDS)
        risk_count = count_keywords(content, RISK_WORDS)

        results.append({
            "segment_id": i,
            "speaker": speaker,
            "text": content,
            "sentiment": sentiment,
            "sentiment_confidence": confidence,
            "confidence_keyword_count": confidence_count,
            "risk_keyword_count": risk_count
        })

    if not results:
        return pd.DataFrame(columns=[
            "segment_id",
            "speaker",
            "text",
            "sentiment",
            "sentiment_confidence",
            "confidence_keyword_count",
            "risk_keyword_count"
        ])

    return pd.DataFrame(results)


def summarize_features(df):
    if df.empty:
        summary = {
            "total_segments": 0,
            "positive_segments": 0,
            "neutral_segments": 0,
            "negative_segments": 0,
            "total_confidence_keywords": 0,
            "total_risk_keywords": 0,
        }

        speaker_summary = pd.DataFrame(columns=[
            "speaker",
            "segments",
            "positive_segments",
            "negative_segments",
            "avg_model_confidence",
            "confidence_keywords",
            "risk_keywords"
        ])

        return summary, speaker_summary

    summary = {
        "total_segments": len(df),
        "positive_segments": (df["sentiment"] == "positive").sum(),
        "neutral_segments": (df["sentiment"] == "neutral").sum(),
        "negative_segments": (df["sentiment"] == "negative").sum(),
        "total_confidence_keywords": df["confidence_keyword_count"].sum(),
        "total_risk_keywords": df["risk_keyword_count"].sum(),
    }

    speaker_summary = (
        df.groupby("speaker")
        .agg(
            segments=("segment_id", "count"),
            positive_segments=("sentiment", lambda x: (x == "positive").sum()),
            negative_segments=("sentiment", lambda x: (x == "negative").sum()),
            avg_model_confidence=("sentiment_confidence", "mean"),
            confidence_keywords=("confidence_keyword_count", "sum"),
            risk_keywords=("risk_keyword_count", "sum"),
        )
        .reset_index()
    )

    return summary, speaker_summary


if __name__ == "__main__":
    transcript_path = Path("data/raw/transcripts/aapl_q1.txt")
    df = process_transcript(transcript_path)

    print("\nSegment-level results:")
    print(df)

    summary, speaker_summary = summarize_features(df)

    print("\nTranscript summary:")
    print(summary)

    print("\nSpeaker summary:")
    print(speaker_summary)

    output_path = Path("data/raw/sample_transcript_scored.csv")
    df.to_csv(output_path, index=False)

    speaker_output_path = Path("data/raw/sample_transcript_speaker_summary.csv")
    speaker_summary.to_csv(speaker_output_path, index=False)

    print(f"\nSaved scored transcript to: {output_path}")
    print(f"Saved speaker summary to: {speaker_output_path}")