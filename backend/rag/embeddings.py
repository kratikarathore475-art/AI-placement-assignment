from sentence_transformers import SentenceTransformer

from config import settings

_model = None


def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it (loading is slow, ~5-10 sec)."""
    global _model
    if _model is None:
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL} ...")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]):
    """Convert a list of texts into embedding vectors (numpy array)."""
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=True, batch_size=64)


def embed_query(query: str):
    """Convert a single query string into an embedding vector."""
    model = get_embedding_model()
    return model.encode([query])[0]
