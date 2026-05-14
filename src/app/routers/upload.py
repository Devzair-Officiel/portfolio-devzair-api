import io
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.repositories.setting_repository import SettingRepository

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("/app/uploads")
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif", "image/svg+xml"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB avant compression
MAX_DIMENSION = 1200          # px max côté le plus long
WEBP_QUALITY = 82


def _compress_to_webp(data: bytes, max_dim: int = MAX_DIMENSION) -> bytes:
    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    # Redimensionne si trop grand
    w, h = img.size
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=WEBP_QUALITY, method=4)
    return buf.getvalue()


@router.post("/image", dependencies=[Depends(get_current_user)])
async def upload_image(
    file: UploadFile = File(...),
) -> dict[str, str]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Format non supporté. PNG, JPEG, WEBP ou SVG uniquement.")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo).")

    # SVG : pas de compression PIL
    if file.content_type == "image/svg+xml":
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"project_{uuid.uuid4().hex[:12]}.svg"
        (UPLOAD_DIR / filename).write_bytes(contents)
        return {"url": f"/uploads/{filename}"}

    compressed = _compress_to_webp(contents)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"project_{uuid.uuid4().hex[:12]}.webp"
    (UPLOAD_DIR / filename).write_bytes(compressed)

    return {"url": f"/uploads/{filename}"}


@router.post("/logo", dependencies=[Depends(get_current_user)])
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Format non supporté. PNG, JPEG, WEBP ou SVG uniquement.")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo).")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if file.content_type == "image/svg+xml":
        filename = f"logo_{uuid.uuid4().hex[:8]}.svg"
        (UPLOAD_DIR / filename).write_bytes(contents)
    else:
        compressed = _compress_to_webp(contents, max_dim=400)
        filename = f"logo_{uuid.uuid4().hex[:8]}.webp"
        (UPLOAD_DIR / filename).write_bytes(compressed)

    url = f"/uploads/{filename}"
    repo = SettingRepository(session=db)
    await repo.upsert("logo_url", url)

    return {"url": url}
