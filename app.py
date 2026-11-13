from datetime import date
from flask import Flask, jsonify, render_template, request

from sales import DATA_FILE, filter_sales, load_sales, summarize

app = Flask(__name__)


def available_filters(rows):
    return {
        "regions": sorted({row["region"] for row in rows}),
        "categories": sorted({row["category"] for row in rows}),
        "min_date": min(row["date"] for row in rows).isoformat(),
        "max_date": max(row["date"] for row in rows).isoformat(),
    }


@app.get("/")
def index():
    rows = load_sales()
    return render_template("index.html", filters=available_filters(rows))


@app.get("/api/dashboard")
def dashboard_data():
    rows = load_sales()
    options = available_filters(rows)
    try:
        start_raw = request.args.get("start")
        end_raw = request.args.get("end")
        start = date.fromisoformat(start_raw) if start_raw else None
        end = date.fromisoformat(end_raw) if end_raw else None
    except ValueError:
        return jsonify({"error": "Choose valid start and end dates."}), 400

    if start and end and start > end:
        return jsonify({"error": "The start date must be on or before the end date."}), 400

    region = request.args.get("region") or None
    category = request.args.get("category") or None
    if region and region not in options["regions"]:
        return jsonify({"error": "Choose a region from the available options."}), 400
    if category and category not in options["categories"]:
        return jsonify({"error": "Choose a category from the available options."}), 400

    selected = filter_sales(rows, start, end, region, category)
    if not selected:
        return jsonify({"error": "No sales match these filters. Try a wider date range."}), 404
    return jsonify(summarize(selected))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "dataset": DATA_FILE.name})


if __name__ == "__main__":
    app.run(debug=True)
