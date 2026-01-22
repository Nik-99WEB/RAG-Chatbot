import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.rag.qa import ask_question
from app.rag.ingest import ingest_docs

app = FastAPI(title="RAG Chatbot API")

# =====================
# CORS (for frontend)
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for demo & dev
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
# Upload & Ingest PDF
# =====================
# Render-safe writable directory
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "data")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Prevent duplicate uploads
    if os.path.exists(file_path):
        return {
            "message": "PDF already exists, skipping upload",
            "filename": file.filename
        }

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ingest after upload
    ingest_docs()

    return {
        "message": "PDF uploaded and ingested successfully",
        "filename": file.filename
    }
