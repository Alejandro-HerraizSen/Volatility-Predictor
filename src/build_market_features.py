from pathlib import Path

import numpy as np
import pandas as pd


def rolling_slope(series, window):
    values = series.to_numpy(dtype=float)
    slopes = np.full(len(values), np.nan)

    if window < 2:
        return pd.Series(np.zeros(len(series)), index=series.index)

    x = np.arange(window, dtype=float)
    x_mean = x.mean()
    denom = ((x - x_mean) ** 2).sum()

    for i in range(window - 1, len(values)):
        y = values[i - window + 1 : i + 1]

        if np.isnan(y).any():
            continue

        y_mean = y.mean()
        num = ((x - x_mean) * (y - y_mean)).sum()
        slopes[i] = num / denom if denom != 0 else 0.0

    return pd.Series(slopes, index=series.index)


def build_market_features(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    # 1. Load market data
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    required_cols = ["timestamp", "stock_price", "implied_volatility"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).copy()
    if df.empty:
        raise ValueError("No valid rows remain after parsing timestamps.")

    if "ticker" not in df.columns:
        df["ticker"] = "UNKNOWN"
    else:
        df["ticker"] = df["ticker"].fillna("UNKNOWN")

    # 2. Create minute buckets
    df["minute"] = df["timestamp"].dt.floor("min")

    # 3. Aggregate by ticker + minute
    agg_dict = {
        "stock_price": "last",
        "implied_volatility": "last",
    }

    if "option_volume" in df.columns:
        agg_dict["option_volume"] = "sum"

    if "call_iv" in df.columns:
        agg_dict["call_iv"] = "last"

    if "put_iv" in df.columns:
        agg_dict["put_iv"] = "last"

    grouped = (
        df.groupby(["ticker", "minute"])
        .agg(agg_dict)
        .reset_index()
        .sort_values(["ticker", "minute"])
    )

    if grouped.empty:
        raise ValueError("No grouped market features could be created from the input data.")

    # 4. Fill missing minutes for each ticker
    all_ticker_frames = []

    for ticker in grouped["ticker"].unique():
        ticker_df = grouped[grouped["ticker"] == ticker].copy()
        ticker_df = ticker_df.sort_values("minute")

        full_range = pd.date_range(
            start=ticker_df["minute"].min(),
            end=ticker_df["minute"].max(),
            freq="min",
        )

        full_df = pd.DataFrame({"minute": full_range})
        full_df["ticker"] = ticker

        ticker_df = full_df.merge(ticker_df, on=["ticker", "minute"], how="left")

        ticker_df["stock_price"] = ticker_df["stock_price"].ffill().bfill()
        ticker_df["implied_volatility"] = ticker_df["implied_volatility"].ffill().bfill()

        if "option_volume" in ticker_df.columns:
            ticker_df["option_volume"] = ticker_df["option_volume"].fillna(0)
        else:
            ticker_df["option_volume"] = 0

        if "call_iv" in ticker_df.columns:
            ticker_df["call_iv"] = ticker_df["call_iv"].ffill().bfill()
        else:
            ticker_df["call_iv"] = np.nan

        if "put_iv" in ticker_df.columns:
            ticker_df["put_iv"] = ticker_df["put_iv"].ffill().bfill()
        else:
            ticker_df["put_iv"] = np.nan

        all_ticker_frames.append(ticker_df)

    if not all_ticker_frames:
        raise ValueError("No ticker-level market feature frames were generated.")

    features = pd.concat(all_ticker_frames, ignore_index=True)
    features = features.sort_values(["ticker", "minute"]).reset_index(drop=True)

    # 5. Returns and IV changes
    features["stock_return_1"] = (
        features.groupby("ticker")["stock_price"].pct_change()
    )
    features["stock_return_5"] = (
        features.groupby("ticker")["stock_price"].pct_change(5)
    )
    features["stock_return_10"] = (
        features.groupby("ticker")["stock_price"].pct_change(10)
    )

    features["iv_change_1"] = (
        features.groupby("ticker")["implied_volatility"].diff()
    )
    features["iv_change_5"] = (
        features.groupby("ticker")["implied_volatility"].diff(5)
    )
    features["iv_change_10"] = (
        features.groupby("ticker")["implied_volatility"].diff(10)
    )

    features["iv_return_1"] = (
        features.groupby("ticker")["implied_volatility"].pct_change()
    )
    features["iv_return_5"] = (
        features.groupby("ticker")["implied_volatility"].pct_change(5)
    )

    change_cols = [
        "stock_return_1",
        "stock_return_5",
        "stock_return_10",
        "iv_change_1",
        "iv_change_5",
        "iv_change_10",
        "iv_return_1",
        "iv_return_5",
    ]
    for col in change_cols:
        features[col] = features[col].fillna(0)

    # 6. Rolling volatility / uncertainty features
    features["price_roll_std_5"] = (
        features.groupby("ticker")["stock_return_1"]
        .transform(lambda x: x.rolling(window=5, min_periods=1).std())
        .fillna(0)
    )
    features["price_roll_std_10"] = (
        features.groupby("ticker")["stock_return_1"]
        .transform(lambda x: x.rolling(window=10, min_periods=1).std())
        .fillna(0)
    )

    features["iv_roll_std_5"] = (
        features.groupby("ticker")["implied_volatility"]
        .transform(lambda x: x.rolling(window=5, min_periods=1).std())
        .fillna(0)
    )
    features["iv_roll_std_10"] = (
        features.groupby("ticker")["implied_volatility"]
        .transform(lambda x: x.rolling(window=10, min_periods=1).std())
        .fillna(0)
    )

    # 7. Rolling slopes
    features["price_slope_5"] = (
        features.groupby("ticker")["stock_price"]
        .transform(lambda x: rolling_slope(x, 5))
        .fillna(0)
    )
    features["price_slope_10"] = (
        features.groupby("ticker")["stock_price"]
        .transform(lambda x: rolling_slope(x, 10))
        .fillna(0)
    )
    features["iv_slope_5"] = (
        features.groupby("ticker")["implied_volatility"]
        .transform(lambda x: rolling_slope(x, 5))
        .fillna(0)
    )
    features["iv_slope_10"] = (
        features.groupby("ticker")["implied_volatility"]
        .transform(lambda x: rolling_slope(x, 10))
        .fillna(0)
    )

    # 8. Option volume features
    features["option_volume_roll_5"] = (
        features.groupby("ticker")["option_volume"]
        .transform(lambda x: x.rolling(window=5, min_periods=1).sum())
    )
    features["option_volume_roll_10"] = (
        features.groupby("ticker")["option_volume"]
        .transform(lambda x: x.rolling(window=10, min_periods=1).sum())
    )
    features["option_volume_change_1"] = (
        features.groupby("ticker")["option_volume"].diff().fillna(0)
    )
    features["option_volume_change_5"] = (
        features.groupby("ticker")["option_volume"].diff(5).fillna(0)
    )

    # 9. Call-put IV skew
    features["iv_skew_cp"] = (features["call_iv"] - features["put_iv"]).fillna(0)

    # 10. Extra helpful features
    features["log_stock_price"] = np.log(features["stock_price"].replace(0, np.nan))
    features["log_stock_price"] = features["log_stock_price"].fillna(0)
    features["log_option_volume"] = np.log1p(features["option_volume"])

    # 11. Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    print(f"Saved market features to: {output_path}")


if __name__ == "__main__":
    input_file = "data/raw/market.csv"
    output_file = "data/processed/market_features.csv"
    build_market_features(input_file, output_file)
