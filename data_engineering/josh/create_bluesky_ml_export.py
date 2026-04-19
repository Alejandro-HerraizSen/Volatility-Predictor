import pandas as pd

input_path = "data/processed/bluesky_posts_combined_deduped.csv"
output_path = "data/processed/bluesky_posts_ml_ready.csv"

df = pd.read_csv(input_path)

ml_df = df[
    [
        "event_id",
        "ticker",
        "company_name",
        "created_at",
        "author_handle",
        "text_raw",
        "relevance_label",
        "match_score",
        "post_uri"
    ]
].copy()

ml_df.to_csv(output_path, index=False)

print("Rows exported:", len(ml_df))
print("Columns exported:", len(ml_df.columns))
print("Saved file:", output_path)