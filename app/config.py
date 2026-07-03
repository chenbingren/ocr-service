import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OcrSettings:
    engine: str = os.getenv("OCR_ENGINE", "rapidocr")


def get_settings() -> OcrSettings:
    return OcrSettings()
