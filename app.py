import csv
import io
from datetime import date
from functools import lru_cache

from flask import Flask, jsonify, render_template, request, send_file

from shop_data import CATEGORY_TARGET_MARGIN, STORE, build_dashboard, format_inr

app = Flask(__name__)


@lru_cache(maxsize=3)
def _dashboard_for(today_iso, days):
    return build_dashboard(days=days, today=date.fromisoformat(today_iso))


def _get_dashboard():
    raw_days = request.args.get("days", "7")
    try:
        days = int(raw_days)
    except ValueError as exc:
        raise ValueError("Choose a 7, 30, or 90 day period.") from exc
    if days not in (7, 30, 90):
        raise ValueError("Choose a 7, 30, or 90 day period.")
    return _dashboard_for(date.today().isoformat(), days)


@app.get("/")
def index():
    return render_template(
        "shoppilot.html",
        store=STORE,
        categories=sorted(CATEGORY_TARGET_MARGIN),
        today=date.today().isoformat(),
    )


@app.get("/api/dashboard")
def dashboard_api():
    try:
        data = _get_dashboard()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({key: value for key, value in data.items() if key != "inventory"})


@app.get("/api/inventory")
def inventory_api():
    try:
        data = _get_dashboard()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    category = request.args.get("category", "").strip()
    query = request.args.get("q", "").strip().casefold()
    if category and category not in CATEGORY_TARGET_MARGIN:
        return jsonify({"error": "Choose a valid product category."}), 400
    products = [
        item for item in data["inventory"]
        if (not category or item["category"] == category)
        and (not query or query in item["name"].casefold() or query in item["sku"].casefold())
    ]
    return jsonify({"products": products, "count": len(products)})


@app.get("/api/export")
def export_api():
    try:
        data = _get_dashboard()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([f"{STORE['name']} — ShopPilot inventory & actions"])
    writer.writerow(["Fictional demo data", STORE["city"], "INR"])
    writer.writerow([])
    writer.writerow(["SKU", "Product", "Category", "On hand", "Unit cost", "Shelf price", "Supplier"])
    for product in data["inventory"]:
        writer.writerow([
            product["sku"], product["name"], product["category"], product["stock"],
            product["cost"], product["price"], product["supplier"],
        ])
    writer.writerow([])
    writer.writerow(["EXPIRY WATCH"])
    writer.writerow(["Product", "Units at risk", "Days left", "Cost at risk (INR)"])
    for item in data["expiry"]:
        writer.writerow([item["name"], item["units"], item["days_left"], item["loss"]])
    writer.writerow([])
    writer.writerow(["REORDER SUGGESTIONS"])
    writer.writerow(["Product", "On hand", "Suggested quantity", "Supplier", "Order estimate (INR)"])
    for item in data["reorder"]:
        writer.writerow([item["name"], item["stock"], item["suggested_qty"], item["supplier"], item["order_cost"]])

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="shoppilot-daily-action-sheet.csv",
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "store": STORE["name"], "data": "fictional demo"})


app.jinja_env.globals["inr"] = format_inr

if __name__ == "__main__":
    app.run(debug=True)
