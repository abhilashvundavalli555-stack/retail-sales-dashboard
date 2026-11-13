"""CSV loading and filtered retail dashboard summaries."""

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "retail_sales.csv"
REQUIRED_FIELDS = {
    "date", "order_id", "region", "state", "category",
    "product", "units", "unit_price", "unit_cost",
}


def load_sales(path=DATA_FILE):
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not REQUIRED_FIELDS.issubset(reader.fieldnames):
            raise ValueError("Sales CSV is missing one or more required columns.")

        rows = []
        for line_number, row in enumerate(reader, start=2):
            try:
                row["date"] = date.fromisoformat(row["date"])
                row["units"] = int(row["units"])
                row["unit_price"] = float(row["unit_price"])
                row["unit_cost"] = float(row["unit_cost"])
                if row["units"] <= 0 or row["unit_price"] < 0 or row["unit_cost"] < 0:
                    raise ValueError
                rows.append(row)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid sales data on CSV line {line_number}.") from exc

    if not rows:
        raise ValueError("Sales CSV has no sales rows.")
    return rows


def filter_sales(rows, start_date=None, end_date=None, region=None, category=None):
    return [
        row for row in rows
        if (start_date is None or row["date"] >= start_date)
        and (end_date is None or row["date"] <= end_date)
        and (region is None or row["region"] == region)
        and (category is None or row["category"] == category)
    ]


def summarize(rows):
    monthly = defaultdict(lambda: {"sales": 0.0, "profit": 0.0})
    by_category = defaultdict(lambda: {"sales": 0.0, "profit": 0.0, "units": 0})
    by_region = defaultdict(lambda: {"sales": 0.0, "profit": 0.0})
    by_product = defaultdict(lambda: {"sales": 0.0, "profit": 0.0, "units": 0})
    total_sales = total_profit = 0.0

    for row in rows:
        sales = row["units"] * row["unit_price"]
        profit = row["units"] * (row["unit_price"] - row["unit_cost"])
        month = row["date"].strftime("%Y-%m")
        total_sales += sales
        total_profit += profit
        monthly[month]["sales"] += sales
        monthly[month]["profit"] += profit
        by_category[row["category"]]["sales"] += sales
        by_category[row["category"]]["profit"] += profit
        by_category[row["category"]]["units"] += row["units"]
        by_region[row["region"]]["sales"] += sales
        by_region[row["region"]]["profit"] += profit
        by_product[row["product"]]["sales"] += sales
        by_product[row["product"]]["profit"] += profit
        by_product[row["product"]]["units"] += row["units"]

    order_count = len({row["order_id"] for row in rows})
    return {
        "kpis": {
            "sales": round(total_sales, 2),
            "profit": round(total_profit, 2),
            "margin": round(total_profit / total_sales * 100, 1) if total_sales else 0,
            "orders": order_count,
            "average_order": round(total_sales / order_count, 2) if order_count else 0,
            "units": sum(row["units"] for row in rows),
        },
        "monthly": [
            {"month": month, "sales": round(values["sales"], 2), "profit": round(values["profit"], 2)}
            for month, values in sorted(monthly.items())
        ],
        "categories": [
            {"name": name, **{key: round(value, 2) for key, value in values.items() if key != "units"},
             "units": values["units"]}
            for name, values in sorted(by_category.items(), key=lambda item: -item[1]["sales"])
        ],
        "regions": [
            {"name": name, "sales": round(values["sales"], 2), "profit": round(values["profit"], 2)}
            for name, values in sorted(by_region.items(), key=lambda item: -item[1]["sales"])
        ],
        "products": [
            {"name": name, **{key: round(value, 2) for key, value in values.items() if key != "units"},
             "units": values["units"]}
            for name, values in sorted(by_product.items(), key=lambda item: -item[1]["sales"])[:5]
        ],
        "transactions": [
            {
                "date": row["date"].isoformat(),
                "order_id": row["order_id"],
                "product": row["product"],
                "category": row["category"],
                "region": row["region"],
                "units": row["units"],
                "sales": round(row["units"] * row["unit_price"], 2),
                "profit": round(row["units"] * (row["unit_price"] - row["unit_cost"]), 2),
            }
            for row in sorted(rows, key=lambda row: row["date"], reverse=True)[:8]
        ],
        "count": len(rows),
    }
