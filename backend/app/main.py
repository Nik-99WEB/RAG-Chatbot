import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.rag.qa import ask_question
from app.rag.ingest import ingest_docs
from app.rag.paths import DATA_PATH
from fastapi import HTTPException
import traceback



app = FastAPI(title="RAG Chatbot API")

# =====================
# CORS (for frontend)
# =====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rag-chatbot-zdo3.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# =====================
# Models
# =====================
class QuestionRequest(BaseModel):
    question: str

# =====================
# Health check
# =====================
@app.get("/")
def root():
    return {"status": "RAG API running"}

# =====================
# Ask Question
# =====================
@app.post("/ask")
def ask(req: QuestionRequest):
    answer = ask_question(req.question)
    return {"answer": answer}

# =====================
# CORS Preflight for Upload
@app.options("/upload")
async def upload_options():
    return {}



# =====================
# Upload & Ingest PDF
# =====================
# Render-safe writable directory
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "data")
os.makedirs(UPLOAD_DIR, exist_ok=True)



@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(DATA_PATH, file.filename)

    if os.path.exists(file_path):
        return {"message": "PDF already exists", "filename": file.filename}

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename
    }

@app.post("/ingest")
def ingest_endpoint():
    try:
        ingest_docs()
        return {"message": "Documents ingested successfully"}
    except Exception as e:
        return {"error": str(e)}
