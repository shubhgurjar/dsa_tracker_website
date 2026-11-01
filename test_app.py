import unittest
from fastapi.testclient import TestClient
from main import app
import json

class TestDSATracker(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_pages_render(self):
        # Multi-page check
        pages = ["/", "/dashboard", "/concepts", "/problems", "/revision", "/profile", "/login"]
        for p in pages:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Page {p} returned {res.status_code}")
            self.assertIn("<!DOCTYPE html>", res.text)

    def test_auth_flow(self):
        # Status check
        res = self.client.get("/api/auth/status")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["auth_enabled"])

        # Login with wrong PIN
        res_fail = self.client.post("/api/auth/login", json={"pin": "wrong_non_matching_pin_99999"})
        self.assertEqual(res_fail.status_code, 401)

        # Login with current configured PIN or session token check
        from backend.config import load_config, generate_session_token, verify_session_token
        token = generate_session_token()
        self.assertTrue(verify_session_token(token))

    def test_dashboard_stats(self):
        res = self.client.get("/api/stats/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("trip", data)
        self.assertIn("problems", data)
        self.assertIn("data_structures", data)
        self.assertIn("algorithms", data)
        self.assertIn("revisions", data)
        self.assertGreaterEqual(data["problems"]["total"], 1)

    def test_concepts_api(self):
        res = self.client.get("/api/concepts")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data["concepts"]), 20)
        
        # Test updating a concept
        first_concept_id = data["concepts"][0]["id"]
        update_res = self.client.put(f"/api/concepts/{first_concept_id}", json={
            "status": "In Progress",
            "confidence": 3,
            "key_notes": "Practiced two pointer patterns with array"
        })
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["status"], "In Progress")
        self.assertEqual(update_res.json()["confidence"], 3)

    def test_problems_crud_and_revision(self):
        # 1. Create problem
        create_res = self.client.post("/api/problems", json={
            "title": "Container With Most Water",
            "leetcode_number": 11,
            "difficulty": "Medium",
            "data_structure": "Arrays & Dynamic Arrays",
            "algorithm": "Two Pointers Technique",
            "pattern": "Two pointers inward scan",
            "time_complexity": "O(N)",
            "space_complexity": "O(1)",
            "approach_notes": "Start with maximum width. Move pointer with smaller height inward."
        })
        self.assertEqual(create_res.status_code, 200)
        prob_id = create_res.json()["id"]

        # 2. Verify days since revised is 0 (solved today)
        self.assertEqual(create_res.json()["days_since_revised"], 0)
        self.assertEqual(create_res.json()["urgency"], "fresh")

        # 3. Test mark revised
        rev_res = self.client.post(f"/api/problems/{prob_id}/revise")
        self.assertEqual(rev_res.status_code, 200)
        self.assertEqual(rev_res.json()["problem"]["revision_count"], 1)

        # 4. Toggle star
        star_res = self.client.post(f"/api/problems/{prob_id}/star")
        self.assertEqual(star_res.status_code, 200)
        self.assertEqual(star_res.json()["starred"], 1)

    def test_revision_queue(self):
        res = self.client.get("/api/revision/queue")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("counts", data)
        self.assertGreater(len(data["items"]), 0)

        # Verify items are sorted descending by days_since_revised
        days_list = [i["days_since_revised"] for i in data["items"]]
        self.assertEqual(days_list, sorted(days_list, reverse=True))

    def test_export_import(self):
        export_res = self.client.get("/api/export")
        self.assertEqual(export_res.status_code, 200)
        export_data = export_res.json()
        self.assertIn("problems", export_data)
        self.assertIn("concepts", export_data)
        self.assertIn("config", export_data)

if __name__ == "__main__":
    unittest.main()
