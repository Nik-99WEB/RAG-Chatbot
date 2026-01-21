import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

DATA_PATH = "data"
DB_PATH = "chroma_db"

def ingest_docs():
    documents = []

    for file in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, file)

        if file.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())

        elif file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    print("✅ Documents (TXT + PDF) ingested successfully")

if __name__ == "__main__":
    ingest_docs()
