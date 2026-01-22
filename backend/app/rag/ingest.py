# type: ignore
import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ---- Paths ----
DATA_PATH = "data"
DB_PATH = "chroma_db"


def ingest_docs():
    """
    Ingest TXT and PDF files into Chroma vector DB.
    Safe for production (won't crash if no files exist).
    """

    # ✅ Safety: data folder must exist
    if not os.path.exists(DATA_PATH):
        print("⚠️ No data folder found. Skipping ingestion.")
        return

    files = os.listdir(DATA_PATH)
    if not files:
        print("⚠️ Data folder is empty. Nothing to ingest.")
        return

    documents = []

    for file in files:
        file_path = os.path.join(DATA_PATH, file)

        try:
            if file.lower().endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())

            elif file.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

        except Exception as e:
            print(f"❌ Failed to load {file}: {e}")

    # ✅ Safety: no documents loaded
    if not documents:
        print("⚠️ No valid documents found. Skipping vector DB creation.")
        return

    # ---- Split documents ----
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)

    if not chunks:
        print("⚠️ No chunks created. Skipping.")
        return

    # ---- Embeddings ----
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # ---- Create / Update Vector DB ----
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    print(f"✅ Ingested {len(chunks)} chunks into Chroma DB")


# Optional CLI test
if __name__ == "__main__":
    ingest_docs()
