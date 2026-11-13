import tempfile
import unittest
from pathlib import Path

from app import app
from sales import filter_sales, load_sales, summarize


class SalesSummaryTests(unittest.TestCase):
    def setUp(self):
        self.rows = load_sales()

    def test_demo_dataset_is_complete_and_spans_2025(self):
        self.assertGreaterEqual(len(self.rows), 1000)
        self.assertEqual(min(row["date"].year for row in self.rows), 2025)
        self.assertEqual(max(row["date"].year for row in self.rows), 2025)

    def test_summary_kpis_match_underlying_rows(self):
        data = summarize(self.rows)
        self.assertEqual(data["kpis"]["orders"], len({row["order_id"] for row in self.rows}))
        self.assertAlmostEqual(data["kpis"]["sales"], sum(row["units"] * row["unit_price"] for row in self.rows), places=2)
        self.assertAlmostEqual(data["kpis"]["profit"], sum(row["units"] * (row["unit_price"] - row["unit_cost"]) for row in self.rows), places=2)
        self.assertLessEqual(len(data["products"]), 5)
        self.assertLessEqual(len(data["transactions"]), 8)

    def test_filters_combine(self):
        filtered = filter_sales(
            self.rows,
            start_date=self.rows[0]["date"].replace(month=6, day=1),
            end_date=self.rows[0]["date"].replace(month=8, day=31),
            region="West",
            category="Electronics",
        )
        self.assertTrue(all(row["region"] == "West" and row["category"] == "Electronics" for row in filtered))

    def test_invalid_csv_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.csv"
            path.write_text("wrong,columns\n1,2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing"):
                load_sales(path)


class DashboardRouteTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage_renders_dashboard_and_demo_label(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Retail, in focus", response.data)
        self.assertIn(b"LIVE DEMO", response.data)
        self.assertIn(b"fictional", response.data.lower())

    def test_dashboard_api_returns_expected_sections(self):
        response = self.client.get("/api/dashboard?region=West&category=Electronics")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(set(data["kpis"]), {"sales", "profit", "margin", "orders", "average_order", "units"})
        self.assertTrue(data["monthly"])
        self.assertTrue(data["transactions"])

    def test_dashboard_api_rejects_bad_filters(self):
        self.assertEqual(self.client.get("/api/dashboard?region=Moon").status_code, 400)
        self.assertEqual(self.client.get("/api/dashboard?start=not-a-date").status_code, 400)
        self.assertEqual(self.client.get("/api/dashboard?start=2025-11-01&end=2025-01-01").status_code, 400)
        self.assertEqual(self.client.get("/api/dashboard?start=2026-01-01").status_code, 404)

    def test_export_route_returns_filtered_downloadable_csv(self):
        response = self.client.get("/api/export?region=West")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=northstar-retail-summary.csv", response.headers["Content-Disposition"])
        self.assertTrue(response.data.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b"Top products", response.data)
        self.assertIn(b"Profit margin (%)", response.data)

    def test_export_route_reports_invalid_filters(self):
        response = self.client.get("/api/export?category=Unknown")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_health_route(self):
        self.assertEqual(self.client.get("/health").get_json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
