import unittest

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "healthy")

    def test_index(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_metrics_exposes_request_counter(self):
        self.client.get("/fast")
        body = self.client.get("/metrics").get_data(as_text=True)
        self.assertIn("app_http_requests_total", body)
        self.assertIn("app_http_request_duration_seconds", body)


if __name__ == "__main__":
    unittest.main()
