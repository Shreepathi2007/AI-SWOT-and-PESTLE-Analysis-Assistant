import tempfile
import unittest
from pathlib import Path

from app import create_app
from analysis import CATEGORIES, generate_analysis


class AnalysisAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(Path(self.temp_dir.name) / "test.sqlite3"),
            }
        )
        self.client = self.app.test_client()
        self.payload = {
            "name": "Green Basket",
            "industry": "Sustainable retail",
            "description": "An online shop with a small team and growing demand.",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_and_frontend(self):
        self.assertEqual(self.client.get("/api/health").json, {"status": "ok"})
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_analysis_returns_all_ten_categories(self):
        response = self.client.post("/api/analyze", json=self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json["analysis"]), set(CATEGORIES))
        self.assertTrue(all(response.json["analysis"][key] for key in CATEGORIES))

    def test_missing_and_oversized_fields_are_rejected(self):
        self.assertEqual(self.client.post("/api/analyze", json={}).status_code, 400)
        too_long = {**self.payload, "description": "x" * 3001}
        self.assertEqual(self.client.post("/api/analyze", json=too_long).status_code, 400)
        self.assertEqual(self.client.post("/api/analyze", data="bad").status_code, 400)

    def test_save_list_reopen_and_persist(self):
        analysis = generate_analysis(**self.payload)
        response = self.client.post(
            "/api/analyses", json={**self.payload, "analysis": analysis}
        )
        self.assertEqual(response.status_code, 201)
        record_id = response.json["id"]
        listed = self.client.get("/api/analyses")
        self.assertEqual(len(listed.json), 1)
        reopened = self.client.get(f"/api/analyses/{record_id}")
        self.assertEqual(reopened.status_code, 200)
        self.assertEqual(reopened.json["analysis"], analysis)
        restarted_app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(Path(self.temp_dir.name) / "test.sqlite3"),
            }
        )
        restarted_record = restarted_app.test_client().get(
            f"/api/analyses/{record_id}"
        )
        self.assertEqual(restarted_record.status_code, 200)
        self.assertEqual(restarted_record.json["name"], self.payload["name"])
        self.assertEqual(self.client.get("/api/analyses/9999").status_code, 404)

    def test_save_rejects_incomplete_analysis(self):
        response = self.client.post(
            "/api/analyses", json={**self.payload, "analysis": {"Strengths": ["one"]}}
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
