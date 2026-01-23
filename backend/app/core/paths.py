from app.rag.paths import DATA_PATH, DB_PATH

import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

DB_PATH = os.path.join(BASE_DIR, "chroma_db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
