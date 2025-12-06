from fastapi import APIRouter, UploadFile, File
from fastapi.responses import  StreamingResponse
from pathlib import Path

import backend.services.video_processing as video_processing_service

from backend.core.settings import Settings
from backend.controller.csv import get_csv_by_id 

router = APIRouter()


@router.post("/data/process")
async def process_video(file: UploadFile = File(...)):
    id = await video_processing_service.process_video(file)
    return await get_csv_by_id(id)


