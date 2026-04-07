from pathlib import Path
import pandas as pd
from process_transcript import process_transcript, summarize_features

def extract_transcript_features(file_path):
    df = process_transcript(file_path)
    summary, speaker_summary = summarize_features(df)

    features = {
        "transcript_file": file_path.name,
        "total_segments": int(summary["total_segments"]),
        "positive_segments": int(summary["positive_segments"]),
        "neutral_segments": int(summary["neutral_segments"]),
        "negative_segments": int(summary["negative_segments"]),
        "total_confidence_keywords": int(summary["total_confidence_keywords"]),
        "total_risk_keywords": int(summary["total_risk_keywords"]),
    }

    for speaker in ["CEO", "CFO", "Analyst", "Unknown"]:
        speaker_df = speaker_summary[speaker_summary["speaker"] == speaker]

        if not speaker_df.empty:
            row = speaker_df.iloc[0]
            features[f"{speaker.lower()}_segments"] = int(row["segments"])
            features[f"{speaker.lower()}_positive_segments"] = int(row["positive_segments"])
            features[f"{speaker.lower()}_negative_segments"] = int(row["negative_segments"])
            features[f"{speaker.lower()}_avg_model_confidence"] = float(row["avg_model_confidence"])
            features[f"{speaker.lower()}_confidence_keywords"] = int(row["confidence_keywords"])
            features[f"{speaker.lower()}_risk_keywords"] = int(row["risk_keywords"])
        else:
            features[f"{speaker.lower()}_segments"] = 0
            features[f"{speaker.lower()}_positive_segments"] = 0
            features[f"{speaker.lower()}_negative_segments"] = 0
            features[f"{speaker.lower()}_avg_model_confidence"] = 0.0
            features[f"{speaker.lower()}_confidence_keywords"] = 0
            features[f"{speaker.lower()}_risk_keywords"] = 0
    
    return features

def build_feature_table(transcripts_folder):
    transcript_files = list(Path(transcripts_folder).glob("*.txt"))

    all_features = []
    for file_path in transcript_files:
        features = extract_transcript_features(file_path)
        all_features.append(features)
    
    return pd.DataFrame(all_features)

if __name__ == "__main__":
    transcripts_folder = Path("data/raw/transcripts")
    features_df = build_feature_table(transcripts_folder)

    print("\Feature table:")
    print(features_df)

    output_path = Path("data/processed/transcript_feature_table.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(output_path, index=False)

    print(f"\nFeature table saved to {output_path}")
