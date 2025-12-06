from pathlib import Path
from datetime import datetime
import shutil
from io import StringIO
from fastapi import APIRouter, UploadFile, File
from backend.services.csv import CsvService
from backend.controller.csv import get_csv_by_id
from backend.core.settings import Settings

settings = Settings()

async def upload_video(file: UploadFile = File(...)) -> id:
    out_name = str(datetime.now().timestamp())
    out_path = settings.UPLOAD_DIR / out_name

    with out_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    return out_path

async def _process_video(id):
    filename = f"{id}.csv"
    processed_path = CsvService.get_file_path(filename)
    buffer = StringIO()
    buffer.write("")
    buffer.seek(0)
    with processed_path.open("w") as f:
        f.write(buffer.read())
    return processed_path

async def process_video(file: UploadFile = File(...)):
    id = await upload_video(file)
    await _process_video(id)
    return id

