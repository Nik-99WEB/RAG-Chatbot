import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from app.core.hf_embeddings import get_hf_embeddings

from app.core.paths import DB_PATH, UPLOAD_DIR



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

    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)

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
