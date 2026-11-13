import csv
import io
from datetime import date
from flask import Flask, jsonify, render_template, request, send_file

from sales import DATA_FILE, filter_sales, load_sales, summarize

app = Flask(__name__)


class DashboardFilterError(ValueError):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


def available_filters(rows):
    return {
        "regions": sorted({row["region"] for row in rows}),
        "categories": sorted({row["category"] for row in rows}),
        "min_date": min(row["date"] for row in rows).isoformat(),
        "max_date": max(row["date"] for row in rows).isoformat(),
    }


def filtered_rows():
    rows = load_sales()
    options = available_filters(rows)
    try:
        start_raw = request.args.get("start")
        end_raw = request.args.get("end")
        start = date.fromisoformat(start_raw) if start_raw else None
        end = date.fromisoformat(end_raw) if end_raw else None
    except ValueError as exc:
        raise DashboardFilterError("Choose valid start and end dates.", 400) from exc

    if start and end and start > end:
        raise DashboardFilterError("The start date must be on or before the end date.", 400)

    region = request.args.get("region") or None
    category = request.args.get("category") or None
    if region and region not in options["regions"]:
        raise DashboardFilterError("Choose a region from the available options.", 400)
    if category and category not in options["categories"]:
        raise DashboardFilterError("Choose a category from the available options.", 400)

    selected = filter_sales(rows, start, end, region, category)
    if not selected:
        raise DashboardFilterError("No sales match these filters. Try a wider date range.", 404)
    return selected


@app.get("/")
def index():
    rows = load_sales()
    return render_template("index.html", filters=available_filters(rows))


@app.get("/api/dashboard")
def dashboard_data():
    try:
        selected = filtered_rows()
    except DashboardFilterError as exc:
        return jsonify({"error": str(exc)}), exc.status_code
    return jsonify(summarize(selected))


@app.get("/api/export")
def export_report():
    try:
        data = summarize(filtered_rows())
    except DashboardFilterError as exc:
        return jsonify({"error": str(exc)}), exc.status_code

    report = io.StringIO(newline="")
    writer = csv.writer(report)
    writer.writerow(["Northstar Retail Summary"])
    writer.writerow(["Fictional demonstration data", "USD"])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    writer.writerows(
        [
            ["Total sales", data["kpis"]["sales"]],
            ["Net profit", data["kpis"]["profit"]],
            ["Profit margin (%)", data["kpis"]["margin"]],
            ["Orders", data["kpis"]["orders"]],
            ["Average order value", data["kpis"]["average_order"]],
            ["Units sold", data["kpis"]["units"]],
        ]
    )
    writer.writerow([])
    writer.writerow(["Top products"])
    writer.writerow(["Product", "Sales (USD)", "Profit (USD)", "Units"])
    for product in data["products"]:
        writer.writerow([product["name"], product["sales"], product["profit"], product["units"]])

    return send_file(
        io.BytesIO(report.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="northstar-retail-summary.csv",
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "dataset": DATA_FILE.name})


if __name__ == "__main__":
    app.run(debug=True)
