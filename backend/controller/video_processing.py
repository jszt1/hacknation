from datetime import datetime
import shutil
from io import StringIO
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import  StreamingResponse
from pathlib import Path
from backend.core.settings import Settings


router = APIRouter()
settings = Settings()

async def upload_video(file: UploadFile = File(...)) -> Path:
    out_name = str(datetime.now().timestamp())
    out_path = settings.UPLOAD_DIR / out_name

    with out_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    return out_path


@router.post("/data/process")
async def process_video(file: UploadFile = File(...)):
    _ = await upload_video(file)

    buffer = StringIO()
    buffer.write("")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="result.csv"'
        }
    )
