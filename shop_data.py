"""Reproducible fictional grocery-shop activity and actionable insights."""

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
import random

HISTORY_DAYS = 90
STORE = {"name": "Lakshmi Fresh Mart", "city": "Bangalore", "currency": "INR"}

CATEGORY_TARGET_MARGIN = {
    "Dairy": 0.08, "Bakery": 0.22, "Fresh Produce": 0.25, "Staples": 0.12,
    "Snacks": 0.20, "Beverages": 0.18, "Personal Care": 0.22, "Household": 0.20,
}
CATEGORY_SUPPLIER = {
    "Dairy": "Nandi Dairy Agency", "Bakery": "Daily Bake Supplies",
    "Fresh Produce": "Kisan Farm Direct", "Staples": "Metro Wholesale",
    "Snacks": "City Distributors", "Beverages": "City Distributors",
    "Personal Care": "Metro Wholesale", "Household": "Metro Wholesale",
}

# sku, product, category, cost, price, daily demand, lead days, shelf life,
# stock cover days, notable demo condition
PRODUCTS = [
    ("DA01", "Toned Milk 500ml", "Dairy", 25.5, 27, 60, 1, 3, 0.8, "expiry"),
    ("DA02", "Curd 400g", "Dairy", 30, 36, 22, 1, 5, 1.1, "expiry"),
    ("DA03", "Paneer 200g", "Dairy", 70, 85, 9, 2, 6, 2.0, "expiry"),
    ("DA04", "Butter 100g", "Dairy", 52, 60, 8, 2, 90, 12, ""),
    ("DA05", "Eggs (6 pack)", "Dairy", 38, 46, 18, 2, 10, 4, ""),
    ("BK01", "Brown Bread 400g", "Bakery", 34, 42, 20, 1, 4, 3, ""),
    ("BK02", "Pav Buns (6)", "Bakery", 18, 25, 14, 1, 3, 2, "expiry"),
    ("FP01", "Tomato 1kg", "Fresh Produce", 28, 40, 25, 1, 5, 3, "expiry"),
    ("FP02", "Onion 1kg", "Fresh Produce", 30, 42, 30, 2, 20, 4, ""),
    ("FP03", "Potato 1kg", "Fresh Produce", 28, 38, 26, 2, 20, 5, ""),
    ("FP04", "Banana (dozen)", "Fresh Produce", 40, 55, 14, 1, 4, 3, "expiry"),
    ("FP05", "Coriander Bunch", "Fresh Produce", 8, 15, 20, 1, 2, 2, "expiry"),
    ("FP06", "Spinach Bunch", "Fresh Produce", 10, 18, 12, 1, 2, 2, "expiry"),
    ("ST01", "Sona Masuri Rice 5kg", "Staples", 265, 310, 7, 3, None, 12, ""),
    ("ST02", "Atta 5kg", "Staples", 225, 262, 8, 3, None, 12, ""),
    ("ST03", "Toor Dal 1kg", "Staples", 142, 165, 9, 3, None, 4.5, ""),
    ("ST04", "Sunflower Oil 1L", "Staples", 128, 138, 14, 3, None, 2, "cost-up"),
    ("ST05", "Sugar 1kg", "Staples", 41, 47, 16, 3, None, 12, ""),
    ("ST06", "Salt 1kg", "Staples", 17, 22, 10, 3, None, 12, ""),
    ("ST07", "Tea Powder 250g", "Staples", 112, 130, 8, 3, None, 12, ""),
    ("SN01", "Potato Chips 52g", "Snacks", 16, 20, 25, 2, None, 12, ""),
    ("SN02", "Namkeen Mixture 200g", "Snacks", 38, 48, 10, 2, None, 12, ""),
    ("SN03", "Marie Biscuits", "Snacks", 22, 28, 18, 2, None, 12, ""),
    ("SN04", "Chocolate Bar", "Snacks", 36, 45, 12, 2, None, 12, ""),
    ("SN05", "Instant Noodles", "Snacks", 11.5, 14, 28, 2, None, 1.5, ""),
    ("SN06", "Imported Cookie Tin", "Snacks", 210, 320, 0.6, 5, None, 23, "dead"),
    ("BV01", "Cola 600ml", "Beverages", 33, 40, 20, 2, None, 12, "discount"),
    ("BV02", "Packaged Water 1L", "Beverages", 14, 20, 30, 2, None, 2.5, ""),
    ("BV03", "Fruit Juice 1L", "Beverages", 82, 105, 6, 2, None, 12, ""),
    ("BV04", "Energy Drink 250ml", "Beverages", 80, 105, 3, 3, None, 6, "dead"),
    ("PC01", "Bath Soap", "Personal Care", 31, 40, 14, 3, None, 12, "cost-up"),
    ("PC02", "Shampoo 180ml", "Personal Care", 98, 135, 5, 3, None, 12, ""),
    ("PC03", "Toothpaste 150g", "Personal Care", 72, 92, 9, 3, None, 12, ""),
    ("PC04", "Face Wash 100ml", "Personal Care", 118, 160, 3, 4, None, 7, "dead"),
    ("HH01", "Detergent Powder 1kg", "Household", 92, 118, 8, 3, None, 2.5, ""),
    ("HH02", "Dishwash Liquid 500ml", "Household", 78, 102, 6, 3, None, 12, ""),
    ("HH03", "Floor Cleaner 1L", "Household", 105, 139, 3, 3, None, 50, "overstock"),
    ("HH04", "Garbage Bags (30)", "Household", 42, 60, 4, 3, None, 65, "overstock"),
    ("HH05", "LED Bulb 9W", "Household", 58, 85, 0.5, 5, None, 80, "dead"),
]

