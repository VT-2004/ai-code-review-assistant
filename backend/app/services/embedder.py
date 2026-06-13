import requests
import numpy as np
from app.core.config import HF_TOKEN

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

def get_model():
    return None  # no local model needed

def embed_texts(texts: list[str]) -> list[list[float]]:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": texts, "options": {"wait_for_model": True}}
    )
    response.raise_for_status()
    return response.json()

def embed_chunks(chunks: list[dict]) -> list[dict]:
    texts = [chunk["text"] for chunk in chunks]
    print(f"Embedding {len(texts)} chunks via HuggingFace API...")

    # batch in groups of 32 to avoid API limits
    batch_size = 32
    all_vectors = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        vectors = embed_texts(batch)
        all_vectors.extend(vectors)
        print(f"  embedded {min(i + batch_size, len(texts))}/{len(texts)}")

    for i, chunk in enumerate(chunks):
        chunk["embedding"] = all_vectors[i]

    print(f"Done. Vector dims: {len(all_vectors[0])}")
    return chunks