from pathlib import Path
import os

class Settings:
    UPLOAD_DIR = Path("uploads")
    PROCESSED_DIR = Path("csv")

    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.PROCESSED_DIR, exist_ok=True)

settings = Settings()
