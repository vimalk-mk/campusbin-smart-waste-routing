# CampusBin: Smart Waste Collection & Route Optimization
SOCIOTHON 2026 · IIT Roorkee · Problem Statement 2

Tracks 30 campus bins from real KML survey data, predicts when they fill, and plans truck routes on the OpenStreetMap road network. Flask backend + Leaflet dashboard.

Demo video: _add link here_ · Live app: _add Render link here_

## Project layout
    app.py              Flask backend (bins, routing, forecast, API)
    static/index.html   Dashboard
    data/campus.kml     Survey points (30 bins are chosen from the campus ones)
    data/roads.json     OpenStreetMap roads (readable copy)
    data/roads.json.gz  Same roads, compressed (used first; hard to corrupt)
    check_data.py       Validates the data files before you push
    render.yaml         Render deploy settings
    requirements.txt    flask, networkx, gunicorn

## Run locally
    python -m pip install -r requirements.txt
    python check_data.py
    python app.py            # http://localhost:5000

## Deploy on Render (free)
1. Upload the **files from the zip** to a GitHub repo. Use "Add file → Upload files" and drag them in. **Never paste file contents**, that corrupts `roads.json`.
2. Run `python check_data.py` locally first; it must print `ALL GOOD`.
3. Render → **New → Blueprint** → pick the repo (it reads `render.yaml`).
   Or **New → Web Service** with: Build `pip install -r requirements.txt`, Start `gunicorn app:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`, env vars `PYTHON_VERSION=3.12.8` and `CAMPUSBIN_OFFLINE=1`.
4. Keep **one worker**: bin state lives in memory.
5. Open `/healthz`. It should show `"routing":"OpenStreetMap road network (1535 junctions…"`. If it says "straight-line fallback", the road files in the repo are damaged: re-upload them from the zip.

The free plan sleeps when idle; the first visit after a pause takes about 30 s. Open the link once before a demo.

## Which 30 bins?
`campus.kml` has 91 placemarks, many outside campus. `app.py` keeps points inside `CAMPUS_BOX`, merges duplicates within 30 m (37 remain), keeps the 10 "Dustbin" folder points, and adds 20 more by farthest-point sampling for even coverage. Settings (`N_BINS`, `CAMPUS_BOX`, `DEPOT_LATLON`) are at the top of `app.py`.

## Method
1. Fill model: zone base rate × hourly peak pattern; an EWMA learns each bin's rate. Zones, bin sizes and rates are **simulated assumptions** until sensors report.
2. Selection: visit if fill ≥ threshold, predicted full within horizon, or citizen-reported.
3. Routing: capacity-limited sweep → nearest neighbour → 2-opt on road distance; ETA = 18 km/h + 3 min/stop.
4. Impact vs a fixed route visiting every bin: km, diesel (0.4 L/km), CO₂ (2.68 kg/L).
5. Next: OR-Tools VRP, live traffic, Prophet/LSTM forecasts.

## IoT hook
    curl -X POST https://YOUR-APP.onrender.com/api/telemetry -H "Content-Type: application/json" -d '{"bin_id":"B05","fill":83.5}'

## API
GET /healthz · /api/bins · /api/plan?threshold=70&horizon=3&cap=1500 · /api/forecast · POST /api/report · /api/collect · /api/telemetry · /api/reset
