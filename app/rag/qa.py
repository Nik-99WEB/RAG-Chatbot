import os
from dotenv import load_dotenv
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_PATH = "chroma_db"

def ask_question(query: str):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    docs = db.similarity_search(query, k=3)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    while True:
        q = input("Ask (type exit to quit): ")
        if q.lower() == "exit":
            break
        print("\nAnswer:", ask_question(q), "\n")
