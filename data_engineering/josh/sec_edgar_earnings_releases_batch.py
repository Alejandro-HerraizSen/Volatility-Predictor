import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

# -----------------------------
# Config
# -----------------------------
INPUT_CSV = Path("data/processed/target_earnings_events_50.csv")
OUTPUT_BASE_DIR = Path("data/raw/sec")
METADATA_OUTPUT_CSV = Path("data/processed/sec_earnings_release_metadata.csv")
FAILURES_OUTPUT_CSV = Path("reports/data_quality/sec_earnings_release_failures.csv")

HEADERS = {
    "User-Agent": "Josh Carlson your_email@example.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}

REQUEST_SLEEP_SECONDS = 0.5


# -----------------------------
# Helpers
# -----------------------------
def get_submissions_json(cik: str) -> dict:
    cik_10 = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_10}.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def get_ticker_to_cik_map() -> dict:
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = HEADERS.copy()
    headers["Host"] = "www.sec.gov"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    ticker_map = {}

    for _, item in data.items():
        ticker = str(item["ticker"]).upper().strip()
        cik_str = str(item["cik_str"]).zfill(10)
        ticker_map[ticker] = cik_str

    return ticker_map


def recent_filings_to_rows(submissions: dict) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {})
    if not recent:
        return []

    keys = list(recent.keys())
    row_count = len(recent[keys[0]])
    rows = []

    for i in range(row_count):
        row = {}
        for key in keys:
            values = recent.get(key, [])
            row[key] = values[i] if i < len(values) else None
        rows.append(row)

    return rows


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def download_text_from_url(url: str) -> str:
    headers = HEADERS.copy()
    headers["Host"] = "www.sec.gov"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return html_to_text(response.text)


def accession_no_dashes(accession: str) -> str:
    return accession.replace("-", "")


def cik_no_leading_zeros(cik: str) -> str:
    return str(int(str(cik)))


def pick_best_8k(rows: list[dict], earnings_date: str) -> dict | None:
    eight_k_rows = [r for r in rows if r.get("form") == "8-K" and r.get("filingDate")]

    if not eight_k_rows:
        return None

    target_date = pd.to_datetime(earnings_date)

    for row in eight_k_rows:
        row["date_diff"] = abs((pd.to_datetime(row["filingDate"]) - target_date).days)

    eight_k_rows = sorted(eight_k_rows, key=lambda x: x["date_diff"])
    return eight_k_rows[0]


def build_exhibit_url(cik: str, accession: str, primary_doc: str) -> str:
    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_no_leading_zeros(cik)}/"
        f"{accession_no_dashes(accession)}/"
        f"{primary_doc}"
    )


# -----------------------------
# Main
# -----------------------------
def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    required_cols = ["ticker", "earnings_date", "earnings_period", "event_id"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in input CSV: {missing_cols}")

    ticker_to_cik = get_ticker_to_cik_map()
    time.sleep(REQUEST_SLEEP_SECONDS)

    metadata_rows = []
    failure_rows = []

    OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    FAILURES_OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    print(f"Total events to process: {len(df)}")

    for idx, row in df.iterrows():
        ticker = str(row["ticker"]).strip().upper()
        earnings_date = str(row["earnings_date"]).strip()
        earnings_period = str(row["earnings_period"]).strip()
        event_id = str(row["event_id"]).strip()

        print(f"\nProcessing {idx + 1}/{len(df)}: {event_id}")

        try:
            cik = ticker_to_cik.get(ticker)
            if not cik:
                raise ValueError(f"No CIK found for ticker: {ticker}")

            submissions = get_submissions_json(cik)
            time.sleep(REQUEST_SLEEP_SECONDS)

            filing_rows = recent_filings_to_rows(submissions)
            best_8k = pick_best_8k(filing_rows, earnings_date)

            if not best_8k:
                raise ValueError("No recent 8-K found")

            accession_number = best_8k["accessionNumber"]
            primary_document = best_8k["primaryDocument"]
            filing_date = best_8k["filingDate"]

            exhibit_url = build_exhibit_url(cik, accession_number, primary_document)
            text = download_text_from_url(exhibit_url)
            time.sleep(REQUEST_SLEEP_SECONDS)

            company_dir = OUTPUT_BASE_DIR / ticker
            company_dir.mkdir(parents=True, exist_ok=True)

            txt_path = company_dir / f"{event_id}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            metadata_rows.append(
                {
                    "event_id": event_id,
                    "ticker": ticker,
                    "cik": cik,
                    "earnings_date": earnings_date,
                    "earnings_period": earnings_period,
                    "filing_date": filing_date,
                    "accession_number": accession_number,
                    "source": "SEC EDGAR",
                    "source_url": exhibit_url,
                    "document_type": "earnings_release",
                    "is_transcript": False,
                    "local_txt_path": str(txt_path),
                }
            )

            print(f"Saved: {txt_path}")

        except Exception as e:
            failure_rows.append(
                {
                    "event_id": event_id,
                    "ticker": ticker,
                    "earnings_date": earnings_date,
                    "error": str(e),
                }
            )
            print(f"Failed: {event_id} | {e}")

    metadata_df = pd.DataFrame(metadata_rows)
    failures_df = pd.DataFrame(failure_rows)

    metadata_df.to_csv(METADATA_OUTPUT_CSV, index=False)
    failures_df.to_csv(FAILURES_OUTPUT_CSV, index=False)

    print("\nDone.")
    print(f"Successful downloads: {len(metadata_df)}")
    print(f"Failures: {len(failures_df)}")
    print(f"Metadata saved to: {METADATA_OUTPUT_CSV}")
    print(f"Failures saved to: {FAILURES_OUTPUT_CSV}")


if __name__ == "__main__":
    main()