import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


class FakeOcrEngine:
    name = "fake-ocr"

    def recognize_bytes(self, content, filename):
        self.last_content = content
        self.last_filename = filename
        return "ocr text\nline two"

    def recognize_file(self, file_path):
        self.last_file_path = file_path
        return "path ocr text"


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
        self.assertEqual(payload["text"], "ocr text\nline two")
        self.assertEqual(payload["engine"], "fake-ocr")
        self.assertEqual(payload["filename"], "sample.png")
        self.assertEqual(self.engine.last_content, b"fake image bytes")

    def test_test_ocr_endpoint_accepts_upload_and_returns_lines(self):
        response = self.client.post(
            "/test/ocr",
            files={"file": ("sample.png", b"fake image bytes", "image/png")},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["source"], "upload")
        self.assertEqual(payload["filename"], "sample.png")
        self.assertEqual(payload["text"], "ocr text\nline two")
        self.assertEqual(payload["lineCount"], 2)
        self.assertEqual(payload["lines"], ["ocr text", "line two"])

    def test_test_ocr_get_endpoint_accepts_local_file_path(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file.write(b"fake image bytes")
            file_path = temp_file.name

        try:
            response = self.client.get("/test/ocr", params={"filePath": file_path})
        finally:
            Path(file_path).unlink(missing_ok=True)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["source"], "filePath")
        self.assertEqual(payload["filename"], Path(file_path).name)
        self.assertEqual(payload["text"], "path ocr text")
        self.assertEqual(payload["lineCount"], 1)
        self.assertEqual(self.engine.last_file_path, file_path)

    def test_test_ocr_get_endpoint_returns_404_for_missing_file(self):
        response = self.client.get("/test/ocr", params={"filePath": "D:\\missing\\image.png"})

        self.assertEqual(response.status_code, 404)
        self.assertIn("file not found", response.json()["detail"])

    def test_health_uses_injected_engine(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["engine"], "fake-ocr")


if __name__ == "__main__":
    unittest.main()
