
from fastapi import FastAPI
from backend.controller import csv

app = FastAPI(title="Video to CSV Processor API")
app.include_router(csv.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)