from datetime import datetime
from pathlib import Path
import pandas as pd
import yaml
import requests

RAW_DIR = Path("data/raw/weather")

def repo_root():
    return Path(__file__).resolve().parents[2]

def load_config():
    config_path = repo_root() / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def fetch_weather(lat, lon, start, end):
    # Open-Meteo expects dates like YYYY-MM-DD
    start_date = pd.to_datetime(start).strftime("%Y-%m-%d")
    end_date = pd.to_datetime(end).strftime("%Y-%m-%d")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "precipitation",
        "timezone": "Asia/Kolkata",
    }

    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    precip = hourly.get("precipitation", [])

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(times),
        "lat": lat,
        "lon": lon,
        "rain_mm": precip
    })

    if df.empty:
        raise ValueError("Open-Meteo returned empty data (unexpected).")

    return df

def main():
    cfg = load_config()
    start = pd.to_datetime(cfg["weather"]["start"])
    end = pd.to_datetime(cfg["weather"]["end"])

    dfs = []
    for p in cfg["weather"]["points"]:
        dfs.append(fetch_weather(p["lat"], p["lon"], start, end))

    out = pd.concat(dfs, ignore_index=True)

    run_date = datetime.now().strftime("%Y-%m-%d")
    outdir = repo_root() / RAW_DIR / run_date
    outdir.mkdir(parents=True, exist_ok=True)

    outpath = outdir / "weather.parquet"
    out.to_parquet(outpath, index=False)

    print("Saved:", outpath)
    print("Rows:", len(out))
    print("Columns:", list(out.columns))
    print(out.head())

if __name__ == "__main__":
    main()