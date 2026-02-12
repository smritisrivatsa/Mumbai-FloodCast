from pathlib import Path
import geopandas as gpd
import numpy as np
from shapely.geometry import box


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def latest_geodata_dir() -> Path:
    base = repo_root() / "data" / "raw" / "geodata"
    dated = sorted([p for p in base.iterdir() if p.is_dir()])
    if not dated:
        raise FileNotFoundError("No data/raw/geodata/<date>/ folders found. Run geodata ingestion first.")
    return dated[-1]


def build_grid(boundary_gdf: gpd.GeoDataFrame, cell_size_m: int = 500) -> gpd.GeoDataFrame:
    # Project to meters so 500m means 500 meters
    boundary_3857 = boundary_gdf.to_crs(3857)
    polygon = boundary_3857.geometry.iloc[0]

    minx, miny, maxx, maxy = polygon.bounds

    xs = np.arange(minx, maxx, cell_size_m)
    ys = np.arange(miny, maxy, cell_size_m)

    cells = []
    for x in xs:
        for y in ys:
            cell = box(x, y, x + cell_size_m, y + cell_size_m)
            if cell.intersects(polygon):
                cells.append(cell)

    grid = gpd.GeoDataFrame({"geometry": cells}, crs=3857)
    grid["grid_id"] = [f"g{i:06d}" for i in range(len(grid))]

    # Centroids back to lat/lon for joins later
    cent = grid.geometry.centroid
    cent_ll = gpd.GeoSeries(cent, crs=3857).to_crs(4326)
    grid["centroid_lon"] = cent_ll.x
    grid["centroid_lat"] = cent_ll.y

    # Return in lat/lon CRS for storage + mapping
    return grid.to_crs(4326)


def main():
    geodata_dir = latest_geodata_dir()
    boundary_path = geodata_dir / "boundary.geojson"

    boundary = gpd.read_file(boundary_path)
    grid = build_grid(boundary, cell_size_m=500)

    outdir = repo_root() / "data" / "processed" / "grids"
    outdir.mkdir(parents=True, exist_ok=True)

    outpath = outdir / "grid_500m.geojson"
    grid.to_file(outpath, driver="GeoJSON")

    print("Loaded boundary:", boundary_path)
    print("Saved grid:", outpath)
    print("Cells:", len(grid))
    print(grid.head(3))


if __name__ == "__main__":
    main()
