"""
Thin wrapper around Sentence-Transformers. The point of keeping this in its
own file: if you ever swap embedding models (or move to an API-based
embedding service), every other file just calls embed_text() and never
needs to know what's underneath.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    # Loaded once per process and cached — loading this model is slow,
    # you do NOT want it reloading on every request.
    return SentenceTransformer(settings.embedding_model_name)


def embed_text(text: str) -> list[float]:
    """Turn one string into a fixed-length vector."""
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Same as embed_text but for many strings at once — used by the seed script."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]
