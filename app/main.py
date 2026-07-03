from __future__ import annotations

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.engine import RapidOcrEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

app = FastAPI(title="Mehup OCR Service", version="1.0.0")


class OcrResponse(BaseModel):
    success: bool
    text: str
    engine: str
    filename: str


def _get_engine():
    engine = getattr(app.state, "ocr_engine", None)
    if engine is None:
        engine = RapidOcrEngine()
        app.state.ocr_engine = engine
    return engine


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
    text = engine.recognize_bytes(content, file.filename or "upload")
    return {
        "success": True,
        "text": text,
        "engine": engine.name,
        "filename": file.filename or "upload",
    }
