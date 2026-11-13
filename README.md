# ShopPilot — Your Shop, Thoughtfully Run

A small-shop assistant built with Python and Flask for Lakshmi Fresh Mart, Bengaluru. ShopPilot turns 90 days of fictional sales into practical daily nudges: stock to reorder, products nearing expiry, prices to review, slow-moving inventory, returning-customer ideas, and products often bought together. Choose a 7-, 30-, or 90-day sales view, search and filter the inventory, or download a CSV action sheet.

> **Demo only:** all generated sales, customer, inventory, supplier, expiry, and recommendation data is fictional. Recommendations are examples, not live business advice.

## Run locally

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The dataset refreshes from a fixed seed and the current date when the server starts.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Other demo dashboard

The earlier Goodfolk retail sales dashboard is also preserved. Run `python goodfolk_app.py` to view it on port 5000 (stop ShopPilot first if it is already using that port).

## Project structure

- `app.py` — ShopPilot Flask routes, dashboard API, inventory search, and CSV export
- `shop_data.py` — fictional shop catalogue, 90-day sales, and business insights
- `templates/shoppilot.html` and `static/shoppilot.*` — ShopPilot website
- `goodfolk_app.py`, `sales.py`, and `templates/index.html` — previous dashboard, preserved
- `data/retail_sales.csv` and `generate_data.py` — previous dashboard's sample dataset
- `tests/` — unit and route tests
