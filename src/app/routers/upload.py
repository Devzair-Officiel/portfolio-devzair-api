import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.repositories.setting_repository import SettingRepository

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("/app/uploads")
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif", "image/svg+xml"}
MAX_SIZE = 2 * 1024 * 1024  # 2 MB


@router.post("/logo", dependencies=[Depends(get_current_user)])
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Format non supporté. PNG, JPEG, WEBP ou SVG uniquement.")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 2 Mo).")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "logo.png").suffix or ".png"
    filename = f"logo_{uuid.uuid4().hex[:8]}{ext}"
    dest = UPLOAD_DIR / filename
    dest.write_bytes(contents)

    url = f"/uploads/{filename}"
    repo = SettingRepository(session=db)
    await repo.upsert("logo_url", url)

    return {"url": url}
