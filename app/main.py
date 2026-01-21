import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.rag.qa import ask_question
from app.rag.ingest import ingest_docs

app = FastAPI(title="RAG Chatbot API")

# ✅ CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "RAG API running"}

@app.post("/ask")
def ask(req: QuestionRequest):
    answer = ask_question(req.question)
    return {"answer": answer}

@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files allowed"}

    os.makedirs("data", exist_ok=True)
    save_path = os.path.join("data", file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest_docs()

    return {"message": "PDF uploaded and ingested successfully"}
