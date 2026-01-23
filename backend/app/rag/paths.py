import os
import tempfile

# Render-safe writable directories
DATA_PATH = os.path.join(tempfile.gettempdir(), "data")
DB_PATH = os.path.join(tempfile.gettempdir(), "chroma_db")

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(DB_PATH, exist_ok=True)
