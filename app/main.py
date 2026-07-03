from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import RapidOcrEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

app = FastAPI(title="Mehup OCR Service", version="1.0.0")


class OcrResponse(BaseModel):
    success: bool
    text: str
    engine: str
    filename: str


class TestOcrResponse(BaseModel):
    success: bool
    text: str
    engine: str
    source: str
    filename: str
    lineCount: int
    lines: List[str]


def _get_engine():
    engine = getattr(app.state, "ocr_engine", None)
    if engine is None:
        engine = RapidOcrEngine()
        app.state.ocr_engine = engine
    return engine


def _text_lines(text: str) -> List[str]:
    return [line for line in text.splitlines() if line.strip()]


def _test_ocr_response(text: str, engine_name: str, source: str, filename: str):
    lines = _text_lines(text)
    return {
        "success": True,
        "text": text,
        "engine": engine_name,
        "source": source,
        "filename": filename,
        "lineCount": len(lines),
        "lines": lines,
    }


def _recognize_bytes(engine, content: bytes, filename: str) -> str:
    try:
        return engine.recognize_bytes(content, filename)
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"OCR engine is not ready: {exc}") from exc


def _recognize_file(engine, file_path: str) -> str:
    try:
        return engine.recognize_file(file_path)
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"OCR engine is not ready: {exc}") from exc


@app.get("/health")
def health():
    engine = _get_engine()
    return {"status": "ok", "engine": engine.name}


@app.post("/ocr", response_model=OcrResponse)
async def ocr(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="file cannot be empty")

    engine = _get_engine()
    text = _recognize_bytes(engine, content, file.filename or "upload")
    return {
        "success": True,
        "text": text,
        "engine": engine.name,
        "filename": file.filename or "upload",
    }


@app.post("/test/ocr", response_model=TestOcrResponse)
async def test_ocr(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="file cannot be empty")

    filename = file.filename or "upload"
    engine = _get_engine()
    text = _recognize_bytes(engine, content, filename)
    return _test_ocr_response(text, engine.name, "upload", filename)


@app.get("/test/ocr", response_model=TestOcrResponse)
def test_ocr_get(filePath: str = Query(..., min_length=1)):
    path = Path(filePath)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"file not found: {filePath}")

    engine = _get_engine()
    text = _recognize_file(engine, str(path))
    return _test_ocr_response(text, engine.name, "filePath", path.name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("OCR_HOST", "0.0.0.0"),
        port=int(os.getenv("OCR_PORT", "8003")),
    )
