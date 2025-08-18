from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as Upload, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from starlette.responses import FileResponse
from app.api.deps import db, require_org_id, current_user  # auth-protected
from app.db.models.file import File as FileModel
from app.schemas.files import FileOut
from app.services.storage_service import save_local_file, open_local_file

router = APIRouter(prefix="/v1/files", tags=["files"])

@router.post("/upload", response_model=FileOut, dependencies=[Depends(current_user)])
async def upload_file(
    f: UploadFile = Upload(...),
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
):
    meta = save_local_file(str(org_id), f.filename or "upload.bin", f.content_type, f.file)
    rec = FileModel(
        org_id=org_id,
        storage=meta["storage"],
        path=meta["path"],
        content_type=meta["content_type"],
        size=meta["size"],
        sha256=meta["sha256"],
        scan_status="clean",   # in dev, mark clean immediately; later set "pending" + run scanner
    )
    session.add(rec); await session.commit(); await session.refresh(rec)
    return rec

@router.get("/{file_id}", response_model=FileOut, dependencies=[Depends(current_user)])
async def get_file_meta(file_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(FileModel, file_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="File not found")
    return row

@router.get("/{file_id}/download", dependencies=[Depends(current_user)])
async def download_file(file_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(FileModel, file_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="File not found")
    if row.storage != "local":
        raise HTTPException(status_code=501, detail="Only local storage is implemented in dev")
    abs_path = open_local_file(str(org_id), row.path)
    return FileResponse(abs_path, media_type=row.content_type or "application/octet-stream", filename=row.path.split("/")[-1])
