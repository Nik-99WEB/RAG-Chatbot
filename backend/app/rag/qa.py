import os
import psycopg2
from dotenv import load_dotenv
from groq import Groq

from app.core.hf_embeddings import get_hf_embeddings

# -------------------------------------------------
# ENV SETUP
# -------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=GROQ_API_KEY)

# -------------------------------------------------
# Ask question using pgvector similarity search
# -------------------------------------------------
def ask_question(query: str) -> str:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Embed the query
    query_embedding = get_hf_embeddings([query])[0].tolist()

    # Vector similarity search (cosine distance)
    cur.execute(
        """
        SELECT content
        FROM document_chunks
        ORDER BY embedding <=> %s
        LIMIT 3;
        """,
        (query_embedding,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return "⚠️ No relevant information found in the uploaded documents."

    context = "\n\n".join(row[0] for row in rows)

    prompt = f"""
You are a helpful assistant.
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
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
