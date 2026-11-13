import unittest
from datetime import date

from app import app
from shop_data import CATEGORY_TARGET_MARGIN, HISTORY_DAYS, build_dashboard, format_inr


class ShopPilotAnalyticsTests(unittest.TestCase):
    def test_dashboard_contains_business_actions_and_inventory(self):
        data = build_dashboard(days=7, today=date(2025, 6, 1))
        self.assertEqual(data["store"]["name"], "Lakshmi Fresh Mart")
        self.assertGreaterEqual(len(data["inventory"]), 30)
        self.assertEqual(len(data["trend"]), 30)
        self.assertTrue(data["expiry"])
        self.assertTrue(data["reorder"])
        self.assertTrue(data["margin_alerts"])
        self.assertTrue(data["actions"])
        self.assertTrue(data["bundle_ideas"])

    def test_supported_periods_return_comparable_sales(self):
        week = build_dashboard(days=7, today=date(2025, 6, 1))
        month = build_dashboard(days=30, today=date(2025, 6, 1))
        quarter = build_dashboard(days=90, today=date(2025, 6, 1))
        self.assertGreater(month["totals"]["revenue"], week["totals"]["revenue"])
        self.assertGreater(quarter["totals"]["revenue"], month["totals"]["revenue"])

    def test_margin_targets_and_indian_currency_format(self):
        self.assertEqual(len(CATEGORY_TARGET_MARGIN), 8)
        self.assertEqual(format_inr(105348), "₹1,05,348")
        self.assertEqual(format_inr(-5000), "-₹5,000")


class ShopPilotRouteTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage_is_shop_pilot(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ShopPilot", response.data)
        self.assertIn(b"Lakshmi Fresh Mart", response.data)
        self.assertIn(b"Download today's sheet", response.data)

    def test_dashboard_api_and_period_validation(self):
        response = self.client.get("/api/dashboard?days=30")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["period_days"], 30)
        self.assertEqual(len(payload["kpis"]), 4)
        self.assertIn("margin_alerts", payload)
        self.assertNotIn("inventory", payload)
        self.assertEqual(self.client.get("/api/dashboard?days=12").status_code, 400)
        self.assertEqual(self.client.get("/api/dashboard?days=seven").status_code, 400)

    def test_inventory_search_and_category_filter(self):
        response = self.client.get("/api/inventory?q=milk&category=Dairy")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["products"])
        self.assertTrue(all("milk" in row["name"].lower() for row in payload["products"]))
        self.assertEqual(self.client.get("/api/inventory?category=Made%20Up").status_code, 400)

    def test_export_is_downloadable_csv_with_restock_data(self):
        response = self.client.get("/api/export?days=7")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=shoppilot-daily-action-sheet.csv", response.headers["Content-Disposition"])
        self.assertIn(b"REORDER SUGGESTIONS", response.data)
        self.assertIn(b"Fictional demo data", response.data)

    def test_health_endpoint(self):
        self.assertEqual(self.client.get("/health").get_json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
