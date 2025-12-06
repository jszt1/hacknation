import os
from core.settings import settings


class CsvService:
    @staticmethod
    def get_all_files():
        files = [f for f in os.listdir(settings.PROCESSED_DIR) if f.endswith('.csv')]

        files.sort(key=lambda x: os.path.getctime(os.path.join(settings.PROCESSED_DIR, x)))
        return files

    @staticmethod
    def get_file_path(filename):
        return os.path.join(settings.PROCESSED_DIR, filename)
