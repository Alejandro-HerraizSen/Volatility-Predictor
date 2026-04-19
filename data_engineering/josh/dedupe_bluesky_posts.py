import pandas as pd

input_path = "data/processed/bluesky_posts_combined.csv"
output_path = "data/processed/bluesky_posts_combined_deduped.csv"

df = pd.read_csv(input_path)

before_rows = len(df)

df_deduped = df.drop_duplicates(subset=["event_id", "author_handle", "text_raw"]).copy()

after_rows = len(df_deduped)
removed_rows = before_rows - after_rows

df_deduped.to_csv(output_path, index=False)

print("Rows before dedupe:", before_rows)
print("Rows after dedupe:", after_rows)
print("Duplicates removed:", removed_rows)
print("Saved file:", output_path)