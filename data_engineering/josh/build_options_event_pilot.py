import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("POLYGON_API_KEY")
if not api_key:
    raise ValueError("Missing POLYGON_API_KEY")

if len(sys.argv) != 2:
    raise ValueError("Usage: python src/collect/build_options_event_pilot.py <event_input_csv>")

input_path = sys.argv[1]
event_df = pd.read_csv(input_path)

if len(event_df) == 0:
    raise ValueError("Input CSV contains no rows")

os.makedirs("data/processed", exist_ok=True)

# Conservative pacing settings
UNDERLYING_LOOKUP_SLEEP = 2
EMPTY_RESPONSE_SLEEP = 3
CONTRACT_BETWEEN_SLEEP = 8
EVENT_BETWEEN_SLEEP = 15
RATE_LIMIT_BASE_SLEEP = 15
MAX_BAR_ATTEMPTS = 5
REQUEST_TIMEOUT = 30

summary_rows = []


def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}


def first_friday_strictly_after(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
    while dt.weekday() != 4:
        dt += timedelta(days=1)
    return dt.strftime("%Y-%m-%d")


def get_underlying_close_with_fallback(ticker, earnings_date):
    for i in range(0, 6):
        check_dt = datetime.strptime(earnings_date, "%Y-%m-%d") - timedelta(days=i)
        check_date = check_dt.strftime("%Y-%m-%d")

        agg_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{check_date}/{check_date}"
        resp = requests.get(
            agg_url,
            params={
                "adjusted": "true",
                "sort": "asc",
                "limit": 10,
                "apiKey": api_key
            },
            timeout=REQUEST_TIMEOUT
        )

        data = safe_json(resp)
        results = data.get("results", [])
        message = data.get("message", "")

        if resp.status_code == 403:
            raise ValueError(
                f"Not authorized for underlying price lookup on {check_date}: {message}"
            )

        if resp.status_code == 429:
            wait_seconds = RATE_LIMIT_BASE_SLEEP * (i + 1)
            print(f"{ticker} underlying lookup -> RATE_LIMITED on {check_date}, waiting {wait_seconds}s")
            time.sleep(wait_seconds)
            continue

        if resp.status_code != 200:
            print(f"{ticker} underlying lookup -> HTTP_{resp.status_code} on {check_date} | {message}")
            time.sleep(UNDERLYING_LOOKUP_SLEEP)
            continue

        if results:
            underlying_close = results[0].get("c")
            return underlying_close, check_date

        time.sleep(UNDERLYING_LOOKUP_SLEEP)

    raise ValueError(
        f"Could not get underlying close for {ticker} on {earnings_date} or prior fallback dates"
    )


def lookup_option_contracts(ticker, expiration_date, selected_strikes):
    contracts_url = "https://api.polygon.io/v3/reference/options/contracts"
    resp = requests.get(
        contracts_url,
        params={
            "underlying_ticker": ticker,
            "expiration_date": expiration_date,
            "expired": "true",
            "limit": 1000,
            "apiKey": api_key,
        },
        timeout=REQUEST_TIMEOUT,
    )

    data = safe_json(resp)
    message = data.get("message", "")

    if resp.status_code == 403:
        raise ValueError(f"Not authorized for options contract lookup: {message}")

    if resp.status_code == 429:
        raise ValueError(f"Rate limited during contract lookup: {message}")

    if resp.status_code != 200:
        raise ValueError(f"Contract lookup failed with HTTP {resp.status_code}: {message}")

    contracts = data.get("results", [])

    selected_contracts = []
    for contract in contracts:
        strike = contract.get("strike_price")
        contract_type = contract.get("contract_type")

        if strike in selected_strikes and contract_type in {"call", "put"}:
            selected_contracts.append({
                "option_ticker": contract.get("ticker"),
                "strike": strike,
                "contract_type": contract_type,
            })

    return selected_contracts


def fetch_option_bars(option_ticker, start_date, end_date):
    bars_url = f"https://api.polygon.io/v2/aggs/ticker/{option_ticker}/range/1/day/{start_date}/{end_date}"

    results = []
    last_message = ""
    last_status_code = None

    for attempt in range(MAX_BAR_ATTEMPTS):
        resp = requests.get(
            bars_url,
            params={
                "adjusted": "true",
                "sort": "asc",
                "limit": 5000,
                "apiKey": api_key
            },
            timeout=REQUEST_TIMEOUT,
        )

        data = safe_json(resp)
        last_message = data.get("message", "")
        last_status_code = resp.status_code
        results = data.get("results", [])

        if resp.status_code == 403:
            print(f"{option_ticker} -> NOT_AUTHORIZED | {last_message}")
            return [], resp.status_code, last_message

        if resp.status_code == 429:
            wait_seconds = RATE_LIMIT_BASE_SLEEP * (attempt + 1)
            print(f"{option_ticker} -> RATE_LIMITED | retrying in {wait_seconds}s")
            time.sleep(wait_seconds)
            continue

        if resp.status_code != 200:
            print(f"{option_ticker} -> HTTP_{resp.status_code} | {last_message}")
            time.sleep(EMPTY_RESPONSE_SLEEP)
            continue

        if results:
            return results, resp.status_code, last_message

        time.sleep(EMPTY_RESPONSE_SLEEP)

    return results, last_status_code, last_message


for idx, event in event_df.iterrows():
    event_id = event["event_id"]
    ticker = event["ticker"]
    earnings_date = event["earnings_date"]

    print("=" * 100)
    print(f"[{idx + 1}/{len(event_df)}] Processing {event_id}")

    try:
        expiration_date = first_friday_strictly_after(earnings_date)

        underlying_close, price_date = get_underlying_close_with_fallback(ticker, earnings_date)

        # Narrower strike band to reduce request load
        center_strike = round(underlying_close / 5) * 5
        selected_strikes = {
            center_strike - 5,
            center_strike,
            center_strike + 5,
        }

        selected_contracts = lookup_option_contracts(ticker, expiration_date, selected_strikes)

        if not selected_contracts:
            raise ValueError(
                f"No option contracts found for {ticker} with expiration {expiration_date}"
            )

        earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
        start_date = (earnings_dt - timedelta(days=1)).strftime("%Y-%m-%d")

        post_dt = earnings_dt + timedelta(days=1)
        while post_dt.weekday() >= 5:
            post_dt += timedelta(days=1)
        post_day_1 = post_dt.strftime("%Y-%m-%d")

        end_date = expiration_date

        rows = []
        contracts_with_bars = 0

        for contract in selected_contracts:
            option_ticker = contract["option_ticker"]

            results, status_code, message = fetch_option_bars(
                option_ticker=option_ticker,
                start_date=start_date,
                end_date=end_date
            )

            print(f"{option_ticker} -> bars returned: {len(results)}")

            if results:
                contracts_with_bars += 1

            for bar in results:
                bar_date = pd.to_datetime(bar["t"], unit="ms", utc=True).date().isoformat()

                relative_day = {
                    start_date: "pre_earnings_day",
                    earnings_date: "earnings_day",
                    post_day_1: "post_day_1",
                    expiration_date: "expiration_day",
                }.get(bar_date)

                rows.append({
                    "event_id": event_id,
                    "underlying_ticker": ticker,
                    "earnings_date": earnings_date,
                    "expiration_date": expiration_date,
                    "underlying_price_date_used": price_date,
                    "option_ticker": option_ticker,
                    "strike": contract["strike"],
                    "contract_type": contract["contract_type"],
                    "bar_date": bar_date,
                    "relative_day": relative_day,
                    "open": bar.get("o"),
                    "high": bar.get("h"),
                    "low": bar.get("l"),
                    "close": bar.get("c"),
                    "volume": bar.get("v"),
                    "vwap": bar.get("vw"),
                    "transactions": bar.get("n"),
                })

            time.sleep(CONTRACT_BETWEEN_SLEEP)

        df = pd.DataFrame(rows)
        output_path = f"data/processed/options_{event_id}_bars.csv"
        df.to_csv(output_path, index=False)

        print("Event ID:", event_id)
        print("Ticker:", ticker)
        print("Earnings date:", earnings_date)
        print("Expiration date:", expiration_date)
        print("Underlying close:", underlying_close)
        print("Underlying price date used:", price_date)
        print("Center strike:", center_strike)
        print("Selected strikes:", sorted(selected_strikes))
        print("Selected contracts:", len(selected_contracts))
        print("Contracts with bars:", contracts_with_bars)
        print("Rows written:", len(df))
        print("Saved file:", output_path)

        summary_rows.append({
            "event_id": event_id,
            "ticker": ticker,
            "earnings_date": earnings_date,
            "expiration_date": expiration_date,
            "status": "SUCCESS",
            "underlying_price_date_used": price_date,
            "underlying_close": underlying_close,
            "center_strike": center_strike,
            "selected_contracts": len(selected_contracts),
            "contracts_with_bars": contracts_with_bars,
            "rows_written": len(df),
            "output_path": output_path,
            "error_message": "",
        })

    except Exception as e:
        print(f"FAILED: {event_id} -> {e}")

        summary_rows.append({
            "event_id": event_id,
            "ticker": ticker,
            "earnings_date": earnings_date,
            "expiration_date": "",
            "status": "FAILED",
            "underlying_price_date_used": "",
            "underlying_close": "",
            "center_strike": "",
            "selected_contracts": 0,
            "contracts_with_bars": 0,
            "rows_written": 0,
            "output_path": "",
            "error_message": str(e),
        })

    time.sleep(EVENT_BETWEEN_SLEEP)

summary_df = pd.DataFrame(summary_rows)
summary_output_path = "data/processed/options_event_pilot_summary.csv"
summary_df.to_csv(summary_output_path, index=False)

print("\n" + "=" * 100)
print("FINAL SUMMARY")
print(summary_df["status"].value_counts(dropna=False))
print("Saved summary:", summary_output_path)