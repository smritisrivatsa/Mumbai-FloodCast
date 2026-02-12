from datetime import datetime
from pathlib import Path
import yaml
import osmnx as ox

RAW_DIR = Path("data/raw/geodata")


def repo_root() -> Path:
    # src/ingestion/geodata.py -> repo root
    return Path(__file__).resolve().parents[2]


def load_config() -> dict:
    config_path = repo_root() / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    # Make Overpass requests more reliable (do NOT set headers here; OSMnx already manages them)
    ox.settings.timeout = 180

    _cfg = load_config()

    # IMPORTANT:
    # "Mumbai, Maharashtra, India" often geocodes to a POINT (city place) -> fails.
    # District-level queries are more likely to return a polygon.
    boundary_place = "Mumbai Suburban, Maharashtra, India"
    # Alternative if you want the core:
    # boundary_place = "Mumbai City, Maharashtra, India"

    run_date = datetime.now().strftime("%Y-%m-%d")
    outdir = repo_root() / RAW_DIR / run_date
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching boundary polygon for: {boundary_place}")
    boundary_gdf = ox.geocode_to_gdf(boundary_place, which_result=1)

    geom_type = boundary_gdf.geometry.iloc[0].geom_type
    print("Boundary geometry type:", geom_type)
    if geom_type not in ["Polygon", "MultiPolygon"]:
        raise ValueError(f"Expected Polygon/MultiPolygon, got {geom_type}")

    # Save boundary
    boundary_path = outdir / "boundary.geojson"
    boundary_gdf.to_file(boundary_path, driver="GeoJSON")
    print("Boundary saved:", boundary_path)

    # Build roads from polygon directly (more robust than graph_from_place)
    polygon = boundary_gdf.geometry.iloc[0]

    # Reduce polygon complexity and add a tiny buffer so truncation doesn't drop everything
    polygon_simplified = polygon.simplify(0.001)   # small simplification
    polygon_buffered = polygon_simplified.buffer(0.001)

    print("Downloading roads from Overpass (can take 1–3 minutes)...")
    try:
        G = ox.graph_from_polygon(polygon_buffered, network_type="drive", simplify=True)
    except ValueError:
        print("Drive network empty for this polygon; falling back to network_type='all'")
        G = ox.graph_from_polygon(polygon_buffered, network_type="all", simplify=True)

    # Save roads
    roads_path = outdir / "roads.graphml"
    ox.save_graphml(G, roads_path)
    print("Roads saved:", roads_path)
    print("Nodes:", len(G.nodes), "Edges:", len(G.edges))

    print("Done.")


if __name__ == "__main__":
    main()
