"""Local-disk media fallback for dev environments without S3 configured."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Optional

_BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = Path(os.getenv("LOCAL_MEDIA_DIR") or (_BASE_DIR / "uploads"))


def _resolve(key: str) -> Path:
    path = (UPLOAD_DIR / key).resolve()
    if UPLOAD_DIR.resolve() not in path.parents and path != UPLOAD_DIR.resolve():
        raise ValueError("Invalid media key.")
    return path


def save_local_file(key: str, data: bytes) -> None:
    path = _resolve(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def read_local_file(key: str) -> Optional[bytes]:
    path = _resolve(key)
    if not path.is_file():
        return None
    return path.read_bytes()


def guess_content_type(key: str) -> str:
    return mimetypes.guess_type(key)[0] or "application/octet-stream"
