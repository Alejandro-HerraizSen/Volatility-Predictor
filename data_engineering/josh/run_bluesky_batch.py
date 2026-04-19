import csv
import subprocess

input_path = "data/processed/bluesky_event_input_50.csv"

with open(input_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        event_id = row["event_id"]
        ticker = row["ticker"]
        company_name = row["company_name"]

        cmd = [
            "python",
            "src/collect/bluesky_collect_simple.py",
            event_id,
            ticker,
            company_name
        ]

        print(f"\nRunning: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)