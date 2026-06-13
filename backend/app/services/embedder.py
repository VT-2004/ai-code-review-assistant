from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        # use a smaller, lighter model for production
        _model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        print("Model loaded.")
    return _model

def embed_chunks(chunks: list[dict]) -> list[dict]:
    model = get_model()
    texts = [chunk["text"] for chunk in chunks]

    print(f"Embedding {len(texts)} chunks...")
    vectors = model.encode(texts, show_progress_bar=False, batch_size=16)

    for i, chunk in enumerate(chunks):
        chunk["embedding"] = vectors[i].tolist()

    print(f"Done. Vector shape: {vectors[0].shape}")
    return chunks