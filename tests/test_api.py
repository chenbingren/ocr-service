import unittest

from fastapi.testclient import TestClient

from app.main import app


class FakeOcrEngine:
    name = "fake-ocr"

    def recognize_bytes(self, content, filename):
        self.last_content = content
        self.last_filename = filename
        return "识别文本"


class OcrApiTest(unittest.TestCase):
    def setUp(self):
        self.engine = FakeOcrEngine()
        app.state.ocr_engine = self.engine
        self.client = TestClient(app)

    def tearDown(self):
        if hasattr(app.state, "ocr_engine"):
            delattr(app.state, "ocr_engine")

    def test_ocr_endpoint_returns_text(self):
        response = self.client.post(
            "/ocr",
            files={"file": ("sample.png", b"fake image bytes", "image/png")},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["text"], "识别文本")
        self.assertEqual(payload["engine"], "fake-ocr")
        self.assertEqual(payload["filename"], "sample.png")
        self.assertEqual(self.engine.last_content, b"fake image bytes")

    def test_health_uses_injected_engine(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["engine"], "fake-ocr")


if __name__ == "__main__":
    unittest.main()
