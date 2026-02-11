# Mumbai FloodCast — Problem Definition (Phase 0)

## Project summary
Mumbai FloodCast is a spatiotemporal machine learning project to predict short-term waterlogging risk at a micro-area level during monsoon conditions.

The first version (MVP) focuses on predicting whether a location is likely to waterlog in the next 1 hour. After that is stable, the project can be extended to 3-hour and 6-hour forecasts.

## MVP objective
Build a reproducible baseline system that answers:

Given current and recent rainfall, weather, and location features, what is the probability that a grid cell will waterlog in the next hour?

The MVP should output:
- A risk score per grid cell (0.0 to 1.0)
- A binary risk class per grid cell (0/1 with a chosen threshold)
- A map showing low, medium, and high risk zones

## Scope decisions for MVP

| Item | Choice |
|---|---|
| Unit of prediction | 500m x 500m grid cell |
| Target | `waterlog_risk_1h` (binary 0/1) |
| Horizon | Next 1 hour (v1) |
| City area | Start with 3 to 5 flood-prone pilot zones, then scale city-wide |
| Model type | Supervised classification on tabular spatiotemporal features |

### Pilot zones
Start with 3 to 5 historically flood-prone micro-areas using complaint/event density. Final pilot zone list will be locked after EDA.

## Target definition (labeling rule)
For each grid cell `g` and hourly timestamp `t`:

- `waterlog_risk_1h(g, t) = 1` if at least one validated waterlogging incident is observed in cell `g` during `(t, t + 1h]`
- Otherwise, `waterlog_risk_1h(g, t) = 0`

Notes:
- Initial labels may use complaint/event records as proxy signals.
- If sources conflict, use a documented source-priority rule in the labeling script.
- Label logic should stay deterministic and versioned.

## Minimum data needed (MVP)

### 1) Weather and rainfall (hourly)
- Rainfall intensity (mm)
- Rolling rainfall windows: last 1h, 3h, 6h, 24h
- Optional: humidity, wind, temperature

### 2) Geospatial layers
- Ward boundaries or city boundary
- Road network features (road density, intersection density)
- Optional: elevation or slope proxies

### 3) Historical waterlogging signals
- Complaint/event records with timestamp and location
- Historical hotspot frequency per grid cell

## Feature set (MVP v1)

### Temporal
- Hour of day
- Day of week
- Month
- Monsoon flag

### Rainfall
- `rain_1h`, `rain_3h`, `rain_6h`, `rain_24h`
- Rainfall trend/change vs previous hour

### Spatial
- Grid ID (or encoded location)
- Road density
- Intersection density
- Historical flooding frequency per grid cell

### Optional interaction features
- `rain_3h * hotspot_score`
- `rain_1h * road_density`

## Baselines and model plan

### Baselines
1. Persistence baseline: predict previous-hour label
2. Frequency baseline: predict historical risk for grid + hour bucket
3. Simple ML baseline: logistic regression

### Candidate main model
- LightGBM or CatBoost on tabular spatiotemporal features

## Evaluation protocol
- Use time-based splits only (no random shuffle):
  - Train on earlier period
  - Validate/test on later period
- Handle class imbalance with class weights and threshold tuning
- Primary metric: PR-AUC
- Secondary metrics: F1, precision, recall
- Report confusion matrix at selected threshold

## Success criteria (Phase 0)
MVP is successful if all are true:

1. Model quality
   - PR-AUC and F1 are better than baselines
   - Improvement is visible on held-out period

2. Usable output
   - Map view renders risk zones for pilot areas

3. Reproducibility
   - End-to-end training pipeline runs from clean setup
   - Fixed random seed and environment file included
   - Data/config/model versions tracked in repo

## Out of scope (MVP)
- City-wide real-time production deployment
- Hydrodynamic or physical drainage simulation
- Satellite-only deep learning pipeline
- Route optimization/recommendation engine
- 3h/6h forecasting (until 1h model is stable)

## Risks and mitigations
- Sparse/noisy labels -> weak-label strategy and confidence flags
- Class imbalance -> weighted loss, threshold tuning, PR-AUC focus
- Location accuracy issues -> grid snapping and validation filters
- Rainfall data gaps -> interpolation and missingness indicators

## Day-1 deliverables checklist
- [x] `docs/problem_definition.md` created
- [ ] Pilot zones shortlist from map/EDA
- [ ] Finalized label logic for `waterlog_risk_1h`
- [ ] Metric template for PR-AUC/F1 reporting
- [ ] Scope freeze committed to GitHub

## Next steps (Phase 1)
1. Set up repository structure and ingestion scripts for:
   - Weather data
   - Geospatial layers
   - Historical complaint/event records
2. Run first EDA notebook to validate pilot zones and label coverage

---

Document version: Phase 0 baseline definition