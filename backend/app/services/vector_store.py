import chromadb
import requests
from chromadb.config import Settings
from app.core.config import HF_TOKEN

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

_client = None
_collection = None
COLLECTION_NAME = "code_chunks"

def get_client():
    global _client
    if _client is None:
        _client = chromadb.Client(Settings(anonymized_telemetry=False))
    return _client

def get_collection(reset: bool = False):
    global _collection
    client = get_client()

    if reset and _collection is not None:
        client.delete_collection(COLLECTION_NAME)
        _collection = None

    if _collection is None:
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    return _collection

def store_chunks(embedded_chunks: list[dict]):
    collection = get_collection(reset=True)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in embedded_chunks:
        ids.append(chunk["chunk_id"])
        embeddings.append(chunk["embedding"])
        documents.append(chunk["text"])
        metadatas.append({
            "file_path": chunk["file_path"],
            "language": chunk["language"],
            "index": chunk["index"]
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Stored {len(ids)} chunks in ChromaDB")
    return len(ids)

def embed_question(question: str) -> list[float]:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": [question], "options": {"wait_for_model": True}}
    )
    response.raise_for_status()
    return response.json()[0]

def query_similar(question: str, embedder=None, n_results: int = 5) -> list[dict]:
    collection = get_collection()
    question_vector = embed_question(question)

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "file_path": results["metadatas"][0][i]["file_path"],
            "language": results["metadatas"][0][i]["language"],
            "score": round(1 - results["distances"][0][i], 4)
        })

    return hits