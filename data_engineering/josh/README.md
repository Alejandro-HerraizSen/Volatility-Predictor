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
