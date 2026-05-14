#!/usr/bin/env python3
"""
Recompresse les images projets existantes dans /app/uploads.
À exécuter une fois dans le conteneur API :
  docker compose -f docker-compose.prod.yml exec api python recompress_uploads.py
"""
import io
from pathlib import Path
from PIL import Image

UPLOAD_DIR = Path("/app/uploads")
MAX_DIM = 800       # px — les cartes s'affichent à 298x524px max
QUALITY = 78

def recompress(path: Path) -> None:
    original_size = path.stat().st_size
    data = path.read_bytes()

    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")

    w, h = img.size
    if max(w, h) > MAX_DIM:
        ratio = MAX_DIM / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=QUALITY, method=6)
    new_data = buf.getvalue()

    if len(new_data) < original_size:
        path.write_bytes(new_data)
        print(f"✓ {path.name}: {original_size//1024} KB → {len(new_data)//1024} KB")
    else:
        print(f"- {path.name}: déjà optimal ({original_size//1024} KB)")

if __name__ == "__main__":
    images = list(UPLOAD_DIR.glob("project_*.webp")) + list(UPLOAD_DIR.glob("project_*.png"))
    if not images:
        print("Aucune image projet trouvée.")
    for img_path in images:
        recompress(img_path)
