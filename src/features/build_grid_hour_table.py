from pathlib import Path
import geopandas as gpd
import pandas as pd


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def latest_dir(base: Path) -> Path:
    dated = sorted([p for p in base.iterdir() if p.is_dir()])
    if not dated:
        raise FileNotFoundError(f"No dated folders found under {base}")
    return dated[-1]


def main():
    root = repo_root()

    # ---- Load grid (centroids + ids)
    grid_path = root / "data" / "processed" / "grids" / "grid_500m.geojson"
    grid = gpd.read_file(grid_path)

    # Keep minimal columns
    grid_df = grid[["grid_id", "centroid_lat", "centroid_lon"]].copy()

    # ---- Load latest weather snapshot
    weather_base = root / "data" / "raw" / "weather"
    weather_dir = latest_dir(weather_base)
    weather_path = weather_dir / "weather.parquet"
    weather = pd.read_parquet(weather_path)

    # Ensure datetime
    weather["timestamp"] = pd.to_datetime(weather["timestamp"])
    weather = weather.sort_values("timestamp")

    # We assume weather is at a few (lat,lon) points across all hours
    stations = weather[["lat", "lon"]].drop_duplicates().reset_index(drop=True)

    # ---- Assign each grid cell to nearest weather station (simple MVP)
    # Cross join grid cells to stations and compute distance in degrees (ok for small areas)
    grid_df["_key"] = 1
    stations["_key"] = 1
    pairs = grid_df.merge(stations, on="_key").drop(columns="_key")

    pairs["dist2"] = (pairs["centroid_lat"] - pairs["lat"]) ** 2 + (pairs["centroid_lon"] - pairs["lon"]) ** 2
    nearest = pairs.sort_values("dist2").groupby("grid_id", as_index=False).first()
    nearest = nearest.drop(columns=["dist2"])

    # Now we have mapping: grid_id -> weather (lat,lon)
    # ---- Join weather time series onto each grid cell
    # Create (grid_id x timestamps) by merging on lat/lon station keys
    grid_weather = nearest.merge(weather, on=["lat", "lon"], how="left")

    # Keep clean columns
    out = grid_weather[["grid_id", "timestamp", "centroid_lat", "centroid_lon", "lat", "lon", "rain_mm"]].copy()

    # Sanity checks
    if out["rain_mm"].isna().any():
        # If this happens, it usually means mismatch in lat/lon types
        missing = out[out["rain_mm"].isna()].head(5)
        raise ValueError(f"Found NaNs in rain_mm after join. Sample:\n{missing}")

    outdir = root / "data" / "processed" / "tables"
    outdir.mkdir(parents=True, exist_ok=True)

    outpath = outdir / "grid_hour.parquet"
    out.to_parquet(outpath, index=False)

    print("Loaded grid:", grid_path)
    print("Loaded weather:", weather_path)
    print("Saved table:", outpath)
    print("Rows:", len(out))
    print("Unique grids:", out["grid_id"].nunique())
    print("Unique hours:", out["timestamp"].nunique())
    print(out.head(5))


if __name__ == "__main__":
    main()
