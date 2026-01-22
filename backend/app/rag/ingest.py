import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# -------------------------------------------------
# Render-safe writable directories (/tmp)
# -------------------------------------------------
DATA_PATH = os.path.join(tempfile.gettempdir(), "data")
DB_PATH = os.path.join(tempfile.gettempdir(), "chroma_db")

# Ensure directories exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(DB_PATH, exist_ok=True)


def ingest_docs():
    documents = []

    for filename in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, filename)

        if filename.lower().endswith(".pdf"):
            documents.extend(PyPDFLoader(file_path).load())

        elif filename.lower().endswith(".txt"):
            documents.extend(TextLoader(file_path, encoding="utf-8").load())

    if not documents:
        print("⚠️ No documents found to ingest")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    vectordb.persist()

    print(f"✅ Successfully ingested {len(chunks)} chunks into ChromaDB")
