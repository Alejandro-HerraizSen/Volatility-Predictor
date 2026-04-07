from pathlib import Path

import numpy as np
import pandas as pd


def _compute_hawkes_intensity(post_volume, mu_soc=0.2, alpha=0.8, beta=1.0):
    intensities = []
    prev_excitation = 0.0

    for volume in post_volume:
        excitation = np.exp(-beta) * prev_excitation + alpha * volume
        intensities.append(mu_soc + excitation)
        prev_excitation = excitation

    return intensities


def _compute_social_velocity(s_soc, gamma=0.5):
    velocities = []

    for t in range(len(s_soc)):
        velocity = 0.0
        for k in range(t):
            weight = np.exp(-gamma * (t - k))
            delta_s = s_soc.iloc[k + 1] - s_soc.iloc[k]
            velocity += weight * delta_s
        velocities.append(velocity)

    return velocities


def build_social_features(
    input_path,
    output_path,
    tau=5,
    mu_soc=0.2,
    alpha=0.8,
    beta=1.0,
    gamma=0.5,
):
    """Build time-bucketed social features from scored text posts."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    # 1. Load scored social data
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    required_cols = ["timestamp", "text", "sent_score"]
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
    grouped = (
        df.groupby(["ticker", "minute"])
        .agg(
            social_sent_mean=("sent_score", "mean"),
            social_sent_std=("sent_score", "std"),
            post_volume=("text", "count"),
        )
        .reset_index()
        .sort_values(["ticker", "minute"])
    )

    if grouped.empty:
        raise ValueError("No grouped social features could be created from the input data.")

    grouped["social_sent_std"] = grouped["social_sent_std"].fillna(0)

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
        ticker_df["social_sent_mean"] = ticker_df["social_sent_mean"].fillna(0)
        ticker_df["social_sent_std"] = ticker_df["social_sent_std"].fillna(0)
        ticker_df["post_volume"] = ticker_df["post_volume"].fillna(0)

        all_ticker_frames.append(ticker_df)

    if not all_ticker_frames:
        raise ValueError("No ticker-level social feature frames were generated.")

    features = pd.concat(all_ticker_frames, ignore_index=True)
    features = features.sort_values(["ticker", "minute"]).reset_index(drop=True)

    # 5. Rolling features by ticker
    features["social_sent_roll_5"] = (
        features.groupby("ticker")["social_sent_mean"]
        .transform(lambda x: x.rolling(window=5, min_periods=1).mean())
    )

    features["social_sent_roll_10"] = (
        features.groupby("ticker")["social_sent_mean"]
        .transform(lambda x: x.rolling(window=10, min_periods=1).mean())
    )

    # Alex notebook: cumulative sentiment state and rolling social state
    features["s_off"] = (
        features.groupby("ticker")["social_sent_mean"].cumsum()
    )

    features["s_soc"] = (
        features.groupby("ticker")["social_sent_mean"]
        .transform(lambda x: x.rolling(window=tau, min_periods=1).mean())
    )

    features["volume_roll_5"] = (
        features.groupby("ticker")["post_volume"]
        .transform(lambda x: x.rolling(window=5, min_periods=1).mean())
    )

    features["volume_roll_10"] = (
        features.groupby("ticker")["post_volume"]
        .transform(lambda x: x.rolling(window=10, min_periods=1).mean())
    )

    # 6. Sentiment velocity
    features["social_sent_velocity_1"] = (
        features.groupby("ticker")["social_sent_mean"].diff().fillna(0)
    )

    features["social_sent_velocity_5"] = (
        features.groupby("ticker")["social_sent_mean"].diff(5).fillna(0)
    )

    # Alex notebook: Hawkes-style social intensity and weighted sentiment velocity
    features["lambda_soc"] = (
        features.groupby("ticker")["post_volume"]
        .transform(lambda x: pd.Series(_compute_hawkes_intensity(x, mu_soc, alpha, beta), index=x.index))
    )

    features["V_soc"] = (
        features.groupby("ticker")["s_soc"]
        .transform(lambda x: pd.Series(_compute_social_velocity(x, gamma), index=x.index))
    )

    # 7. Burst ratio
    features["burst_ratio"] = np.where(
        features["volume_roll_5"] > 0,
        features["post_volume"] / features["volume_roll_5"],
        0,
    )

    # 8. Extra useful features
    features["abs_sentiment"] = features["social_sent_mean"].abs()
    features["intensity_conviction"] = (
        np.log1p(features["post_volume"]) * features["abs_sentiment"]
    )
    features["rolling_intensity_conviction"] = (
        np.log1p(features["volume_roll_5"]) * features["social_sent_roll_5"].abs()
    )

    features["sentiment_pressure"] = features["lambda_soc"] * features["s_soc"].abs()

    # 9. Save output
    ordered_columns = [
        "ticker",
        "minute",
        "social_sent_mean",
        "social_sent_std",
        "post_volume",
        "social_sent_roll_5",
        "social_sent_roll_10",
        "volume_roll_5",
        "volume_roll_10",
        "s_off",
        "s_soc",
        "lambda_soc",
        "V_soc",
        "social_sent_velocity_1",
        "social_sent_velocity_5",
        "burst_ratio",
        "abs_sentiment",
        "intensity_conviction",
        "rolling_intensity_conviction",
        "sentiment_pressure",
    ]
    features = features[ordered_columns]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    print(f"Saved social features to: {output_path}")


if __name__ == "__main__":
    input_file = "data/processed/social_scored.csv"
    output_file = "data/processed/social_features.csv"
    build_social_features(input_file, output_file)
