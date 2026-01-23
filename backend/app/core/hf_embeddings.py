import os
import requests
import numpy as np

HF_API_URL = (
    "https://api-inference.huggingface.co/"
    "pipeline/feature-extraction/"
    "sentence-transformers/all-MiniLM-L6-v2"
)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}


def get_hf_embeddings(texts: list[str]) -> np.ndarray:
    response = requests.post(
        HF_API_URL,
        headers=headers,
        json={"inputs": texts}
    )
    response.raise_for_status()

    data = response.json()
    return np.mean(np.array(data), axis=1)
