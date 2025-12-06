import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.csv import CsvService

router = APIRouter(prefix="/csv", tags=["CSV Retrieving CSVs"])


@router.get("/list")
async def list_csvs():
    files = CsvService.get_all_files()
    if not files:
        raise HTTPException(status_code=404, detail="No CSV files present on the host")
    return files

@router.get("/last")
async def get_last_csv():
    files = CsvService.get_all_files()
    if not files:
        raise HTTPException(status_code=404, detail="No CSV files present on the host")

    newest_file = files[-1]
    path = CsvService.get_file_path(newest_file)

    return FileResponse(path=path, filename=newest_file, media_type='text/csv')


@router.get("/{id}")
async def get_csv_by_id(id):
    clean_id = os.path.basename(id)
    filename = clean_id if clean_id.endswith('.csv') else f"{clean_id}.csv"

    path = CsvService.get_file_path(filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="CSV file not found")

    return FileResponse(path=path, filename=filename, media_type='text/csv')
