"""
This is the actual "memory" in ECHOFORGE. NEXUS could classify a single
mistake. This file is what lets the system remember every mistake a
student has ever made and search across all of them.

Read query_related_mistakes() carefully — that function is the entire
innovation of this project in code form.
"""
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.embedding_service import embed_text
from app.models import Answer, RelatedMistake

_COLLECTION_NAME = "student_answers"

_client = chromadb.PersistentClient(
    path=settings.chroma_persist_dir,
    settings=ChromaSettings(anonymized_telemetry=False),
)
_collection = _client.get_or_create_collection(
    name=_COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


def store_answer(answer: Answer) -> None:
    """Embed one answer and persist it, tagged with the real standard, not free text."""
    vector = embed_text(answer.embedding_text())
    _collection.add(
        ids=[answer.answer_id],
        embeddings=[vector],
        metadatas=[
            {
                "student_id": answer.student_id,
                "subject": answer.subject,
                "concept_key": answer.concept_key,
                "standard_code": answer.standard_code,
                "question_text": answer.question_text,
                "is_correct": answer.is_correct,
                "timestamp": answer.timestamp.isoformat(),
                "question_text": answer.question_text,
                "student_answer": answer.student_answer,
                "correct_answer": answer.correct_answer,
                "is_correct": answer.is_correct,
            }
        ],
        documents=[answer.embedding_text()],
    )


def query_related_mistakes(
    answer: Answer,
    top_k: int | None = None,
) -> list[RelatedMistake]:
    """
    Given a NEW wrong answer, search ALL of this student's past wrong
    answers (any subject, any time) for ones that are semantically close.

    This is what no other tutoring tool does: a fractions mistake last
    week and a percentage mistake today never get compared to each other
    anywhere else. Here, they do, automatically, every single time.
    """
    if not answer.is_correct:
        vector = embed_text(answer.embedding_text())
    else:
        # We don't pattern-match on correct answers — only mistakes matter.
        return []

    k = top_k or settings.neighbor_search_k

    results = _collection.query(
        query_embeddings=[vector],
        n_results=k + 1,  # +1 because the answer itself may already be stored
        where={
            "$and": [
                {"student_id": {"$eq": answer.student_id}},
                {"is_correct": {"$eq": False}},
            ]
        },
    )

    related: list[RelatedMistake] = []
    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc_id, meta, distance in zip(ids, metadatas, distances):
        if doc_id == answer.answer_id:
            continue
        if distance > (1 - settings.similarity_threshold):
            # Chroma returns cosine DISTANCE (0 = identical). We store a
            # similarity threshold for readability, so we invert it here.
            continue
        related.append(
            RelatedMistake(
                answer_id=doc_id,
                student_id=meta["student_id"],
                subject=meta["subject"],
                concept_key=meta["concept_key"],
                standard_code=meta["standard_code"],
                question_text=meta["question_text"],
                timestamp=datetime.fromisoformat(meta["timestamp"]),
                distance=distance,
            )
        )

    return related


def get_student_history(student_id: str) -> list[dict]:
    """All stored answers for one student, used to build the full gap map."""
    results = _collection.get(where={"student_id": {"$eq": student_id}})
    history = []
    for doc_id, meta in zip(results["ids"], results["metadatas"]):
        history.append({"answer_id": doc_id, **meta})
    return history


def reset_collection() -> None:
    """Wipes all stored data. Useful between demo rehearsals — NOT for production."""
    global _collection
    _client.delete_collection(_COLLECTION_NAME)
    _collection = _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
