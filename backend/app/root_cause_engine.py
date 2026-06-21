"""
Once memory_store.py finds 2+ mistakes that look related, this file is
what actually explains WHY — by asking an LLM to read all of them
together and name the one misunderstanding that connects them.

streaming_root_cause_analysis() yields text chunks so main.py can push
them to the frontend over WebSocket as they're generated, instead of
making the student stare at a spinner.
"""
from collections.abc import AsyncIterator

import anthropic

from app.config import settings
from app.models import Answer, RelatedMistake

_SYSTEM_PROMPT = """You are ECHOFORGE, a diagnostic engine inside an AI tutoring system.
You will be shown one NEW mistake a student just made, plus one or more PAST mistakes
from the same student that were flagged as semantically related. Each mistake is tagged
with the REAL official curriculum standard it falls under (Common Core State Standards) —
use those standard descriptions as ground truth for what the student was actually supposed
to know, don't just guess from the question wording alone.

Your job: identify the single underlying misconception that explains ALL of these
mistakes, even though they may be filed under different subjects or different standards.
Be specific and concrete — never say something generic like "needs more practice". Name
the actual conceptual gap (e.g. "does not treat a percentage as a ratio out of 100", not
"struggles with math").

Respond in two parts, separated by a line containing only "---":
1. A one-sentence root cause summary (max 20 words).
2. A short explanation (2-4 sentences) a teacher or parent could read and immediately
   understand what to reteach.
"""


def _build_user_prompt(trigger: Answer, related: list[RelatedMistake]) -> str:
    lines = [
        "NEW MISTAKE:",
        f"- Curriculum standard: {trigger.standard_code}",
        f"- Standard says: {trigger.official_description}",
        f"- Question: {trigger.question_text}",
        f"- Student answered: {trigger.student_answer} (correct: {trigger.correct_answer})",
        "",
        "RELATED PAST MISTAKES (same student, flagged as semantically close):",
    ]
    for i, m in enumerate(related, start=1):
        lines.append(
            f"{i}. [{m.standard_code}] \"{m.question_text}\" "
            f"(similarity distance: {m.distance:.3f})"
        )
    lines.append("")
    lines.append("What is the one shared root cause?")
    return "\n".join(lines)


async def streaming_root_cause_analysis(
    trigger: Answer, related: list[RelatedMistake]
) -> AsyncIterator[str]:
    """Yields text chunks live as Claude writes the root-cause explanation."""
    if settings.use_provider != "anthropic":
        raise NotImplementedError(
            "Groq streaming path not wired up yet — add it here, mirroring the "
            "Anthropic branch below, using the groq Python client's streaming API."
        )

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    user_prompt = _build_user_prompt(trigger, related)

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def full_root_cause_analysis(trigger: Answer, related: list[RelatedMistake]) -> str:
    """Non-streaming version — convenient for the seed script and tests."""
    chunks = []
    async for chunk in streaming_root_cause_analysis(trigger, related):
        chunks.append(chunk)
    return "".join(chunks)
