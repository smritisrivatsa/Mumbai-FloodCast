# Mumbai FloodCast — Problem Definition (Phase 0)

## Project summary
Mumbai FloodCast is a spatiotemporal ML project that predicts short-term waterlogging risk at micro-area level during monsoon conditions.
The MVP predicts whether a location is likely to waterlog in the next 1 hour; later horizons (3h, 6h) are planned after v1.

---

## MVP objective
Build a reproducible baseline system that answers the question:

“Given current + recent rainfall/weather and location features, what is the probability that this grid cell will waterlog in the next 1 hour?”

Required outputs
- Risk score per grid cell (float 0.0–1.0)
- Binary risk class per grid cell (0/1 using a chosen threshold)
- Map visualization showing low / medium / high risk zones

---

## Scope decisions (locked for MVP)

| Item | MVP choice |
| --- | --- |
| Unit of prediction | **500 m × 500 m grid cell** |
| Target | **`waterlog_risk_1h` (binary 0/1)** |
| Horizon | **Next 1 hour** (v1); 3h/6h added later |
| City area | Start with **3–5 flood-prone pilot zones**, then scale city-wide |
| Modeling type | Supervised classification on tabular spatiotemporal features |

Pilot zones (initial)
- Use 3–5 historically flood-prone micro-areas identified from complaint/event density. Exact list finalized after EDA.

---

## Target definition (labeling rule)
For each grid cell `g` and hourly timestamp `t`:

- `waterlog_risk_1h(g, t) = 1` if at least one validated waterlogging incident is observed in cell `g` during the interval `(t, t + 1h]`.
- Otherwise `waterlog_risk_1h(g, t) = 0`.

Notes
- Initial labels may use complaint / event records as proxy signals.
- If sources conflict, apply a documented source-priority rule in the labeling script.
- Keep label logic deterministic and versioned.

---

## Minimum data needed (MVP)

1) Weather / rainfall (hourly)
- Rainfall intensity (mm)
- Rolling rainfall windows: last 1h, 3h, 6h, 24h
- Optional: humidity, wind, temperature

2) Geospatial layers
- Ward boundaries / city boundary
- Road network features (road / intersection density)
- Optional: elevation / slope proxies

3) Historical waterlogging signals
- Complaint / event records with timestamp + location
- Historical hotspot frequency per grid cell

---

## Feature set (MVP v1)

Temporal
- Hour of day, day of week, month, monsoon flag

Rainfall
- `rain_1h`, `rain_3h`, `rain_6h`, `rain_24h`
- Rainfall trend / change vs previous hour

Spatial
- Grid ID (or encoded location)
- Road density, intersection density
- Historical flooding frequency per grid cell

Optional interactions
- `rain_3h * hotspot_score`
- `rain_1h * road_density`

---

## Baselines and model plan

Baselines
1. Persistence baseline — predict previous-hour label
2. Frequency baseline — predict historical risk for grid+hour bucket
3. Simple ML baseline — logistic regression

Candidate main model
- Gradient-boosted tree (LightGBM or CatBoost) on tabular spatiotemporal features

---

## Evaluation protocol

- Use time-based splits only (no random shuffle across time):
  - Train on earlier time period
  - Validate / test on later period
- Handle class imbalance with class weights and threshold tuning
- Primary metric: PR-AUC
- Secondary metrics: F1-score, precision, recall
- Report confusion matrix at chosen threshold

---

## Success criteria (Phase 0)

MVP is successful if all three are true:

1. Model quality
- PR-AUC and F1 exceed baseline(s)
- Improvement visible on held-out time period

2. Usable output
- Map view renders risk zones for pilot areas

3. Reproducibility
- End-to-end training pipeline runs from a clean setup
- Fixed random seed and environment file included
- Data / version + config tracked in the repo

---

## Out of scope (for MVP)

- City-wide real-time production deployment
- Hydrodynamic simulation or physical drainage modeling
- Satellite-only deep learning pipeline
- Full route optimization / commuter recommendation engine
- 3h / 6h forecasting (added only after the 1h model is stable)

---

## Risks and mitigations

- Sparse or noisy labels → use weak-label strategies and confidence flags
- Class imbalance → focus on PR-AUC, use weighted loss and threshold tuning
- Location accuracy issues → apply grid snapping and validation filters
- Data gaps in rainfall → fallback interpolation and missingness indicators

---

## Day-1 deliverables checklist

- [x] `docs/problem_definition.md` created
- [ ] Pilot zones shortlist from initial map / EDA
- [ ] Finalized label logic for `waterlog_risk_1h`
- [ ] Metric template for PR-AUC / F1 reporting
- [ ] Scope freeze committed to GitHub

---

## Next steps (Phase 1)

1. Set up repository structure and ingestion scripts for:
   - weather data
   - geospatial layers
   - historical complaint / event records

2. Run first EDA notebook to validate pilot zones and label coverage.

---

_Document version: Phase 0 — baseline problem definition_
