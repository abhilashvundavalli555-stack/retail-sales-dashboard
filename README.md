# Northstar — Retail Sales Dashboard

A polished, responsive retail analytics website built with Python and Flask. Explore sales, net profit, orders, average order value, sales trends, category mix, regional performance, bestsellers, and recent transactions. Filters update the dashboard live, and the Export report button downloads a filtered CSV summary with top products.

> **Demo only:** This project includes 1,200 reproducible, entirely fictional sample orders for 2025. It does not contain real customer or business data.

## Run locally

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Regenerate demo data

```powershell
python generate_data.py
```

The fixed random seed makes the sample dataset reproducible.

## Project structure

- `app.py` — Flask routes and validated dashboard API
- `sales.py` — CSV loading, filtering, and metric aggregation
- `data/retail_sales.csv` — fictional sample transactions
- `generate_data.py` — reproducible sample-data generator
- `templates/` and `static/` — responsive dashboard website and interactive charts
- `tests/` — unit and route tests
