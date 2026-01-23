from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_hf_embeddings(texts):
    return _model.encode(texts, show_progress_bar=False)
