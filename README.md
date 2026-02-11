# Mumbai-FloodCast

A spatiotemporal machine learning project that predicts micro-area waterlogging risk in Mumbai using rainfall, geospatial, and historical incident data, with map-based visualization of flood-risk zones.

## Why this project
Mumbai sees repeated monsoon waterlogging that affects daily commute, emergency response, and neighborhood safety.  
This project focuses on short-term risk prediction (starting with next 1 hour) so high-risk areas can be identified earlier.

## MVP scope (v1)
- Unit of prediction: 500m x 500m grid cell
- Target: `waterlog_risk_1h` (binary 0/1)
- Forecast horizon: next 1 hour
- Initial geography: 3–5 flood-prone pilot zones in Mumbai
- Model type: supervised classification on tabular spatiotemporal features

See full scope in [`docs/problem_definition.md`](docs/problem_definition.md).

## Planned outputs
- Risk score per grid cell (0.0 to 1.0)
- Binary risk class (0/1 using threshold)
- Risk map with low/medium/high zones

## Tech stack
- Python
- Pandas, NumPy
- scikit-learn (baselines)
- LightGBM / CatBoost (main model)
- GeoPandas / OSMnx (geospatial features)
- Matplotlib / Plotly / Folium (visualization)
- Jupyter notebooks (EDA and experiments)

## Repository structure
```text
Mumbai-FloodCast/
├── app/                    # dashboard / demo app (later phase)
├── config/                 # project configs
├── data/
│   ├── external/           # external source files
│   ├── processed/          # cleaned + feature-ready data
│   └── raw/                # ingested raw data snapshots
├── docs/
│   └── problem_definition.md
├── notebooks/              # EDA and experiments
├── reports/                # metrics, plots, evaluation reports
├── src/
│   ├── ingestion/          # data ingestion scripts
│   ├── features/           # feature engineering
│   ├── modeling/           # training/evaluation code
│   ├── inference/          # prediction pipeline
│   └── visualization/      # map/risk plotting
├── tests/                  # unit/integration tests
├── requirements.txt
└── README.md
