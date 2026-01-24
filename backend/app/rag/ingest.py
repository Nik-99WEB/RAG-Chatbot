import os
import psycopg2
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.hf_embeddings import get_hf_embeddings
from app.rag.paths import DATA_PATH

DATABASE_URL = os.getenv("DATABASE_URL")

def ingest_docs():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    documents = []

    for filename in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, filename)

        if filename.lower().endswith(".pdf"):
            documents.extend(PyPDFLoader(file_path).load())

        elif filename.lower().endswith(".txt"):
            documents.extend(TextLoader(file_path, encoding="utf-8").load())

    if not documents:
        print("⚠️ No documents found")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    # insert document record once
    cur.execute(
        "INSERT INTO documents (filename) VALUES (%s) ON CONFLICT DO NOTHING RETURNING id",
        (filename,)
    )
    doc_id = cur.fetchone()
    if not doc_id:
        cur.execute("SELECT id FROM documents WHERE filename=%s", (filename,))
        doc_id = cur.fetchone()

    doc_id = doc_id[0]

    texts = [c.page_content for c in chunks]
    embeddings = get_hf_embeddings(texts)

    for text, emb in zip(texts, embeddings):
        cur.execute(
            """
            INSERT INTO document_chunks (document_id, content, embedding)
            VALUES (%s, %s, %s)
            """,
            (doc_id, text, emb.tolist())
        )

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Ingested {len(chunks)} chunks into Supabase pgvector")
