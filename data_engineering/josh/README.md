## 1. Bluesky Files

The Bluesky files contain social media posts collected around earnings events.

### Contents
- One CSV file per earnings event
- Combined Bluesky output files
- Deduplicated and ML-ready exports

### Main fields
Typical columns include:
- `event_id`
- `ticker`
- `company_name`
- `created_at`
- `author_handle`
- `text_raw`
- `relevance_label`
- `match_score`
- `post_uri`

### Purpose
These files are meant to give the ML team social discussion data tied to specific earnings events.

---

## 2. Options Data

The options files contain daily option bar data for selected contracts around each earnings event.

### Contents
- One CSV file per accessible earnings event
- A summary file showing which events succeeded or failed

### Main fields
Typical columns include:
- `event_id`
- `underlying_ticker`
- `earnings_date`
- `expiration_date`
- `underlying_price_date_used`
- `option_ticker`
- `strike`
- `contract_type`
- `bar_date`
- `relative_day`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `vwap`
- `transactions`

### Purpose
These files are meant to give the ML team event-window options market data for earnings-related analysis.

### Notes
- Only the earnings events supported by the current Polygon access plan were collected
- Most files cover selected near-the-money call and put contracts
- The summary file documents the overall collection results

---

## 3. Transcript / SEC EDGAR Files

These files contain text-based earnings-related documents collected for each event.

### Contents
- One text file per earnings event
- Metadata CSV linking each event to its source file and source information

### File types
There are two main document types:
- **Transcript text files**: full earnings call transcript text where available
- **SEC EDGAR text files**: earnings release or filing text extracted from SEC documents

### Metadata fields
Typical metadata includes:
- `event_id`
- `ticker`
- `earnings_date`
- `source`
- `source_url`
- `local_txt_path`

### Purpose
These files are meant to give the ML team the text source for each event, including transcripts when available and SEC earnings-release text as a structured fallback.

---

## Summary

This deliverable package is organized to support downstream ML work across three areas:

- **Social data** from Bluesky
- **Market data** from options price activity
- **Text data** from transcripts and SEC EDGAR documentsJosh data engineering deliverables

- # Bluesky Data Collection Pipeline

This part of the project collects Bluesky posts related to earnings events and prepares them for ML use.

## Files

### `src/collect/bluesky_collect_simple.py`
This script collects Bluesky posts for **one earnings event**.

It:
- logs into Bluesky using environment variables
- searches posts using the query: `<TICKER> earnings`
- scores posts for relevance using ticker, company name, and earnings-related terms
- keeps only medium/high relevance posts
- saves the results to a CSV file

**Output example:**
`data/processed/bluesky_<event_id>.csv`

---

### `src/collect/run_bluesky_batch.py`
This script runs the Bluesky scraper for **multiple events**.

It:
- reads the input file `data/processed/bluesky_event_input_50.csv`
- takes each event’s `event_id`, `ticker`, and `company_name`
- calls `bluesky_collect_simple.py` for each row

This is the batch runner for the full Bluesky collection process.

---

### `src/process/combine_bluesky_outputs.py`
This script combines all individual Bluesky event CSV files into one dataset.

**Output example:**
`data/processed/bluesky_posts_combined.csv`

---

### `src/process/dedupe_bluesky_posts.py`
This script removes duplicate Bluesky posts from the combined dataset.

**Output example:**
`data/processed/bluesky_posts_combined_deduped.csv`

---

### `src/process/create_bluesky_ml_export.py`
This script creates the final ML-ready Bluesky export.

It keeps the cleaned and relevant columns needed for downstream modeling.

**Output example:**
`data/processed/bluesky_posts_ml_ready.csv`

---

## Pipeline Flow

1. `bluesky_collect_simple.py` → collect posts for one event  
2. `run_bluesky_batch.py` → run collection for all events  
3. `combine_bluesky_outputs.py` → combine all event files  
4. `dedupe_bluesky_posts.py` → remove duplicate posts  
5. `create_bluesky_ml_export.py` → build final ML-ready dataset  

---

## Input File

The batch process uses:

`data/processed/bluesky_event_input_50.csv`

This file contains:
- `event_id`
- `ticker`
- `company_name`

---

## Final Output

The final dataset for the ML team is:

`data/processed/bluesky_posts_ml_ready.csv`

This contains earnings-related Bluesky posts matched to target events and cleaned for downstream analysis.
