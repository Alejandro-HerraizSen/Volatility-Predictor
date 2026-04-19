import glob
import os
import pandas as pd

file_paths = glob.glob("data/processed/bluesky_*.csv")

file_paths = [
    p for p in file_paths
    if "event_input" not in p
    and "combined" not in p
    and "ml_ready" not in p
]

dfs = []
for path in sorted(file_paths):
    df = pd.read_csv(path)
    df["source_file"] = os.path.basename(path)
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)

output_path = "data/processed/bluesky_posts_combined.csv"
combined.to_csv(output_path, index=False)

print("Files combined:", len(file_paths))
print("Total rows:", len(combined))
print("Saved file:", output_path)
print("\nFirst 10 source files:")
for p in sorted(file_paths)[:10]:
    print(os.path.basename(p))