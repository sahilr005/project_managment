from __future__ import annotations
from typing import BinaryIO
from app.core.config import settings
import os,hashlib,pathlib,uuid,shutil

BASE_DIR = pathlib.Path.cwd() / "var" / "uploads"
BASE_DIR.mkdir(parents=True,exist_ok=True)

def _safe_name(name:str) -> str:
    return "".join(c for c in name.replace("\\","/").split("/")[-1] if c.isalnum() or c in (" ",".","-","_"))[:100]

def save_local_file(org_id: str, file_name: str, content_type: str | None, stream: BinaryIO) -> dict:
    org_dir = BASE_DIR / org_id
    org_dir.mkdir(parents=True, exist_ok=True)
    
    fname = _safe_name(file_name) or "upload.bin" 
    obj_id = str(uuid.uuid4())

    ext = ""
    if "." in fname:
        ext = "."+ fname.rsplit(".",1)[-1]

    rel_path = f"{obj_id}{ext}"
    abs_path = org_dir / rel_path

    h = hashlib.sha256()
    size = 0 
    with open(abs_path,"wb") as out:
        while True:
            chunk = stream.read(1024*12024)
            if not chunk:
                break
            out.write(chunk)
            size += len(chunk)
            h.update(chunk)
    return {
        "storage": "local",
        "path": str(rel_path),
        "content_type": content_type or "application/octet-stream",
        "size":size,
        "sha256": h.hexdigest(),
    }

def open_local_file(org_id:str, rel_path: str)-> str:
    p = BASE_DIR / org_id / rel_path
    if not p.exists():
        raise FileNotFoundError
    return str(p)
