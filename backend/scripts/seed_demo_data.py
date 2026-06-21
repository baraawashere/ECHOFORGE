"""
THIS SCRIPT IS NOT OPTIONAL. Read the ECHOFORGE plan again — a live demo
cannot show "a pattern discovered over weeks" if the student just opened
the app. This script pre-loads a fake history of 3 mistakes, backdated,
so that when you submit ONE more (live, on camera) the system already
has something to connect it to.

Run this BEFORE you start recording:
    cd backend
    python scripts/seed_demo_data.py

Then, during the recording, submit the TRIGGER_ANSWER below through the
UI yourself — that's the moment the Cognitive Gap Map lights up live.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Let this script import from app/ even though it lives in scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.memory_store import reset_collection, store_answer  # noqa: E402
from app.models import Answer  # noqa: E402
from app.cluster_store import save_clusters  # noqa: E402

DEMO_STUDENT_ID = "demo_student_01"

now = datetime.now(timezone.utc)

# Three mistakes, different subjects, different surface wording — all
# secretly the SAME root cause, and each tagged with a REAL Common Core
# standard from curriculum_standards.py, not an invented label.
PRELOADED_MISTAKES = [
    Answer(
        student_id=DEMO_STUDENT_ID,
        concept_key="fractions_subtract_same_whole",
        question_text="A pizza is cut into 8 equal slices. You eat 3. What fraction of the pizza is left?",
        student_answer="3/8",
        correct_answer="5/8",
        is_correct=False,
        timestamp=now - timedelta(days=14),
    ),
    Answer(
        student_id=DEMO_STUDENT_ID,
        concept_key="percent_of_a_quantity",
        question_text="A class has 25 students. 15 passed the test. What percentage passed?",
        student_answer="15%",
        correct_answer="60%",
        is_correct=False,
        timestamp=now - timedelta(days=7),
    ),
    Answer(
        student_id=DEMO_STUDENT_ID,
        concept_key="unit_rate_constant_speed",
        question_text="A car travels 120 km in 3 hours. What is its average speed?",
        student_answer="120 km/h",
        correct_answer="40 km/h",
        is_correct=False,
        timestamp=now - timedelta(days=2),
    ),
]

# Submit THIS one live, through the UI, while recording. It should trigger
# the analysis and connect back to all three mistakes above.
TRIGGER_ANSWER = Answer(
    student_id=DEMO_STUDENT_ID,
    concept_key="uniform_probability_model",
    question_text="A bag has 4 red marbles and 6 blue marbles. What is the probability of picking red?",
    student_answer="4",
    correct_answer="4/10 (or 40%)",
    is_correct=False,
)


def main() -> None:
    print(f"Resetting collection and seeding history for {DEMO_STUDENT_ID}...")
    reset_collection()
    save_clusters({})  # wipe persisted connections too — otherwise old
    # discoveries from earlier testing survive a "clean slate" reset and
    # can point at mistakes that don't exist in the fresh data anymore.
    for mistake in PRELOADED_MISTAKES:
        store_answer(mistake)
        print(f"  stored: [{mistake.standard_code}] {mistake.question_text[:50]}...")

    print()
    print("Done. Do NOT submit TRIGGER_ANSWER now — save it for the live recording.")
    print("Trigger question to submit live during the demo:")
    print(f"  > {TRIGGER_ANSWER.question_text}")
    print(f"  > concept_key to select in the UI: {TRIGGER_ANSWER.concept_key}")
    print(f"  > student_id to use in the UI: {DEMO_STUDENT_ID}")


if __name__ == "__main__":
    main()
