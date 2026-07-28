# -*- coding: utf-8 -*-
"""
خادم الواجهة الخلفية للتطبيق.
يخدم الواجهة الأمامية ويدير جميع عمليات RAG.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is in path for sibling imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import (
    CHROMA_DIR,
    DATA_DIR,
    DATA_FILE_CHUNKS,
    DATA_FILE_DOCUMENTS,
    DATA_FILE_PREPROCESSED,
    DOCUMENTS_DIR,
    LLM_MODEL,
    MIN_SIMILARITY,
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    TOP_K,
    get_openrouter_api_key,
)
from utils import read_json_file, read_text_file

# ── إنشاء التطبيق ─────────────────────────────────────────────────────────────

app = FastAPI(title="مساعد RAG عربي ذكي")

# ── المجلدات الأساسية ─────────────────────────────────────────────────────────

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ── تحميل الوحدات ─────────────────────────────────────────────────────────────

import importlib.util


def load_project_module(filename: str, module_name: str) -> Any:
    here = Path(__file__).resolve().parent
    path = here / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"تعذر العثور على وحدة الملف: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


document_module = load_project_module("01_documents.py", "document_module")
preprocess_module = load_project_module("02_preprocessing.py", "preprocess_module")
chunk_module = load_project_module("03_chunking.py", "chunk_module")
vector_module = load_project_module("04_vector_representation.py", "vector_module")
store_module = load_project_module("05_create_chroma_store.py", "store_module")
retrieve_module = load_project_module("06_retrieve_context.py", "retrieve_module")
prompt_module = load_project_module("07_prompting.py", "prompt_module")

run_store_creation = store_module.run_store_creation
retrieve_context = retrieve_module.retrieve_context
ask = prompt_module.ask
VectorStoreNotFoundError = retrieve_module.VectorStoreNotFoundError

# ── المسارات الثابتة ──────────────────────────────────────────────────────────

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ── الدوال المساعدة ──────────────────────────────────────────────────────────


def get_stats() -> Dict[str, int]:
    doc_count = 0
    chunk_count = 0
    if DATA_FILE_DOCUMENTS.exists():
        try:
            doc_count = len(read_json_file(DATA_FILE_DOCUMENTS))
        except Exception:
            doc_count = 0
    if DATA_FILE_CHUNKS.exists():
        try:
            chunk_count = len(read_json_file(DATA_FILE_CHUNKS))
        except Exception:
            chunk_count = 0
    return {"documents": doc_count, "chunks": chunk_count}


def rebuild_knowledge_base() -> Dict[str, int]:
    documents = document_module.load_documents_from_directory(DOCUMENTS_DIR)
    if not documents:
        raise ValueError("لم يتم العثور على مستندات نصية صالحة للمعالجة.")
    document_module.save_documents(documents)
    preprocess_module.run_preprocessing()
    chunk_module.run_chunking()
    vector_module.build_embeddings()
    run_store_creation()
    stats = get_stats()
    return {"documents": stats["documents"], "chunks": stats["chunks"]}


# ── المسارات ──────────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def serve_index() -> str:
    index_file = static_dir / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return HTMLResponse(
        content="<h1>مساعد RAG عربي ذكي</h1><p>الواجهة غير موجودة</p>",
        status_code=200,
    )


@app.get("/api/stats")
async def api_stats() -> JSONResponse:
    stats = get_stats()
    db_built = CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir())
    return JSONResponse({"documents": stats["documents"], "chunks": stats["chunks"], "db_built": db_built})


@app.get("/api/documents")
async def api_documents() -> JSONResponse:
    files = []
    for p in sorted(DOCUMENTS_DIR.glob("*.txt")):
        files.append({"name": p.name, "size": p.stat().st_size})
    return JSONResponse({"documents": files})


@app.post("/api/upload")
async def api_upload(files: List[UploadFile] = File(...)) -> JSONResponse:
    saved = []
    for f in files:
        if f.filename.lower().endswith(".txt"):
            target = DOCUMENTS_DIR / f.filename
            target.write_bytes(await f.read())
            saved.append(f.filename)
    return JSONResponse({"saved": saved, "count": len(saved)})


@app.post("/api/rebuild")
async def api_rebuild() -> JSONResponse:
    try:
        result = rebuild_knowledge_base()
        return JSONResponse({"success": True, **result})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chat")
async def api_chat(request: Dict[str, Any]) -> JSONResponse:
    query = request.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="الاستعلام فارغ")

    top_k = int(request.get("top_k", TOP_K))
    similarity = float(request.get("similarity", MIN_SIMILARITY))
    model = request.get("model", os.getenv("OPENROUTER_MODEL", LLM_MODEL))
    api_key = get_openrouter_api_key()

    if not api_key:
        return JSONResponse({"answer": "يرجى توفير مفتاح OpenRouter API.", "sources": []})

    try:
        contexts = retrieve_context(query, k=top_k, min_similarity=similarity)
    except VectorStoreNotFoundError as exc:
        return JSONResponse({"answer": str(exc), "sources": []})

    from memory import ConversationMemory

    memory = ConversationMemory()
    memory.add_turn("user", query)

    try:
        result = ask(query, contexts, memory, api_key=api_key, model=model)
        answer = result.get("answer", "تعذر توليد إجابة.")
        sources = result.get("sources", [])
        memory.add_turn("assistant", answer)
        return JSONResponse({"answer": answer, "sources": sources})
    except Exception as exc:
        return JSONResponse({"answer": f"حدث خطأ: {exc}", "sources": []})


@app.post("/api/clear")
async def api_clear() -> JSONResponse:
    return JSONResponse({"success": True, "message": "تم مسح المحادثة"})


# ── التشغيل ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