BUNDLES = [
    ("BK01", "DA04", 0.40), ("SN01", "BV01", 0.40), ("ST03", "ST01", 0.30),
    ("DA01", "ST07", 0.30), ("SN05", "DA05", 0.25), ("PC03", "PC01", 0.25),
    ("FP01", "FP02", 0.45),
]
WEEKDAY_FACTOR = [0.92, 0.90, 0.92, 0.95, 1.12, 1.32, 1.28]
EXPIRY_DAYS = {"DA01": 2, "DA02": 1, "DA03": 2, "BK02": 1, "FP01": 3, "FP04": 2, "FP06": 1}
FIRST_NAMES = ["Anita", "Ravi", "Suresh", "Meena", "Kiran", "Lakshmi", "Arjun", "Divya", "Manoj", "Pooja", "Harish", "Sunita", "Naveen", "Deepa", "Prakash", "Revathi", "Vijay", "Shalini", "Ganesh", "Padma", "Rohit", "Kavya", "Sanjay", "Nandini", "Mahesh", "Latha", "Sandeep", "Bhavana", "Rajesh", "Swathi"]
LAST_NAMES = ["Reddy", "Gowda", "Nair", "Iyer", "Rao", "Shetty", "Naidu", "Kumar", "Hegde", "Patil", "Menon", "Prasad", "Murthy", "Bhat", "Singh", "Sharma", "Joshi", "Kulkarni", "Pillai", "Das"]


def _money(value):
    return round(float(value), 2)


def _product_records():
    records = []
    for row in PRODUCTS:
        sku, name, category, cost, price, demand, lead, shelf, cover, tag = row
        effective_cost = cost + (10 if tag == "cost-up" else 0)
        stock = max(1, round(demand * cover))
        if tag == "dead":
            stock = 14 if sku == "SN06" else (18 if sku == "BV04" else 22 if sku == "PC04" else 40)
        elif tag == "overstock":
            stock = round(demand * cover)
        elif sku in EXPIRY_DAYS:
            stock = max(1, round(demand * (1.3 if sku in ("DA01", "FP01", "DA03") else 1.8)))
        records.append({
            "sku": sku, "name": name, "category": category, "cost": float(effective_cost),
            "price": float(price), "demand": float(demand), "lead_days": lead,
            "shelf_life": shelf, "stock": stock, "tag": tag,
            "supplier": CATEGORY_SUPPLIER[category],
        })
    return records


def _build_history(products, today, seed=42):
    rng = random.Random(seed)
    start = today - timedelta(days=HISTORY_DAYS)
    daily = []
    sales_by_sku = Counter()
    category_totals = Counter()
    daily_hour = Counter()
    for offset in range(HISTORY_DAYS):
        day = start + timedelta(days=offset)
        total_sales = 0.0
        total_profit = 0.0
        units = 0
        bills = 0
        for item in products:
            trend = 1 + .0015 * offset
            weekday = WEEKDAY_FACTOR[day.weekday()]
            quantity = max(0, round(item["demand"] * weekday * trend * rng.uniform(.72, 1.24)))
            if item["tag"] == "dead" and offset < 50:
                quantity = 0
            if not quantity:
                continue
            paid = item["price"]
            if item["tag"] == "discount":
                paid *= rng.uniform(.85, .92)
            elif rng.random() < .02:
                paid *= .9
            revenue = quantity * paid
            profit = quantity * (paid - item["cost"])
            total_sales += revenue
            total_profit += profit
            units += quantity
            sales_by_sku[item["sku"]] += quantity
            category_totals[item["category"]] += revenue
            bills += max(1, round(quantity / max(1, item["demand"] / 5)))
        # Model bill count independently so average bill is a realistic basket size.
        bills = max(1, round(units / rng.uniform(5.2, 6.8)))
        hour = rng.choices(range(7, 23), weights=[3, 5, 6, 5, 4, 4, 4, 5, 7, 9, 11, 12, 10, 8, 5, 2])[0]
        daily_hour[hour] += bills
        daily.append({
            "date": day.isoformat(), "sales": round(total_sales, 2),
            "profit": round(total_profit, 2), "units": units, "bills": bills,
        })
    return daily, sales_by_sku, category_totals, daily_hour


