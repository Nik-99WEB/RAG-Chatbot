import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from app.core.hf_embeddings import get_hf_embeddings

# -------------------------------------------------
# Render-safe writable directories (/tmp)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(DB_PATH, exist_ok=True)


# -------------------------------------------------
# Hugging Face ONLINE embedding wrapper for Chroma
# -------------------------------------------------
class HFEmbeddingFunction:
    def embed_documents(self, texts):
        return get_hf_embeddings(texts).tolist()

    def embed_query(self, text):
        return get_hf_embeddings([text])[0].tolist()


# -------------------------------------------------
# Ingest documents into ChromaDB
# -------------------------------------------------
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

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=HFEmbeddingFunction(),
        persist_directory=DB_PATH
    )

    vectordb.persist()

    print(f"✅ Successfully ingested {len(chunks)} chunks into ChromaDB")
