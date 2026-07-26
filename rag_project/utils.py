from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import DATA_DIR


def ensure_directory(path: Path | str) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text_file(path: str | os.PathLike[str]) -> str:
    path = Path(path)
    for encoding in ["utf-8-sig", "utf-8", "cp1256", "cp1252", "latin-1"]:
        try:
            with path.open("r", encoding=encoding) as handle:
                return handle.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", b"", 0, 1, "Unable to decode text file")


def write_json_file(path: str | os.PathLike[str], payload: Any) -> None:
    output_path = Path(path)
    ensure_directory(output_path.parent)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def read_json_file(path: str | os.PathLike[str]) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_path(path: str | os.PathLike[str]) -> str:
    return str(Path(path).resolve())


def compute_file_hash(path: str | os.PathLike[str]) -> str:
    hash_obj = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def is_empty_or_whitespace(text: str) -> bool:
    return not text or not text.strip()


def sanitize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not metadata:
        return {}
    return {key: value for key, value in metadata.items() if value is not None}


def iter_txt_files(directory: str | os.PathLike[str]) -> List[Path]:
    target_dir = Path(directory)
    if not target_dir.exists():
        return []
    return sorted(path for path in target_dir.rglob("*.txt") if path.is_file())


def load_documents_manifest() -> List[Dict[str, Any]]:
    manifest_path = DATA_DIR / "documents_manifest.json"
    if not manifest_path.exists():
        return []
    return read_json_file(manifest_path)


def save_documents_manifest(items: List[Dict[str, Any]]) -> None:
    write_json_file(DATA_DIR / "documents_manifest.json", items)