def build_dashboard(days=7, today=None, seed=42):
    today = today or date.today()
    days = max(7, min(int(days), 90))
    products = _product_records()
    daily, sold_by_sku, category_totals, hourly = _build_history(products, today, seed)
    current = daily[-days:]
    previous = daily[-days * 2:-days]

    def totals(rows):
        revenue = sum(row["sales"] for row in rows)
        profit = sum(row["profit"] for row in rows)
        bills = sum(row["bills"] for row in rows)
        return {
            "revenue": round(revenue), "profit": round(profit), "bills": bills,
            "units": sum(row["units"] for row in rows),
            "average_bill": round(revenue / bills) if bills else 0,
            "margin": round(profit / revenue * 100, 1) if revenue else 0,
        }

    now = totals(current)
    before = totals(previous)
    kpis = []
    for key, label, unit in [
        ("revenue", "Sales", "inr"), ("profit", "Gross profit", "inr"),
        ("bills", "Bills", "num"), ("average_bill", "Average bill", "inr"),
    ]:
        prior = before[key]
        delta = round((now[key] - prior) / prior * 100, 1) if prior else None
        kpis.append({
            "id": key, "label": label, "value": now[key], "unit": unit,
            "delta": delta,
            "spark": [row["sales" if key == "revenue" else "profit" if key == "profit" else "bills" if key == "bills" else "sales"] for row in current],
            "sub": f"{now['margin']}% margin" if key == "profit" else "",
        })

    latest = daily[-30:]
    category_sales = Counter()
    item_sales = Counter()
    for item in products:
        units = round(sold_by_sku[item["sku"]] * days / HISTORY_DAYS)
        revenue = units * item["price"]
        category_sales[item["category"]] += revenue
        item_sales[item["sku"]] = revenue
    category_rows = [
        {"name": name, "sales": round(value), "share": round(value / max(1, sum(category_sales.values())) * 100, 1)}
        for name, value in category_sales.most_common()
    ]

    actions = []
    expiry_rows = []
    reorder_rows = []
    margin_rows = []
    dead_rows = []
    total_expiry_loss = 0
    total_reorder_cost = 0
    total_margin_leak = 0

    for item in products:
        units_14 = max(0, round(item["demand"] * 14 * .88))
        rate = units_14 / 14
        cover = item["stock"] / rate if rate else 999
        days_left = EXPIRY_DAYS.get(item["sku"])
        if days_left is not None:
            expiring_units = min(item["stock"], max(1, round(rate * (1.3 if item["sku"] in ("DA01", "FP01") else 2.4))))
            loss = round(expiring_units * item["cost"])
            total_expiry_loss += loss
            row = {
                "sku": item["sku"], "name": item["name"], "category": item["category"],
                "units": expiring_units, "days_left": days_left, "loss": loss,
                "supplier": item["supplier"],
            }
            expiry_rows.append(row)
            if days_left <= 2:
                actions.append({
                    "id": f"expiry-{item['sku']}", "type": "urgent", "icon": "◷",
                    "title": f"Move {item['name']} before it expires",
                    "detail": f"{expiring_units} units · expires in {days_left} day{'s' if days_left != 1 else ''}",
                    "value": loss, "value_label": "at risk", "action": "Plan a small markdown",
                    "href": "#expiry",
                })

        if cover < item["lead_days"] + 2 and item["tag"] != "dead":
            quantity = max(1, round(rate * 7 - item["stock"]))
            cost = round(quantity * item["cost"])
            total_reorder_cost += cost
            reorder_rows.append({
                "sku": item["sku"], "name": item["name"], "category": item["category"],
                "stock": item["stock"], "cover_days": round(cover, 1), "lead_days": item["lead_days"],
                "suggested_qty": quantity, "order_cost": cost, "supplier": item["supplier"],
            })
            if cover <= item["lead_days"] + 1:
                actions.append({
                    "id": f"stock-{item['sku']}", "type": "warning", "icon": "↘",
                    "title": f"Reorder {item['name']}",
                    "detail": f"{item['stock']} on hand · about {cover:.1f} days of stock",
                    "value": quantity, "value_label": "units to order",
                    "action": f"From {item['supplier']}", "href": "#reorder",
                })

        current_margin = max(0, (item["price"] - item["cost"]) / item["price"])
        target = CATEGORY_TARGET_MARGIN[item["category"]]
        if item["tag"] == "cost-up" or current_margin < target:
            gap = max(0, round((target - current_margin) * item["price"]))
            leak = max(gap * units_14, round(item["cost"] * .11 * units_14) if item["tag"] == "cost-up" else 0)
            total_margin_leak += leak
            margin_rows.append({
                "sku": item["sku"], "name": item["name"], "category": item["category"],
                "price": item["price"], "cost": item["cost"],
                "margin": round(current_margin * 100, 1), "target_margin": round(target * 100, 1),
                "suggested_price": round(item["cost"] / max(.01, 1 - target), 0),
                "weekly_leak": leak, "supplier": item["supplier"],
            })
            if item["tag"] == "cost-up" or current_margin < target - .025:
                actions.append({
                    "id": f"margin-{item['sku']}", "type": "insight", "icon": "₹",
                    "title": f"Review the price on {item['name']}",
                    "detail": f"{current_margin * 100:.1f}% margin · {target * 100:.0f}% category target",
                    "value": leak, "value_label": "weekly margin gap",
                    "action": f"Consider ₹{round(item['cost'] / max(.01, 1 - target)):.0f}", "href": "#margin",
                })

        if item["tag"] in ("dead", "overstock"):
            days_inactive = 50 if item["tag"] == "dead" else 0
            value = round(item["stock"] * item["cost"])
            dead_rows.append({
                "sku": item["sku"], "name": item["name"], "category": item["category"],
                "stock": item["stock"], "days_inactive": days_inactive,
                "cover_days": round(cover), "stock_value": value,
            })

    actions.sort(key=lambda row: {"urgent": 0, "warning": 1, "insight": 2}[row["type"]])
    total_at_risk = total_expiry_loss + total_margin_leak
    sales_total = totals(daily[-90:])["revenue"]
    peak_hour = max(hourly, key=hourly.get)
    winback_names = [
        f"{random.Random(seed + i).choice(FIRST_NAMES)} {random.Random(seed + i + 71).choice(LAST_NAMES)}"
        for i in range(6)
    ]
    return {
        "store": STORE,
        "today": today.isoformat(),
        "period_days": days,
        "kpis": kpis,
        "totals": now,
        "previous": before,
        "trend": latest,
        "categories": category_rows,
        "actions": actions[:10],
        "action_count": len(actions),
        "at_risk": total_at_risk,
        "expiry": sorted(expiry_rows, key=lambda row: row["days_left"]),
        "reorder": sorted(reorder_rows, key=lambda row: row["cover_days"]),
        "margin_alerts": sorted(margin_rows, key=lambda row: -row["weekly_leak"]),
        "dead_stock": dead_rows,
        "top_products": sorted([
            {"sku": item["sku"], "name": item["name"], "category": item["category"],
             "sales": round(item_sales[item["sku"]]), "units": round(sold_by_sku[item["sku"]] * days / HISTORY_DAYS)}
            for item in products
        ], key=lambda row: -row["sales"])[:6],
        "hourly": [{"hour": hour, "bills": hourly[hour]} for hour in sorted(hourly)],
        "peak_hour": peak_hour,
        "daily_target": round(sales_total / HISTORY_DAYS * 1.08),
        "inventory": products,
        "inventory_value": sum(item["stock"] * item["cost"] for item in products),
        "customers_lapsed": 16,
        "winback_names": winback_names,
        "bundle_ideas": [
            {"items": f"{next(p['name'] for p in products if p['sku'] == a)} + {next(p['name'] for p in products if p['sku'] == b)}",
             "lift": f"{int(prob * 100)}%"}
            for a, b, prob in BUNDLES[:4]
        ],
    }


def format_inr(amount):
    amount = int(round(amount))
    sign = "-" if amount < 0 else ""
    digits = str(abs(amount))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        digits = ",".join(parts) + "," + tail
    return f"{sign}₹{digits}"
