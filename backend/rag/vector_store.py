import json
from pathlib import Path

import numpy as np
import faiss

from config import settings
from rag.embeddings import embed_texts, embed_query

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root
INDEX_PATH = BASE_DIR / settings.VECTOR_STORE_PATH.replace("./", "")
METADATA_PATH = BASE_DIR / settings.VECTOR_METADATA_PATH.replace("./", "")


def load_all_qa_from_processed() -> list[dict]:
    """Load every topic JSON from data/processed/ and combine into one list."""
    processed_dir = BASE_DIR / "data" / "processed"
    all_items = []
    for json_file in sorted(processed_dir.glob("*.json")):
        items = json.loads(json_file.read_text(encoding="utf-8"))
        all_items.extend(items)
    return all_items


def build_index():
    """Build the FAISS index from all Q&A pairs and save it to disk."""
    items = load_all_qa_from_processed()
    print(f"Loaded {len(items)} Q&A pairs")

    texts = [f"Q: {item['question']}\nA: {item['answer']}" for item in items]

    print("Embedding all texts (this may take a minute)...")
    embeddings = embed_texts(texts)
    embeddings = np.array(embeddings).astype("float32")

    faiss.normalize_L2(embeddings)  # for cosine similarity via inner product

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved FAISS index ({index.ntotal} vectors, dim={dim}) -> {INDEX_PATH}")


def load_index():
    """Load the FAISS index and metadata from disk."""
    index = faiss.read_index(str(INDEX_PATH))
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return index, metadata


def search(query: str, top_k: int = 5) -> list[dict]:
    """Search the index for the most relevant Q&A pairs to a query."""
    index, metadata = load_index()
    q_vec = embed_query(query).astype("float32").reshape(1, -1)
    faiss.normalize_L2(q_vec)

    scores, indices = index.search(q_vec, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        item = metadata[idx]
        results.append({"score": float(score), **item})
    return results


if __name__ == "__main__":
    build_index()
    print("\n--- Sample search test ---")
    for r in search("What is the difference between git merge and rebase?", top_k=3):
        print(f"[{r['score']:.3f}] ({r['topic']}) {r['question']}")