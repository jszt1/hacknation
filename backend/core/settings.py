
import os

class Settings:
    UPLOAD_DIR = "uploads"
    PROCESSED_DIR = "csv"

    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.PROCESSED_DIR, exist_ok=True)

settings = Settings()