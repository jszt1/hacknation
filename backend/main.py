
from fastapi import FastAPI
from controller import csv, video_processing

app = FastAPI(title="Video to CSV Processor API")
app.include_router(csv.router)
app.include_router(video_processing.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
