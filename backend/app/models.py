"""
Every shape of data that moves through ECHOFORGE is defined here once,
so the FastAPI routes, the memory store, and the root-cause engine all
agree on what an "Answer" or a "GapCluster" actually looks like.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class AnswerIn(BaseModel):
    """
    What the frontend sends when a student submits one answer.

    Notice there's no free-text "subject" or "sub_concept" field anymore.
    concept_key is a fixed key into curriculum_standards.CURRICULUM_STANDARDS —
    subject, the real standard code, and the official description all get
    looked up from there, not typed in by whoever fills out the form.
    """

    student_id: str
    concept_key: str
    question_text: str
    student_answer: str
    correct_answer: str
    is_correct: bool

    @field_validator("concept_key")
    @classmethod
    def concept_key_must_exist(cls, v: str) -> str:
        from app.curriculum_standards import CURRICULUM_STANDARDS

        if v not in CURRICULUM_STANDARDS:
            valid = ", ".join(CURRICULUM_STANDARDS.keys())
            raise ValueError(f"Unknown concept_key '{v}'. Must be one of: {valid}")
        return v


class Answer(AnswerIn):
    """The stored version — same as AnswerIn, plus an id and a timestamp."""

    answer_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def subject(self) -> str:
        from app.curriculum_standards import get_concept

        return get_concept(self.concept_key)["subject"]

    @property
    def standard_code(self) -> str:
        from app.curriculum_standards import get_concept

        return get_concept(self.concept_key)["standard_code"]

    @property
    def official_description(self) -> str:
        from app.curriculum_standards import get_concept

        return get_concept(self.concept_key)["official_description"]

    def embedding_text(self) -> str:
        """
        The single string we actually embed. Deliberately built from the
        REAL official standard description, not free text someone typed —
        that's what lets a math mistake and a physics mistake land near
        each other in vector space when they share a conceptual root,
        even though the surface wording is totally different, and it's
        why two people labeling the same mistake always produce the
        exact same embedding input.
        """
        return (
            f"Curriculum standard {self.standard_code}: {self.official_description} "
            f"Question: {self.question_text}. "
            f"Student answered: {self.student_answer}. "
            f"Correct answer: {self.correct_answer}."
        )


class RelatedMistake(BaseModel):
    """One neighbor returned from a ChromaDB similarity search."""

    answer_id: str
    student_id: str
    subject: str
    concept_key: str
    standard_code: str
    question_text: str
    timestamp: datetime
    distance: float  # lower = more similar


class GapCluster(BaseModel):
    """
    The output of root_cause_engine.py: a group of mistakes the AI believes
    share one underlying misunderstanding, plus its explanation.
    """

    student_id: str
    trigger_answer_id: str
    related_answer_ids: list[str]
    root_cause_summary: str
    explanation: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GapMapNode(BaseModel):
    answer_id: str
    subject: str
    concept_key: str
    standard_code: str
    question_text: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    timestamp: datetime


class GapMapEdge(BaseModel):
    """One edge in the dashboard graph — two mistakes linked by a shared root cause."""

    source_id: str
    target_id: str
    root_cause_summary: str


class GapMapResponse(BaseModel):
    """What GET /api/students/{id}/gap-map returns to draw the whole dashboard."""

    nodes: list[GapMapNode]
    edges: list[GapMapEdge]
