import os
from dotenv import load_dotenv
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

DB_PATH = "chroma_db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 🚨 Hard fail early if key is missing
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=GROQ_API_KEY)


def ask_question(query: str) -> str:
    # ✅ Prevent 502 when DB is missing
    if not os.path.exists(DB_PATH):
        return "⚠️ No documents uploaded yet. Please upload a PDF first."

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    docs = db.similarity_search(query, k=3)

    if not docs:
        return "⚠️ No relevant information found in the uploaded documents."

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
