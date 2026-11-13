"""Generate the clearly fictional, reproducible dashboard demo dataset."""

import csv
import random
import calendar
from datetime import date
from pathlib import Path

random.seed(2025)

PRODUCTS = [
    ("Home & Living", "Stoneware dinner set", 72, 34),
    ("Home & Living", "Linen cushion cover", 28, 11),
    ("Home & Living", "Glass table lamp", 64, 29),
    ("Electronics", "Wireless headphones", 89, 46),
    ("Electronics", "Portable speaker", 58, 27),
    ("Electronics", "Smart desk light", 43, 19),
    ("Apparel", "Everyday tote bag", 32, 12),
    ("Apparel", "Cotton knit sweater", 84, 36),
    ("Apparel", "Relaxed fit tee", 26, 9),
    ("Beauty", "Botanical hand care set", 36, 14),
    ("Beauty", "Daily ritual face oil", 48, 19),
    ("Beauty", "Citrus body wash", 22, 8),
]
REGIONS = {
    "Northeast": ["New York", "Massachusetts", "Pennsylvania"],
    "South": ["Georgia", "Texas", "North Carolina"],
    "Midwest": ["Illinois", "Ohio", "Minnesota"],
    "West": ["California", "Washington", "Colorado"],
}
MONTH_WEIGHTS = [0.83, 0.79, 0.91, 0.94, 1.02, 0.98, 1.08, 1.04, 0.96, 1.1, 1.25, 1.48]
FIELDS = ["date", "order_id", "region", "state", "category", "product", "units", "unit_price", "unit_cost"]


def build_rows():
    rows = []
    for order_number in range(1, 1201):
        month = random.choices(range(1, 13), weights=MONTH_WEIGHTS, k=1)[0]
        day = random.randint(1, calendar.monthrange(2025, month)[1])
        order_date = date(2025, month, day)
        category, product, price, cost = random.choice(PRODUCTS)
        region = random.choice(list(REGIONS))
        units = random.choices([1, 2, 3, 4], weights=[65, 24, 8, 3])[0]
        seasonal_price = round(price * random.uniform(0.94, 1.07), 2)
        seasonal_cost = round(cost * random.uniform(0.96, 1.04), 2)
        rows.append(
            {
                "date": order_date.isoformat(),
                "order_id": f"RT-{order_number:05d}",
                "region": region,
                "state": random.choice(REGIONS[region]),
                "category": category,
                "product": product,
                "units": units,
                "unit_price": f"{seasonal_price:.2f}",
                "unit_cost": f"{seasonal_cost:.2f}",
            }
        )
    return rows


def write_dataset(path=None):
    output = Path(path) if path else Path(__file__).parent / "data" / "retail_sales.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output


if __name__ == "__main__":
    print(f"Generated fictional demo data at {write_dataset()}")
