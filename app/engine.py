from __future__ import annotations

import os
import tempfile
from pathlib import Path

from app.config import OcrSettings, get_settings


class RapidOcrEngine:
    name = "rapidocr"

    def __init__(self, settings: OcrSettings | None = None):
        self.settings = settings or get_settings()
        self._engine = None

    def recognize_bytes(self, content: bytes, filename: str) -> str:
        suffix = Path(filename or "").suffix or ".png"
        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            return self.recognize_file(temp_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def recognize_file(self, file_path: str) -> str:
        engine = self._load()
        result, _ = engine(file_path)
        if not result:
            return ""
        return "\n".join(str(item[1]) for item in result if len(item) > 1 and item[1])

    def _load(self):
        if self._engine is None:
            if self.settings.engine != "rapidocr":
                raise ValueError(f"unsupported OCR_ENGINE: {self.settings.engine}")
            from rapidocr_onnxruntime import RapidOCR

            self._engine = RapidOCR()
        return self._engine
